# The game engine: it consumes typed commands and returns the text the player
# reads.  No UI knowledge lives here, so the whole game can be exercised from
# a headless test.
#
# Movement follows `playermove()` in codigo_fuente_open_adventure/main.c:
# the first travel rule of the room whose motion matches the verb wins, and a
# failing condition walks forward to the next rule with a different
# destination, which is how "enter grate" turns into "the grate is locked".
class_name Interpreter
extends RefCounted

const MAX_RULE_WALK := 64

var world: WorldData
var state: GameState
var parser: CommandParser
var rng := RandomNumberGenerator.new()

## Rooms visited during this session, in order, for the map view.
var visit_log: PackedStringArray = PackedStringArray()


func _init(world_data: WorldData) -> void:
	world = world_data
	parser = CommandParser.new(world_data)
	state = GameState.new()
	state.reset(world)
	rng.seed = 20251020


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

func submit(line: String) -> Array[String]:
	var output: Array[String] = []
	if state.finished:
		return output
	if state.travel_outcome in [GameState.TravelOutcome.DEATH_PENDING, GameState.TravelOutcome.DEPENDENCY_PENDING, GameState.TravelOutcome.CYCLE_ERROR]:
		return output
	# misc.c:get_command_input rejects empty/overlong input before counting.
	var input_words := line.strip_edges().replace("\t", " ").split(" ", false)
	if input_words.is_empty():
		return output
	if input_words.size() > 2:
		return [world.message("TWO_WORDS")]
	state.turn += 1
	state.travel_outcome = GameState.TravelOutcome.IDLE
	state.travel_dependency = ""
	state.pending_location = state.current_location

	var command := parser.parse(line)
	# Interface commands that are not part of the source vocabulary.
	if command.verb_stem == "LICEN" or command.verb_stem == "ABOUT":
		return _do_licenses()
	if command.verb_stem == "MAP":
		return [world.ui("map_hint")]

	if command.kind == Command.Kind.UNKNOWN:
		output.append(world.message("CANT_APPLY"))
		return output

	if command.is_motion():
		output.append_array(_handle_motion(command))
		return output

	if command.is_action():
		output.append_array(_handle_action(command))
		return output

	return output


# ---------------------------------------------------------------------------
# motions
# ---------------------------------------------------------------------------

func _handle_motion(command: Command) -> Array[String]:
	match command.motion:
		"LOOK":
			return _describe_current(true)
		"BACK":
			return _go_back()
		"CAVE":
			return _cave_hint()
		_:
			pass

	_advance_history()
	var result := _try_move(command.motion)
	if result["handled"]:
		return result["lines"]

	# A word that is both a motion and an action may still make sense as an
	# action ("CONTINUE" is a travel motion but also means "go").
	if parser.has_action_fallback(command):
		return _handle_action(command)

	return _movement_failure(command)


func _movement_failure(command: Command) -> Array[String]:
	state.travel_outcome = GameState.TravelOutcome.REJECTED
	var compass := [
		"EAST", "WEST", "NORTH", "SOUTH",
		"NE", "NW", "SE", "SW", "UP", "DOWN",
	]
	if command.motion in compass:
		return [world.message("BAD_DIRECTION")]
	if command.motion in ["FORWARD", "LEFT", "RIGHT"]:
		return [world.message("UNSURE_FACING")]
	if command.motion in ["OUTSIDE", "INSIDE"]:
		return [world.message("NO_INOUT_HERE")]
	if command.motion in ["XYZZY", "PLUGH"]:
		return [world.message("NOTHING_HAPPENS")]
	return [world.message("CANT_APPLY")]


func _try_move(motion: String) -> Dictionary:
	var result := {"handled": false, "moved": false, "spoke": false, "lines": [] as Array[String]}
	var disconnected: Array[String] = [world.message("NOT_CONNECTED")]
	var loc := world.location(state.current_location)
	if loc == null:
		result["handled"] = true
		result["lines"] = disconnected
		return result
	var rule := _select_rule(loc, motion)
	if rule == null:
		if state.travel_outcome in [GameState.TravelOutcome.DEPENDENCY_PENDING, GameState.TravelOutcome.CYCLE_ERROR]:
			result["handled"] = true
			result["lines"] = disconnected
		return result
	return _execute_move(rule)


