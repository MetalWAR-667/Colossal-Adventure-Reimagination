# CUT C source-derived darkness/lamp fixtures; global rooms remain test-only.
extends SceneTree

var checks := 0
var failures := 0
var source_locations: Array = []


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func fixture(ids: Array[String], start: String) -> Interpreter:
	var w := WorldData.load_default()
	var lamp := w.world_object("LAMP")
	w.locations.clear()
	w.objects.clear()
	w.l10n_locations.clear()
	w.map_nodes.clear()
	w.map_edges.clear()
	if lamp != null:
		w.objects["LAMP"] = lamp
	for row in source_locations:
		if not ids.has(String(row["id"])):
			continue
		var travel: Array = []
		for rule in row["travel"]:
			travel.append({
				"verbs": rule["verbs"],
				"action_type": rule["action_type"],
				"target": rule["target"],
				"cond": {"type": "no_dwarves"} if rule["nodwarves"] else rule["condition"],
			})
		w.locations[row["id"]] = WorldLocation.from_dict({
			"id": row["id"],
			"description_en": "SOURCE LONG " + String(row["id"]),
			"short_en": "SOURCE SHORT " + String(row["id"]),
			"conditions": row["source_conditions"].duplicate(true),
			"travel": travel,
		})
	w._resolve_motion_names()
	var e := Interpreter.new(w)
	e.state.current_location = start
	e.state.pending_location = start
	e.state.visited.clear()
	return e


func set_lamp(e: Interpreter, place: String, bright: bool) -> void:
	e.state.object_place["LAMP"] = place
	e.state.object_state["LAMP"] = "LAMP_BRIGHT" if bright else "LAMP_DARK"


func add_readable_vend(e: Interpreter, place: String) -> void:
	var vend := WorldObject.from_dict({
		"id": "VEND",
		"words": ["machi", "vendi"],
		"states": ["VEND_BLOCKS", "VEND_UNBLOCKS"],
		"initial_state": "VEND_BLOCKS",
		"locations": [place],
		"texts": [
			"\"Drop coins here to receive fresh batteries.\"",
			"\"Drop coins here to receive fresh batteries.\"",
		],
	})
	e.world.objects["VEND"] = vend
	e.state.object_place["VEND"] = place
	e.state.object_state["VEND"] = "VEND_BLOCKS"
	e.parser = CommandParser.new(e.world)


func seed_for_fall(wants_fall: bool) -> int:
	for candidate in range(1, 10000):
		var probe := RandomNumberGenerator.new()
		probe.seed = candidate
		var falls := probe.randf() * 100.0 < float(Interpreter.PIT_KILL_PERCENT)
		if falls == wants_fall:
			return candidate
	return 0


func _initialize() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WorldData.DATASET_PATH))
	source_locations = data["simulation_graph"]["locations"]
	_test_illumination()
	_test_visibility_and_read()
	_test_energy()
	_test_falls()
	print("%s: %d CUT C darkness/lamp checks, %d failures" % ["PASS" if failures == 0 else "FAIL", checks, failures])
	quit(0 if failures == 0 else 1)


func _test_illumination() -> void:
	var e := Interpreter.new(WorldData.load_default())
	check(e.state.lamp_energy == 330, "lamp starts with historical GAMELIMIT")
	check(not e._is_dark_here(), "LIT start room needs no lamp")
	e = fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	check(e._is_dark_here(), "unlit room is dark without lamp")
	check(not e.world.location("LOC_DEBRIS").has_condition("DEEP"), "darkness does not imply DEEP")
	set_lamp(e, GameState.CARRIED, true)
	check(not e._is_dark_here(), "bright carried lamp illuminates")
	set_lamp(e, "LOC_DEBRIS", true)
	check(not e._is_dark_here(), "bright lamp on room floor illuminates")
	set_lamp(e, "LOC_AWKWARD", true)
	check(e._is_dark_here(), "bright lamp elsewhere does not illuminate")
	set_lamp(e, GameState.CARRIED, false)
	check(e._is_dark_here(), "dark lamp does not illuminate")
	var lines := e.submit("LIGHT")
	check(not e._is_dark_here() and lines.has("SOURCE LONG LOC_DEBRIS"), "lighting HERE restores visibility and re-describes")
	lines = e.submit("EXTINGUISH")
	check(e._is_dark_here() and lines.has(e.world.message("PITCH_DARK")), "extinguishing HERE immediately reports lost illumination")
	e = fixture(["LOC_MISTHALL"], "LOC_MISTHALL")
	check(e.world.location("LOC_MISTHALL").has_condition("DEEP") and e._is_dark_here(), "DEEP remains independent and can also be dark")


