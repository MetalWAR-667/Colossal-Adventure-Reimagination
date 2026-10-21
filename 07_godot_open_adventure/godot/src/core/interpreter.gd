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

	var result := _try_move(command.motion)
	if result["handled"]:
		return result["lines"]

	# A word that is both a motion and an action may still make sense as an
	# action ("CONTINUE" is a travel motion but also means "go").
	if parser.has_action_fallback(command):
		return _handle_action(command)

	return _movement_failure(command)


func _movement_failure(command: Command) -> Array[String]:
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
	var loc := world.location(state.current_location)
	if loc == null:
		result["handled"] = true
		result["lines"] = [world.message("NOT_CONNECTED")]
		return result

	var rule := _select_rule(loc, motion)
	if rule == null:
		return result

	result["handled"] = true
	if rule.action_type == TravelRule.ActionType.SPEAK:
		result["spoke"] = true
		var lines: Array[String] = []
		lines.append(world.message(rule.target))
		result["lines"] = lines
		return result

	return _execute_move(rule)


func _execute_move(rule: TravelRule) -> Dictionary:
	var result := {"handled": true, "moved": false, "spoke": false, "lines": [] as Array[String]}
	var lines: Array[String] = []

	if not world.is_in_chapter(rule.target):
		# The rule leaves the chapter: the chapter is a closed slice, so the
		# move is refused and the boundary is announced.
		if rule.target.begins_with("LOC_FOOF"):
			lines.append(world.message("MAGIC_FOOF"))
		lines.append(world.ui("frontier"))
		result["lines"] = lines
		return result

	state.move_to(rule.target)
	state.turn += 1
	result["moved"] = true
	lines.append_array(_describe_current(false))
	result["lines"] = lines
	return result


func _select_rule(loc: WorldLocation, verb: String) -> TravelRule:
	var rules := loc.travel
	var index := 0
	while index < rules.size():
		var rule := rules[index]
		if rule.matches_verb(verb):
			var cursor := index
			var guard := 0
			while guard < MAX_RULE_WALK:
				guard += 1
				var candidate := rules[cursor]
				if _condition_holds(candidate):
					return candidate
				# Conditional failure: walk to the next rule with a
				# different condition and destination, as `playermove()` does.
				var probe := cursor + 1
				while probe < rules.size() and candidate.is_equivalent_to(rules[probe]):
					probe += 1
				if probe >= rules.size():
					return null
				cursor = probe
		index += 1
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
			return true
		_:
			return true


func _go_back() -> Array[String]:
	var loc := world.location(state.current_location)
	if loc != null and loc.forbids_back():
		return [world.message("TWIST_TURN")]
	if state.previous_location == "" or state.previous_location == state.current_location:
		return [world.message("FORGOT_PATH")]
	if not world.is_in_chapter(state.previous_location):
		return [world.ui("frontier")]

	state.move_to(state.previous_location)
	state.turn += 1
	return _describe_current(false)


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