func _execute_move(rule: TravelRule) -> Dictionary:
	var result := {"handled": true, "moved": false, "spoke": false, "lines": [] as Array[String]}
	var lines: Array[String] = []
	result["lines"] = lines
	var candidate := rule
	for step in range(MAX_RULE_WALK):
		var loc := world.location(state.current_location)
		if candidate.action_type == TravelRule.ActionType.SPECIAL:
			match candidate.special_id:
				1:
					# main.c: Plover passage permits no load or only emerald.
					var carried := state.carried_objects()
					if carried.size() > 1 or (carried.size() == 1 and carried[0] != "EMERALD"):
						state.travel_outcome = GameState.TravelOutcome.SPOKE
						lines.append(world.message("MUST_DROP"))
						result["spoke"] = true
						return result
					var passage := TravelRule.new()
					passage.target = "LOC_ALCOVE" if state.current_location == "LOC_PLOVER" else "LOC_PLOVER"
					candidate = passage
				2:
					if not world.objects.has("EMERALD") or not state.object_place.has("EMERALD"):
						_pending_dependency("special_2: global EMERALD state")
						return result
					if loc == null or not loc.travel.has(candidate):
						_travel_error("special_2 without source alternative")
						return result
					state.object_place["EMERALD"] = state.current_location
					candidate = _select_from(loc, _next_distinct(loc, loc.travel.find(candidate)))
					if candidate == null:
						return result
					continue
				3:
					# Requires original two-place/fixed objects and croak().
					# No invented bridge result or partial mutation.
					_pending_dependency("special_3: global TROLL/TROLL2/CHASM/BEAR placements and death")
					return result
				_:
					_travel_error("unknown special travel")
					return result
		if candidate.action_type == TravelRule.ActionType.SPEAK:
			state.pending_location = state.current_location
			state.travel_outcome = GameState.TravelOutcome.SPOKE
			result["spoke"] = true
			lines.append(world.message(candidate.target))
			return result
		state.pending_location = candidate.target
		if candidate.target == "LOC_NOWHERE" and loc != null and loc.is_forced():
			# do_move() would call croak. Keep last entered location and
			# oldloc/oldlc2/newloc for CUT D; no reincarnation or score change.
			state.travel_outcome = GameState.TravelOutcome.DEATH_PENDING
			return result
		if not world.is_in_chapter(candidate.target):
			state.travel_outcome = GameState.TravelOutcome.FRONTIER
			if candidate.target.begins_with("LOC_FOOF"):
				lines.append(world.message("MAGIC_FOOF"))
			lines.append(world.ui("frontier"))
			return result
		result["moved"] = result["moved"] or candidate.target != state.current_location
		state.move_to(candidate.target, false)
		lines.append_array(_describe_current(false))
		loc = world.location(state.current_location)
		if not loc.is_forced():
			state.travel_outcome = GameState.TravelOutcome.ARRIVED
			return result
		# do_command describes forced room, calls playermove(HERE), then
		# next do_move. No new input or turn between these steps.
		_advance_history()
		candidate = _select_rule(loc, "HERE")
		if candidate == null:
			if state.travel_outcome != GameState.TravelOutcome.DEPENDENCY_PENDING:
				_travel_error("FORCED location has no eligible HERE destination")
			return result
	_travel_error("travel cycle exceeded %d dispatches" % MAX_RULE_WALK)
	return result


func _advance_history() -> void:
	state.previous_previous_location = state.previous_location
	state.previous_location = state.current_location


func _pending_dependency(reason: String) -> void:
	state.travel_outcome = GameState.TravelOutcome.DEPENDENCY_PENDING
	state.travel_dependency = reason
	state.pending_location = state.current_location


func _travel_error(reason: String) -> void:
	state.travel_outcome = GameState.TravelOutcome.CYCLE_ERROR
	state.travel_dependency = reason


func _select_rule(loc: WorldLocation, verb: String) -> TravelRule:
	for index in range(loc.travel.size()):
		if loc.travel[index].matches_verb(verb):
			return _select_from(loc, index)
	return null