func _test_visibility_and_read() -> void:
	var e := fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	set_lamp(e, "LOC_DEBRIS", false)
	var lines := e._describe_current(true)
	check(lines == [e.world.message("PITCH_DARK")], "ordinary dark room hides normal description and objects")
	check(not e.state.has_visited("LOC_DEBRIS"), "dark observation does not advance visible-description state")
	set_lamp(e, "LOC_DEBRIS", true)
	lines = e._describe_current(true)
	check(lines.has("SOURCE LONG LOC_DEBRIS"), "valid light reveals room description")
	check(lines.size() >= 2 and not lines.has(e.world.message("PITCH_DARK")), "valid light reveals visible objects")
	check(e.state.has_visited("LOC_DEBRIS"), "lit observation records visible visit")

	e = fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	add_readable_vend(e, "LOC_DEBRIS")
	lines = e.submit("READ MACHINE")
	check(not lines.is_empty() and lines[0].contains("I see no"), "transitive READ refuses an object in darkness")
	e.world.location("LOC_DEBRIS").conditions["LIT"] = true
	lines = e.submit("READ MACHINE")
	check(lines.has("\"Drop coins here to receive fresh batteries.\""), "transitive READ uses the historical object text in light")
	lines = e.submit("READ")
	check(lines.has("\"Drop coins here to receive fresh batteries.\""), "intransitive READ resolves one visible readable object")

	e = fixture(["LOC_CRACK"], "LOC_CRACK")
	lines = e._describe_current(true)
	check(lines.has("SOURCE LONG LOC_CRACK"), "FORCED room keeps its source description in darkness")
	check(not lines.has(e.world.message("PITCH_DARK")), "FORCED room does not substitute pitch-dark description")


func _test_energy() -> void:
	var e := Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.submit("BLORP")
	check(e.state.lamp_energy == 329 and e.state.turn == 1, "unknown processed input consumes one lamp turn")
	e.submit("NE")
	check(e.state.lamp_energy == 328 and e.state.turn == 2, "rejected movement consumes one lamp turn")
	e.submit("INVENTORY")
	check(e.state.lamp_energy == 327 and e.state.turn == 3, "action input consumes one lamp turn")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, false)
	e.state.lamp_energy = 5
	e.submit("LIGHT LAMP")
	check(e.state.lamp_energy == 5 and e.state.state_of("LAMP") == "LAMP_BRIGHT", "lighting occurs after the command's lampcheck")
	e.submit("LOOK")
	check(e.state.lamp_energy == 4, "LOOK consumes energy while lamp was already bright")
	e.submit("EXTINGUISH LAMP")
	check(e.state.lamp_energy == 3 and e.state.state_of("LAMP") == "LAMP_DARK", "extinguish consumes before switching lamp off")
	e.submit("BLORP")
	check(e.state.lamp_energy == 3, "dark lamp stops energy consumption")

	e = Interpreter.new(WorldData.load_default())
	e.state.current_location = "LOC_BUILDING"
	e.state.pending_location = "LOC_BUILDING"
	set_lamp(e, GameState.CARRIED, true)
	e.submit("DOWNSTREAM")
	check(e.state.current_location == "LOC_BUILDING", "source SEWER HERE cascade still completes")
	check(e.state.lamp_energy == 329, "HERE cascade consumes no additional lamp turn")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.state.lamp_energy = 31
	var lines := e.submit("LOOK")
	check(e.state.lamp_energy == 30 and e.state.lamp_warned, "warning begins at historical WARNTIME")
	check(lines.has(e.world.message("LAMP_DIM")), "missing future batteries produce LAMP_DIM")
	lines = e.submit("LOOK")
	check(lines.count(e.world.message("LAMP_DIM")) == 0, "lamp warning is not repeated")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.state.object_place["BATTERY"] = "LOC_AWKWARD"
	e.state.lamp_energy = 31
	lines = e.submit("LOOK")
	check(lines.has(e.world.message("GET_BATTERIES")), "available batteries elsewhere produce GET_BATTERIES")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.state.set_state("BATTERY", "DEAD_BATTERIES")
	e.state.lamp_energy = 31
	lines = e.submit("LOOK")
	check(lines.has(e.world.message("MISSING_BATTERIES")), "dead batteries produce MISSING_BATTERIES")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.state.object_place["BATTERY"] = GameState.CARRIED
	e.state.lamp_energy = 31
	lines = e.submit("LOOK")
	check(lines.has(e.world.message("REPLACE_BATTERIES")), "fresh batteries HERE are replaced automatically")
	check(e.state.lamp_energy == 2530, "replacement adds historical BATTERYLIFE after decrement")
	check(e.state.state_of("BATTERY") == "DEAD_BATTERIES" and not e.state.lamp_warned, "replacement marks batteries dead and clears warning")

	e = Interpreter.new(WorldData.load_default())
	set_lamp(e, GameState.CARRIED, true)
	e.state.lamp_energy = 1
	e.state.lamp_warned = true
	lines = e.submit("BLORP")
	check(e.state.lamp_energy == -1 and e.state.state_of("LAMP") == "LAMP_DARK", "zero energy exhausts and extinguishes lamp")
	check(lines.has(e.world.message("LAMP_OUT")), "exhaustion reports LAMP_OUT when lamp is HERE")
	lines = e.submit("LIGHT LAMP")
	check(lines.has(e.world.message("LAMP_OUT")) and e.state.state_of("LAMP") == "LAMP_DARK", "exhausted lamp cannot be relit")


