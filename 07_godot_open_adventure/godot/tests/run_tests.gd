# Headless test suite for the chapter 01 engine.
#
# Run with:
#   Godot_v4.7.x-stable_win64_console.exe --headless --path godot --script res://tests/run_tests.gd
extends SceneTree

var _failures: PackedStringArray = PackedStringArray()
var _checks: int = 0


func _initialize() -> void:
	var world := WorldData.load_default()
	_test_dataset(world)
	_test_connectivity(world)
	_test_parser(world)
	_test_movement(world)
	_test_grate_and_keys(world)
	_test_magic_words(world)
	_test_sewer(world)
	_test_objects(world)
	_test_score(world)
	_test_art(world)
	_test_map_view(world)
	await _test_debug_interface()

	if _failures.is_empty():
		print("PASS: %d checks" % _checks)
		quit(0)
	else:
		for failure in _failures:
			printerr("FAIL: %s" % failure)
		printerr("FAILED: %d of %d checks" % [_failures.size(), _checks])
		quit(1)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

func _check(condition: bool, label: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(label)


func _equal(actual: Variant, expected: Variant, label: String) -> void:
	_checks += 1
	if actual != expected:
		_failures.append("%s (got %s, expected %s)" % [label, str(actual), str(expected)])


func _contains(haystack: Array, needle: String, label: String) -> void:
	_checks += 1
	var found := false
	for item in haystack:
		if String(item).contains(needle):
			found = true
			break
	if not found:
		_failures.append("%s (%s not in %s)" % [label, needle, str(haystack)])


func _play(interpreter: Interpreter, lines: Array[String]) -> Array[String]:
	var output: Array[String] = []
	for line in lines:
		output.append_array(interpreter.submit(line))
	return output


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

func _test_dataset(world: WorldData) -> void:
	_equal(world.chapter_id, "CH_SURFACE", "chapter id")
	_equal(world.locations.size(), 42, "chapter location count")
	_equal(world.objects.size(), 8, "chapter object count")
	_equal(world.map_nodes.size(), 34, "map node count")
	_check(world.map_edges.size() > 100, "map edges present")
	_equal(world.num_deaths, 3, "NDEATHS from the source")
	_check(world.classes.size() >= 10, "score classes exported")
	_equal(world.chest_index, 55, "chest index from the source object order")
	var sapphire := world.world_object("SAPPH")
	_check(sapphire != null, "the sapphire of the ledge is part of the chapter")
	if sapphire != null:
		_equal(sapphire.source_index, 68, "sapphire source index")
		_check(sapphire.source_index > world.chest_index, "the sapphire scores as a late treasure")

	# Every travel target must exist in the chapter or be declared as frontier.
	for location_id in world.locations.keys():
		var loc: WorldLocation = world.locations[location_id]
		for rule in loc.travel:
			if rule.action_type != TravelRule.ActionType.GOTO:
				continue
			_check(
				world.is_in_chapter(rule.target) or world.frontier.has(rule.target) or world.has_structural_location(rule.target),
				"travel target %s of %s is known" % [rule.target, location_id]
			)

	# The grate rule pair must survive the export in source order.
	var grate: WorldLocation = world.location("LOC_GRATE")
	_check(grate != null, "LOC_GRATE present")
	if grate != null:
		var speak_index := -1
		for index in grate.travel.size():
			if grate.travel[index].action_type == TravelRule.ActionType.SPEAK:
				speak_index = index
		_check(speak_index >= 0, "LOC_GRATE has the locked-grate fallback")


func _test_connectivity(world: WorldData) -> void:
	var seen := {"LOC_START": true}
	var queue := PackedStringArray(["LOC_START"])
	while not queue.is_empty():
		var current := queue[0]
		queue.remove_at(0)
		var loc: WorldLocation = world.location(current)
		if loc == null:
			continue
		for rule in loc.travel:
			if rule.action_type != TravelRule.ActionType.GOTO:
				continue
			if not world.is_in_chapter(rule.target) or seen.has(rule.target):
				continue
			seen[rule.target] = true
			queue.append(rule.target)
	_equal(seen.size(), world.locations.size() - 2, "chapter rooms reachable from LOC_START")
	# The source gives no inbound rule for these three inside chapter 01:
	# the two magic-word pseudo rooms live in other chapters, and the ledge
	# is only reachable from the reservoir side of the cave.
	for orphan in ["LOC_FOOF4", "LOC_LEDGE"]:
		_check(not seen.has(orphan), "%s is not reachable inside the chapter" % orphan)


func _test_parser(world: WorldData) -> void:
	var parser := CommandParser.new(world)
	_equal(parser.stem("downstream"), "DOWNS", "five letter stem of downstream")
	_equal(parser.stem("inwards"), "INWAR", "five letter stem of inwards")
	_equal(parser.stem("n"), "N", "single letter stem")

	var north := parser.parse("n")
	_equal(north.motion, "NORTH", "N is the north motion")
	var take := parser.parse("take lamp")
	_equal(take.action, "CARRY", "TAKE maps to CARRY")
	_equal(take.noun_stem, "LAMP", "noun stem of TAKE LAMP")
	var magic := parser.parse("xyzzy")
	_equal(magic.motion, "XYZZY", "XYZZY is a motion")
	_equal(parser.parse("ayuda").kind, Command.Kind.UNKNOWN, "AYUDA is not advertised as a parser alias")
	var specifically_handled := {
		"CARRY": true,
		"DROP": true,
		"INVENTORY": true,
		"UNLOCK": true,
		"LOCK": true,
		"LIGHT": true,
		"EXTINGUISH": true,
		"DRINK": true,
		"FILL": true,
		"POUR": true,
		"EAT": true,
		"ATTACK": true,
		"WAKE": true,
		"LISTEN": true,
		"TREE": true,
		"SCORE": true,
		"HELP": true,
		"INFO": true,
		"QUIT": true,
		"SAY": true,
		"NOTHING": true,
	}
	var checked_actions: Dictionary = {}
	for action in world.action_verbs.values():
		var action_name := String(action)
		if (
			checked_actions.has(action_name)
			or specifically_handled.has(action_name)
			or not world.action_messages.has(action_name)
		):
			continue
		checked_actions[action_name] = true
		_check(
			world.l10n_messages.has(action_name),
			"recognized action %s has a Spanish fallback" % action_name
		)


func _test_movement(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)
	_equal(interpreter.state.current_location, "LOC_START", "start location")

	_play(interpreter, ["S"])
	_equal(interpreter.state.current_location, "LOC_VALLEY", "south of the road is the valley")

	_play(interpreter, ["N"])
	_equal(interpreter.state.current_location, "LOC_START", "north returns to the road")

	_play(interpreter, ["E"])
	_equal(interpreter.state.current_location, "LOC_BUILDING", "east enters the building")

	_play(interpreter, ["OUT"])
	_equal(interpreter.state.current_location, "LOC_START", "out leaves the building")

	_play(interpreter, ["W"])
	_equal(interpreter.state.current_location, "LOC_HILL", "west climbs the hill")

	_play(interpreter, ["N"])
	_equal(interpreter.state.current_location, "LOC_FOREST20", "north of the hill is the forest")

	# A direction with no rule must not move the player.
	var output := _play(interpreter, ["UP"])
	_contains(output, "Por ahí no se puede ir", "an impossible direction is refused")
	_equal(interpreter.state.current_location, "LOC_FOREST20", "the player did not move")
	output = _play(interpreter, ["LEFT"])
	_contains(output, "puntos cardinales", "relative movement failure is localized")


func _test_grate_and_keys(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)

	# The depression is one of the exits of the road: "depression" is the
	# motion verb of the source.
	_play(interpreter, ["DEPRESSION"])
	_equal(interpreter.state.current_location, "LOC_GRATE", "reached the grate")

	var output := _play(interpreter, ["ENTER"])
	_contains(output, "reja", "the locked grate refuses entry")

	# Unlocking without keys fails.
	output = _play(interpreter, ["UNLOCK GRATE"])
	_contains(output, "llaves", "the grate needs the keys")

	# Fetch the keys in the building and come back.
	_play(interpreter, ["BUILD", "E"])
	_equal(interpreter.state.current_location, "LOC_BUILDING", "back inside the building")
	output = _play(interpreter, ["TAKE KEYS"])
	_contains(output, "Cogido", "the keys can be taken")
	_check(interpreter.state.is_carried("KEYS"), "the keys are carried")

	_play(interpreter, ["OUT", "DEPRESSION"])
	_equal(interpreter.state.current_location, "LOC_GRATE", "back at the grate with the keys")

	output = _play(interpreter, ["UNLOCK GRATE"])
	_contains(output, "reja", "the grate unlocks")
	_equal(interpreter.state.state_of("GRATE"), "GRATE_OPEN", "grate state is open")

	output = _play(interpreter, ["ENTER"])
	_equal(interpreter.state.current_location, "LOC_BELOWGRATE", "entering the open grate moves to LOC_BELOWGRATE")
	output = _play(interpreter, ["WEST"])
	_equal(interpreter.state.current_location, "LOC_COBBLE", "moving west from LOC_BELOWGRATE enters LOC_COBBLE")
	output = _play(interpreter, ["EAST"])
	_equal(interpreter.state.current_location, "LOC_BELOWGRATE", "returning east moves back to LOC_BELOWGRATE")
	output = _play(interpreter, ["OUT"])
	_equal(interpreter.state.current_location, "LOC_GRATE", "leaving LOC_BELOWGRATE returns to LOC_GRATE")


func _test_magic_words(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)
	_play(interpreter, ["E"])
	_equal(interpreter.state.current_location, "LOC_BUILDING", "inside the building")
	var output := _play(interpreter, ["XYZZY"])
	_contains(output, ">>Foof!<<", "the magic word triggers foof transition")
	_equal(interpreter.state.current_location, "LOC_DEBRIS", "XYZZY teleports to LOC_DEBRIS via LOC_FOOF1")
	output = _play(interpreter, ["XYZZY"])
	_contains(output, "Puf", "return XYZZY triggers foof transition")
	_equal(interpreter.state.current_location, "LOC_BUILDING", "XYZZY teleports back to LOC_BUILDING via LOC_FOOF2")


func _test_sewer(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)
	_play(interpreter, ["E"])
	var output := _play(interpreter, ["DOWNSTREAM"])
	_equal(interpreter.state.current_location, "LOC_BUILDING", "sewer HERE returns automatically to the building")
	output = _play(interpreter, ["N"])
	_equal(interpreter.state.current_location, "LOC_BUILDING", "the sewer only leads back")


func _test_objects(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)
	var output := _play(interpreter, ["TAKE SAPPHIRE"])
	_contains(output, "No ves ninguna", "an absent object cannot be taken")

	_play(interpreter, ["E"])
	output = _play(interpreter, ["TAKE LAMP"])
	_contains(output, "Cogido", "the lamp can be taken")
	_check(interpreter.state.is_carried("LAMP"), "the lamp is carried")
	output = _play(interpreter, ["DROP LAMP"])
	_contains(output, "Soltado", "the lamp can be dropped")
	_check(interpreter.state.is_here("LAMP"), "the lamp is on the floor again")

	# The grate is immovable, and it lives by the depression.
	_play(interpreter, ["OUT", "DEPRESSION"])
	_equal(interpreter.state.current_location, "LOC_GRATE", "at the grate again")
	output = _play(interpreter, ["TAKE GRATE"])
	_contains(output, "no se mueve", "the grate cannot be carried")


func _test_score(world: WorldData) -> void:
	var interpreter := Interpreter.new(world)
	# The score is reported with its class.
	var output := _play(interpreter, ["SCORE"])
	_contains(output, "Puntuación", "the score is reported")
	_contains(output, "principiante", "the class is reported")

	# The interface shows the project and third-party legal notices.
	output = _play(interpreter, ["LICENSES"])
	_contains(output, "General Public License", "the licence notice is available")
	_contains(output, "Open Adventure", "the notice credits the source")
	_contains(output, "MetalWAR", "the notice names the author")
	output = _play(interpreter, ["HELP"])
	_contains(output, "GPL", "the help carries the licence line")
	_contains(output, "LICENSES", "the help advertises the implemented licence command")
	_check(not "\n".join(output).contains("AYUDA"), "the help does not advertise an unsupported alias")

	# Survival (3 deaths) plus the rounding points, before any treasure.
	_equal(interpreter._score(), 32, "score without treasure")


func _test_art(world: WorldData) -> void:
	_check(world.art.has("scenes"), "the art pack is loaded")
	var scenes: Dictionary = world.art.get("scenes", {})
	_check(scenes.has("LOC_START"), "the start room has an illustration")
	_check(scenes.has("LOC_FOREST"), "the forest has a shared illustration")
	var meta: Dictionary = world.art.get("meta", {})
	var palette: Dictionary = meta.get("palette", {})
	_check(palette.size() > 5, "the art palette is present")
	var illustration := RoomIllustration.from_dict(scenes["LOC_START"], palette)
	var texture := illustration.render()
	_equal(texture.get_width(), 64, "illustration width")
	_equal(texture.get_height(), 40, "illustration height")
	_check(world.map_edges.size() > 100, "the chapter map has edges")
	if world.map_edges.size() > 0:
		var edge: Dictionary = world.map_edges[0]
		_check(world.map_nodes.size() > 0, "the chapter map has nodes")


func _test_map_view(world: WorldData) -> void:
	var map_view := MapView.new(world)
	_check(map_view.has_signal("exit_requested"), "map view provides exit_requested signal")
	map_view.zoom_level = 1.75
	map_view.pan_offset = Vector2(42, -17)
	map_view.set_location("LOC_START", {"LOC_START": true})
	_equal(map_view.zoom_level, 1.75, "location refresh preserves map zoom")
	_equal(map_view.pan_offset, Vector2(42, -17), "location refresh preserves map pan")

	# Test across all 34 rooms of the chapter
	for loc_id in world.locations.keys():
		map_view.set_location(loc_id, {"LOC_START": true})
		var exits := map_view._get_exits_for(loc_id)
		_check(exits.size() > 0, "room %s has navigable exits for walkthrough guide" % loc_id)

	# Test start room specific exits
	var start_exits := map_view._get_exits_for("LOC_START")
	var targets: PackedStringArray = PackedStringArray()
	for e in start_exits:
		targets.append(e["target"])
	_check(targets.has("LOC_BUILDING"), "start exits lead to building")
	_check(targets.has("LOC_VALLEY"), "start exits lead to valley")
	_check(targets.has("LOC_HILL"), "start exits lead to hill")

	# Test mode toggle
	_equal(map_view.view_mode, MapView.ViewMode.LOCAL, "initial mode is local guide view")
	map_view._on_mode_toggled()
	_equal(map_view.view_mode, MapView.ViewMode.GLOBAL, "toggled mode is global view")
	map_view._on_mode_toggled()
	_equal(map_view.view_mode, MapView.ViewMode.LOCAL, "toggled back to local view")

	# Observed transitions are display-only and reject non-movements.
	map_view.set_observed_transition("LOC_START", "LOC_BUILDING", "E")
	_equal(map_view.observed_from, "LOC_START", "observed transition stores origin")
	_equal(map_view.observed_to, "LOC_BUILDING", "observed transition stores destination")
	_equal(map_view.observed_command, "E", "observed transition stores parser command")
	map_view.set_observed_transition("LOC_BUILDING", "LOC_BUILDING", "LOOK")
	_equal(map_view.observed_command, "E", "non-movement preserves last observed transition")

	map_view.set_navigation_enabled(false)
	_check(not map_view.navigation_enabled, "debug map navigation is disabled")
	for child in map_view._exit_buttons_flow.get_children():
		if child is Button:
			_check((child as Button).disabled, "debug walkthrough button is disabled")

	map_view.free()


func _test_debug_interface() -> void:
	var main: Control = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	_equal(ProjectSettings.get_setting("display/window/size/viewport_width"), 1920, "base viewport width")
	_equal(ProjectSettings.get_setting("display/window/size/viewport_height"), 1080, "base viewport height")

	var terminal_before: Terminal = main.terminal
	var map_before: MapView = main.map_view
	var terminal_connections := terminal_before.command_entered.get_connections().size()
	var map_connections := map_before.exit_requested.get_connections().size()
	var location_before: String = main.interpreter.state.current_location
	var turn_before: int = main.interpreter.state.turn
	map_before.zoom_level = 1.6
	map_before.pan_offset = Vector2(30, -12)
	var mode_before: MapView.ViewMode = map_before.view_mode
	_check(terminal_before.output.selection_enabled, "terminal output text is selectable")
	_check(terminal_before.input.keep_editing_on_text_submit, "command input keeps editing after Enter")
	await process_frame
	_check(terminal_before.input.has_focus(), "command input receives initial deferred focus")
	terminal_before._on_text_submitted("   ")
	await process_frame
	_check(terminal_before.input.has_focus(), "empty command restores input focus")
	terminal_before.input.text = "texto parcial"

	var tab_event := InputEventKey.new()
	tab_event.keycode = KEY_TAB
	tab_event.pressed = true
	main._input(tab_event)
	_check(main.debug_mode, "debug mode opens")
	_check(main.terminal == terminal_before, "debug mode reuses terminal instance")
	_check(main.map_view == map_before, "debug mode reuses map instance")
	_equal(terminal_before.input.text, "texto parcial", "partial parser input survives opening debug mode")
	_equal(main.interpreter.state.current_location, location_before, "opening debug mode preserves location")
	_equal(main.interpreter.state.turn, turn_before, "opening debug mode preserves turn")
	_equal(map_before.zoom_level, 1.6, "opening debug mode preserves zoom")
	_equal(map_before.pan_offset, Vector2(30, -12), "opening debug mode preserves pan")
	_equal(map_before.view_mode, mode_before, "opening debug mode preserves map mode")
	_check(not map_before.navigation_enabled, "debug mode disables graph navigation")

	main._on_command("E")
	await process_frame
	_check(terminal_before.input.has_focus(), "valid command restores input focus")
	_equal(main.interpreter.state.current_location, "LOC_BUILDING", "parser moves while debug mode is open")
	_equal(map_before.current_location, "LOC_BUILDING", "debug graph follows interpreter location")
	_equal(map_before.observed_from, "LOC_START", "debug graph records actual origin")
	_equal(map_before.observed_to, "LOC_BUILDING", "debug graph records actual destination")
	_equal(map_before.observed_command, "E", "debug graph records movement command")
	_equal(map_before.zoom_level, 1.6, "command execution preserves zoom")
	_equal(map_before.pan_offset, Vector2(30, -12), "command execution preserves pan")

	main._on_command("LOOK")
	await process_frame
	_equal(main.interpreter.state.current_location, "LOC_BUILDING", "LOOK does not move in debug mode")
	_equal(map_before.observed_command, "E", "LOOK preserves the last valid observed transition")

	main._input(tab_event)
	await process_frame
	_check(not main.debug_mode, "debug mode closes")
	_check(terminal_before.input.has_focus(), "view toggle restores input focus")
	_check(map_before.navigation_enabled, "normal mode restores graph navigation")
	_equal(terminal_before.command_entered.get_connections().size(), terminal_connections, "terminal signal is not duplicated")
	_equal(map_before.exit_requested.get_connections().size(), map_connections, "map signal is not duplicated")
	_equal(map_before.zoom_level, 1.6, "closing debug mode preserves zoom")
	_equal(map_before.pan_offset, Vector2(30, -12), "closing debug mode preserves pan")
	_equal(map_before.view_mode, mode_before, "closing debug mode preserves map mode")

	main._on_command("OUT")
	await process_frame
	_equal(main.interpreter.state.current_location, "LOC_START", "parser still moves in normal mode")
	main._on_command("UNKNOWN-COMMAND")
	await process_frame
	_check(terminal_before.input.has_focus(), "unknown command restores input focus")
	terminal_before.input.text_submitted.emit("BLORP")
	await process_frame
	_check(terminal_before.input.has_focus(), "signal submission keeps focus after unknown command")
	terminal_before.input.text_submitted.emit("")
	await process_frame
	_check(terminal_before.input.has_focus(), "signal submission keeps focus after empty command")
	main.free()