func _next_distinct(loc: WorldLocation, index: int) -> int:
	var probe := index + 1
	while probe < loc.travel.size() and loc.travel[index].is_equivalent_to(loc.travel[probe]):
		probe += 1
	return probe


func _select_from(loc: WorldLocation, index: int) -> TravelRule:
	while index < loc.travel.size():
		var candidate := loc.travel[index]
		if candidate.cond_object != "" and not world.objects.has(candidate.cond_object):
			_pending_dependency("travel condition requires object " + candidate.cond_object)
			return null
		if _condition_holds(candidate):
			return candidate
		if state.travel_outcome == GameState.TravelOutcome.CYCLE_ERROR:
			return null
		index = _next_distinct(loc, index)
	_travel_error("conditional travel has no distinct alternative")
	return null


func _condition_holds(rule: TravelRule) -> bool:
	match rule.cond_type:
		"always":
			return true
		"not_state":
			return state.state_of(rule.cond_object) != rule.cond_state
		"carry":
			return state.is_carried(rule.cond_object)
		"with":
			return state.is_here(rule.cond_object) or state.is_carried(rule.cond_object)
		"pct":
			return rng.randf() * 100.0 < float(rule.cond_percent)
		"no_dwarves":
			# Historical player condition is PCT(100); actors exclude this row.
			return rng.randf() * 100.0 < 100.0
		_:
			_travel_error("unknown travel condition " + rule.cond_type)
			return false


func _go_back() -> Array[String]:
	var loc := world.location(state.current_location)
	var target := state.previous_location
	var previous := world.location(target)
	if previous != null and previous.is_forced():
		target = state.previous_previous_location
	_advance_history()
	if loc != null and loc.forbids_back():
		state.travel_outcome = GameState.TravelOutcome.REJECTED
		return [world.message("TWIST_TURN")]
	if target == state.current_location:
		state.travel_outcome = GameState.TravelOutcome.REJECTED
		return [world.message("FORGOT_PATH")]
	var fallback: TravelRule = null
	if loc != null:
		for rule in loc.travel:
			if rule.action_type != TravelRule.ActionType.GOTO:
				continue
			if rule.target == target:
				return _try_move(_rule_motion(rule))["lines"]
			var via := world.location(rule.target)
			if via != null and via.is_forced() and via.travel[0].target == target:
				fallback = rule
	if fallback != null:
		return _try_move(_rule_motion(fallback))["lines"]
	state.travel_outcome = GameState.TravelOutcome.REJECTED
	return [world.message("NOT_CONNECTED")]


func _rule_motion(rule: TravelRule) -> String:
	if rule.is_here():
		return "HERE"
	# BACK selects an expanded C motion, so aliases must re-enter rule
	# selection by normalized motion identity rather than one raw spelling.
	return rule.motion_names[0] if not rule.motion_names.is_empty() else rule.verbs[0]


func _cave_hint() -> Array[String]:
	var loc := world.location(state.current_location)
	if loc != null and loc.is_above_ground() and state.current_location != "LOC_GRATE":
		return [world.message("FOLLOW_STREAM")]
	return [world.message("NEED_DETAIL")]


# ---------------------------------------------------------------------------
# actions
# ---------------------------------------------------------------------------

func _handle_action(command: Command) -> Array[String]:
	match command.action:
		"CARRY":
			return _do_carry(command)
		"DROP":
			return _do_drop(command)
		"INVENTORY":
			return _do_inventory()
		"UNLOCK":
			return _do_lock(command, true)
		"LOCK":
			return _do_lock(command, false)
		"LIGHT":
			return _do_lamp(command, true)
		"EXTINGUISH":
			return _do_lamp(command, false)
		"DRINK":
			return _do_drink()
		"FILL":
			return _do_fill()
		"POUR":
			return _do_pour()
		"EAT", "ATTACK", "WAKE":
			return [world.message("EAT_THAT")]
		"LISTEN":
			return _do_listen()
		"TREE":
			return [world.message("TREE")]
		"SCORE":
			return _do_score()
		"HELP", "INFO":
			return _do_help()
		"QUIT":
			return _do_quit()
		"SAY":
			return _do_say(command)
		"NOTHING":
			return [world.message("NOTHING_HAPPENS")]
		_:
			var fallback := world.action_message(command.action)
			if fallback.is_empty():
				fallback = world.message("CANT_APPLY")
			return [fallback]