func _test_falls() -> void:
	var fall_seed := seed_for_fall(true)
	var safe_seed := seed_for_fall(false)
	check(fall_seed != 0 and safe_seed != 0 and Interpreter.PIT_KILL_PERCENT == 35, "controlled seeds bracket historical 35 percent threshold")

	var e := fixture(["LOC_COBBLE", "LOC_DEBRIS", "LOC_AWKWARD"], "LOC_COBBLE")
	e.rng.seed = fall_seed
	var rng_before := e.rng.state
	var lines := e.submit("WEST")
	check(e.state.current_location == "LOC_DEBRIS" and e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "first arrival from light into darkness does not fall")
	check(e.rng.state == rng_before, "first dark arrival consumes no fall RNG")
	lines = e.submit("WEST")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEATH_PENDING, "below-threshold move from prior darkness becomes pending death")
	check(lines.has(e.world.message("PIT_FALL")), "dark fall emits historical PIT_FALL")
	check(e.state.pending_location == "LOC_NOWHERE" and e.state.previous_previous_location == "LOC_AWKWARD", "dark death preserves lethal location for CUT D")
	var turn_at_death := e.state.turn
	e.submit("LOOK")
	check(e.state.turn == turn_at_death, "pending dark death suspends further input")

	e = fixture(["LOC_DEBRIS", "LOC_AWKWARD"], "LOC_DEBRIS")
	e.rng.seed = safe_seed
	rng_before = e.rng.state
	e.submit("WEST")
	check(e.state.current_location == "LOC_AWKWARD" and e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "outside-threshold draw survives dark movement")
	check(e.rng.state != rng_before, "eligible surviving dark movement consumes one RNG draw")

	e = fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	e.rng.seed = fall_seed
	rng_before = e.rng.state
	lines = e.submit("LOOK")
	check(e.state.travel_outcome != GameState.TravelOutcome.DEATH_PENDING and lines.has(e.world.message("PITCH_DARK")), "LOOK is exempt while still reporting darkness")
	check(e.rng.state == rng_before, "LOOK exemption consumes no fall RNG")

	e = fixture(["LOC_DEBRIS", "LOC_AWKWARD"], "LOC_DEBRIS")
	set_lamp(e, GameState.CARRIED, true)
	e.rng.seed = fall_seed
	rng_before = e.rng.state
	e.submit("WEST")
	check(e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "movement with valid light cannot fall")
	check(e.rng.state == rng_before, "lit movement consumes no fall RNG")

	e = fixture(["LOC_CRACK", "LOC_PITTOP"], "LOC_CRACK")
	e.state.was_dark = true
	e.rng.seed = fall_seed
	rng_before = e.rng.state
	check(e._check_dark_fall().is_empty(), "FORCED current location is excluded from fall check")
	check(e.rng.state == rng_before, "FORCED exclusion consumes no fall RNG")

	e = fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	e.rng.seed = fall_seed
	lines = e.submit("SOUTH")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEATH_PENDING, "historical rejected motion still reaches do_move fall check")
	check(lines.has(e.world.message("PIT_FALL")), "rejected dark motion reports fall when draw is below threshold")

	e = fixture(["LOC_DEBRIS"], "LOC_DEBRIS")
	e.rng.seed = fall_seed
	rng_before = e.rng.state
	e.submit("BLORP")
	check(e.state.travel_outcome != GameState.TravelOutcome.DEATH_PENDING and e.rng.state == rng_before, "non-motion input does not evaluate a fall")

	e = fixture(["LOC_PITTOP", "LOC_CRACK"], "LOC_PITTOP")
	e.rng.seed = safe_seed
	var expected := RandomNumberGenerator.new()
	expected.seed = safe_seed
	expected.randf()
	e.submit("WEST")
	check(e.state.current_location == "LOC_PITTOP" and e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "dark HERE cascade completes with safe draw")
	check(e.rng.state == expected.state, "HERE cascade performs exactly one final fall draw")