func _do_carry(command: Command) -> Array[String]:
	if not command.has_noun():
		return [world.message("TAKE_WHAT")]
	var obj := _resolve_object(command.noun_stem)
	if obj == null:
		return [world.message("NO_SUCH_THING").replace("{noun}", command.noun_text.to_lower())]
	if state.is_carried(obj.id):
		return [world.message("ALREADY_CARRYING")]
	if not state.is_here(obj.id):
		return [world.message("NO_SUCH_THING").replace("{noun}", command.noun_text.to_lower())]
	if obj.immovable:
		return [world.message("IMMOVABLE")]

	state.object_place[obj.id] = GameState.CARRIED
	var label := _object_label(obj)
	var lines: Array[String] = [world.message("TAKEN").replace("{object}", label)]
	if obj.treasure:
		state.treasures_taken += 1
	return lines


func _do_drop(command: Command) -> Array[String]:
	if not command.has_noun():
		return [world.message("DROP_WHAT")]
	var obj := _resolve_object(command.noun_stem)
	if obj == null or not state.is_carried(obj.id):
		return [world.message("NOT_CARRYING")]
	state.object_place[obj.id] = state.current_location
	return [world.message("DROPPED").replace("{object}", _object_label(obj))]


func _do_inventory() -> Array[String]:
	var carried := state.carried_objects()
	if carried.is_empty():
		return [world.message("INVENTORY_EMPTY")]
	var lines: Array[String] = [world.message("INVENTORY_HEADER")]
	for object_id in carried:
		var obj := world.world_object(object_id)
		if obj == null:
			continue
		lines.append("  - " + _object_label(obj))
	return lines


func _do_lock(command: Command, unlocking: bool) -> Array[String]:
	if not command.has_noun():
		return [world.message("NOTHING_LOCKED")]
	var obj := _resolve_object(command.noun_stem)
	if obj == null:
		return [world.message("NOTHING_LOCKED")]

	if obj.id == "GRATE":
		# The source rule: the grate only opens for whoever holds the keys.
		if not state.is_carried("KEYS") and not state.is_here("KEYS"):
			return [world.message("NO_KEYS")]
		var target_state := "GRATE_OPEN" if unlocking else "GRATE_CLOSED"
		state.set_state("GRATE", target_state)
		return [world.object_change_message(obj, target_state)]

	return [world.action_message("UNLOCK" if unlocking else "LOCK")]


func _do_lamp(command: Command, lighting: bool) -> Array[String]:
	var obj := _resolve_object(command.noun_stem) if command.has_noun() else null
	if obj == null or obj.id != "LAMP":
		return [world.action_message("LIGHT" if lighting else "EXTINGUISH")]
	if not state.is_carried("LAMP"):
		return [world.message("NO_SUCH_THING").replace("{noun}", "lámpara")]
	var target_state := "LAMP_BRIGHT" if lighting else "LAMP_DARK"
	state.set_state("LAMP", target_state)
	return [world.object_change_message(obj, target_state)]


func _do_drink() -> Array[String]:
	var loc := world.location(state.current_location)
	if loc != null and loc.has_water():
		return [world.message("DRINK_STREAM")]
	return [world.action_message("DRINK")]


func _do_fill() -> Array[String]:
	var loc := world.location(state.current_location)
	if state.is_carried("BOTTLE") and loc != null and loc.has_water():
		var bottle := world.world_object("BOTTLE")
		state.set_state("BOTTLE", "WATER_BOTTLE")
		return [world.object_change_message(bottle, "WATER_BOTTLE")]
	return [world.message("FILL_THAT")]


func _do_pour() -> Array[String]:
	if state.is_carried("BOTTLE") and state.state_of("BOTTLE") == "WATER_BOTTLE":
		var bottle := world.world_object("BOTTLE")
		state.set_state("BOTTLE", "EMPTY_BOTTLE")
		var lines: Array[String] = [world.object_change_message(bottle, "EMPTY_BOTTLE")]
		lines.append(world.message("POUR_GROUND"))
		return lines
	return [world.message("FILL_THAT")]


func _do_listen() -> Array[String]:
	var loc := world.location(state.current_location)
	if loc != null and loc.sound != "":
		var sound_text := world.message(loc.sound)
		if not sound_text.is_empty():
			return [sound_text]
	return [world.message("ALL_SILENT")]


func _do_say(command: Command) -> Array[String]:
	var spoken := command.noun_text.to_upper()
	if spoken == "XYZZY" or spoken == "PLUGH":
		var magic := Command.new()
		magic.kind = Command.Kind.MOTION
		magic.verb_stem = spoken.substr(0, 5)
		magic.motion = spoken
		return _handle_motion(magic)
	return [world.message("NOTHING_HAPPENS")]


func _do_score() -> Array[String]:
	var score := _score()
	var class_message := _class_for(score)
	var lines: Array[String] = [
		world.ui("score_line").replace("{score}", str(score)).replace("{class}", class_message)
	]
	lines.append(world.ui("turn_line").replace("{turn}", str(state.turn)))
	return lines


func _do_help() -> Array[String]:
	var lines: Array[String] = []
	for line in world.ui_lines("help"):
		lines.append(line)
	var footer := world.ui("help_footer")
	if not footer.is_empty():
		lines.append(footer)
	return lines


## HELP carries the short licence notice; LICENSES prints the project and
## third-party notices.
func _do_licenses() -> Array[String]:
	var lines: Array[String] = []
	for line in world.ui_lines("license_notice"):
		lines.append(line)
	return lines


func _do_quit() -> Array[String]:
	state.finished = true
	return [world.ui("quit_line")]


# ---------------------------------------------------------------------------
# scoring (mirrors score.c)
# ---------------------------------------------------------------------------

func _score() -> int:
	var points := 0
	for object_id in world.objects.keys():
		var obj: WorldObject = world.objects[object_id]
		if not obj.treasure:
			continue
		# The treasure value follows score.c: 12 for the treasures before the
		# chest, 14 for the chest itself, 16 for the ones after it.
		var k := 12
		if obj.id == "CHEST":
			k = 14
		elif obj.source_index > world.chest_index:
			k = 16
		if state.is_carried(obj.id) or state.is_here(obj.id):
			points += 2
		if state.is_here(obj.id) and state.current_location == "LOC_BUILDING":
			points += k - 2
	# Surviving: (NDEATHS - deaths) * 10, with no deaths possible in chapter 01.
	points += world.num_deaths * 10
	points += 2
	return points


func _class_for(score: int) -> String:
	for entry in world.classes:
		var threshold := int(entry.get("threshold", 0))
		if threshold < score:
			continue
		var message := String(entry.get("message", ""))
		if message.is_empty():
			continue
		var key := "CLASS_%d" % threshold
		if world.l10n_messages.has(key):
			return String(world.l10n_messages[key])
		return message
	return world.message("OFF_SCALE")


# ---------------------------------------------------------------------------
# descriptions
# ---------------------------------------------------------------------------

func _describe_current(force_long: bool) -> Array[String]:
	var lines: Array[String] = []
	var location_id := state.current_location
	var first_visit := not state.has_visited(location_id)
	state.visited[location_id] = true
	visit_log.append(location_id)

	var description := ""
	if force_long or first_visit:
		description = world.describe(location_id)
	else:
		description = world.describe_short(location_id)
		if description.is_empty():
			description = world.describe(location_id)
	if not description.is_empty():
		lines.append(description)

	for object_id in state.objects_here():
		var obj := world.world_object(object_id)
		if obj == null:
			continue
		lines.append(world.object_description_for_state(obj, state.state_of(object_id)))
	return lines


func _object_label(obj: WorldObject) -> String:
	var entry: Dictionary = world.l10n_objects.get(obj.id, {})
	if entry.has("inventory"):
		return String(entry["inventory"])
	return obj.inventory_label


func _resolve_object(stem: String) -> WorldObject:
	if stem.is_empty():
		return null
	var best: WorldObject = null
	for object_id in world.objects.keys():
		var obj: WorldObject = world.objects[object_id]
		for word in obj.words:
			if String(word).to_upper() == stem:
				if state.is_carried(obj.id):
					return obj
				if best == null:
					best = obj
	return best
