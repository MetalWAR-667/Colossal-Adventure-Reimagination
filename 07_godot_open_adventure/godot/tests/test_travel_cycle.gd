# CUT B unit worlds derived from source records; never enabled in production.
# Baseline before core edits: six characterization checks PASS.
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
	w.locations.clear()
	w.objects.clear()
	w.map_nodes.clear()
	w.map_edges.clear()
	# Only test code reads global records to construct isolated source islands.
	for row in source_locations:
		if not ids.has(String(row["id"])):
			continue
		var travel: Array = []
		for r in row["travel"]:
			travel.append({"verbs": r["verbs"], "action_type": r["action_type"], "target": r["target"], "cond": {"type": "no_dwarves"} if r["nodwarves"] else r["condition"]})
		w.locations[row["id"]] = WorldLocation.from_dict({"id": row["id"], "conditions": row["source_conditions"], "travel": travel})
	w._resolve_motion_names()
	var e := Interpreter.new(w)
	e.state.current_location = start
	e.state.pending_location = start
	return e

func add_object(e: Interpreter, id: String, place: String, prop: String = "") -> void:
	# Minimal symbolic fixtures for the object references in source rows.
	var obj := WorldObject.from_dict({"id": id, "locations": [place], "states": [prop], "initial_state": prop})
	e.world.objects[id] = obj
	e.state.object_place[id] = place
	e.state.object_state[id] = prop

func _initialize() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WorldData.DATASET_PATH))
	source_locations = data["simulation_graph"]["locations"]
	_test_turns()
	_test_forced()
	_test_back()
	_test_terminal_outcomes()
	_test_specials()
	_test_conditions()
	print("%s: %d CUT B travel checks, %d failures" % ["PASS" if failures == 0 else "FAIL", checks, failures])
	quit(0 if failures == 0 else 1)

func _test_turns() -> void:
	var e := Interpreter.new(WorldData.load_default())
	e.submit("LOOK")
	check(e.state.turn == 1, "LOOK counts input")
	e.submit("BLORP")
	check(e.state.turn == 2, "unknown counts input")
	e.submit("")
	check(e.state.turn == 2, "empty input excluded before turn increment")
	e.submit("one two three")
	check(e.state.turn == 2, "overlong input excluded before turn increment")
	e.submit("NE")
	check(e.state.turn == 3 and e.state.current_location == "LOC_START", "rejected movement counts input")
	check(e.state.previous_location == "LOC_START", "rejected ordinary motion updates oldloc")
	e.submit("E")
	check(e.state.turn == 4 and e.state.current_location == "LOC_BUILDING", "successful movement counts input")
	e.submit("TAKE KEYS")
	check(e.state.turn == 5 and e.state.is_carried("KEYS"), "nonmovement puzzle action counts input")
	var lines := e.submit("DOWNSTREAM")
	check(e.state.turn == 6 and e.state.current_location == "LOC_BUILDING", "SEWER HERE returns with one input")
	check(e.visit_log.slice(-2) == PackedStringArray(["LOC_SEWER", "LOC_BUILDING"]) and lines.size() >= 2, "transient is narrated before stable room")
	check(e.state.previous_location == "LOC_SEWER" and e.state.previous_previous_location == "LOC_BUILDING", "SEWER history follows HERE order")
	for line in ["OUT", "DEPRESSION", "UNLOCK GRATE", "ENTER"]:
		e.submit(line)
	check(e.state.current_location == "LOC_BELOWGRATE" and e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "descent into LOC_BELOWGRATE after unlock")
	check(e.state.state_of("GRATE") == "GRATE_OPEN", "grate puzzle preserved")
	e.submit("WEST")
	check(e.state.current_location == "LOC_COBBLE" and e.state.travel_outcome == GameState.TravelOutcome.ARRIVED, "movement west enters LOC_COBBLE")
	check(e.state.turn == 11, "movement to LOC_COBBLE counts one input")
	e = Interpreter.new(WorldData.load_default())
	e.submit("!")
	check(e.state.turn == 1, "nonempty unknown punctuation still counts an input")

func _test_forced() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_CRACK"], "LOC_PITTOP")
	e.submit("WEST")
	check(e.state.current_location == "LOC_PITTOP" and e.state.turn == 1, "CRACK returns without extra input")
	check(e.visit_log == PackedStringArray(["LOC_CRACK", "LOC_PITTOP"]), "CRACK transition order")
	check(e.state.previous_location == "LOC_CRACK" and e.state.previous_previous_location == "LOC_PITTOP", "CRACK oldloc/oldlc2")
	e = fixture(["LOC_MISTHALL", "LOC_DOME"], "LOC_MISTHALL")
	add_object(e, "NUGGET", GameState.CARRIED)
	e.submit("UP")
	check(e.state.current_location == "LOC_MISTHALL" and e.visit_log.has("LOC_DOME") and e.state.turn == 1, "DOME condition and automatic return")
	e = fixture(["LOC_WESTPIT", "LOC_BUILDING1", "LOC_NOCLIMB"], "LOC_WESTPIT")
	add_object(e, "PLANT", "LOC_WESTPIT", "PLANT_THIRSTY")
	e.submit("CLIMB")
	check(e.state.current_location == "LOC_WESTPIT" and e.state.turn == 1, "multiple forced transitions without extra command")
	check(e.visit_log == PackedStringArray(["LOC_BUILDING1", "LOC_NOCLIMB", "LOC_WESTPIT"]), "multi-HERE source order")
	check(e.state.previous_location == "LOC_NOCLIMB" and e.state.previous_previous_location == "LOC_BUILDING1", "multi-HERE history")
	var flags_match := true
	for row in source_locations:
		var f := fixture([String(row["id"])], String(row["id"]))
		flags_match = flags_match and f.world.location(String(row["id"])).is_forced() == bool(row["flags"]["FORCED"])
	check(flags_match, "FORCED derivation matches 185 source records")

func _test_back() -> void:
	var e := Interpreter.new(WorldData.load_default())
	e.submit("E")
	e.submit("BACK")
	check(e.state.current_location == "LOC_START" and e.state.turn == 2, "BACK follows source return route")
	e.submit("BACK")
	check(e.state.current_location == "LOC_BUILDING", "BACK shifts history")
	e.submit("DOWNSTREAM")
	e.submit("BACK")
	check(e.state.current_location == "LOC_BUILDING", "BACK forced oldloc uses oldlc2, same room")
	e = fixture(["LOC_PLOVER", "LOC_ALCOVE"], "LOC_PLOVER")
	add_object(e, "LAMP", GameState.CARRIED)
	e.state.previous_location = "LOC_ALCOVE"
	e.submit("BACK")
	check(e.state.current_location == "LOC_PLOVER" and e.state.travel_outcome == GameState.TravelOutcome.SPOKE, "BACK rechecks special restriction instead of teleporting")
	e = Interpreter.new(WorldData.load_default())
	e.submit("WEST")
	e.submit("NORTH")
	var before := e.state.current_location
	e.submit("BACK")
	check(e.state.current_location == before and e.state.previous_location == before, "NOBACK refuses after historical history shift")

func _test_terminal_outcomes() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "NUGGET", GameState.CARRIED)
	e.submit("DOWN")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEATH_PENDING, "NECKBROKE signals pending death")
	check(e.state.current_location == "LOC_NECKBROKE" and e.state.pending_location == "LOC_NOWHERE", "last entered room retained with pending limbo")
	check(e.state.previous_location == "LOC_NECKBROKE" and e.state.previous_previous_location == "LOC_PITTOP", "killer and last safe location retained")
	e.submit("LOOK")
	check(e.state.turn == 1 and e.state.is_carried("NUGGET") and not e.state.finished, "pending death freezes input without reincarnation or inventory loss")
	e = fixture(["LOC_CLIFF", "LOC_NOMAKE"], "LOC_CLIFF")
	e.submit("JUMP")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEATH_PENDING and e.state.turn == 1, "NOMAKE lethal transient")
	e = fixture(["LOC_PITTOP", "LOC_CRACK"], "LOC_PITTOP")
	# Deliberate corruption of one fixture destination, not a historical route.
	e.world.location("LOC_CRACK").travel[0].target = "LOC_CRACK"
	e.submit("WEST")
	check(e.state.travel_outcome == GameState.TravelOutcome.CYCLE_ERROR, "unexpected cascade stops diagnostically")
	check(e.state.travel_dependency.contains("exceeded") and e.state.turn == 1, "guard records reason without inventing success or turns")

func _test_specials() -> void:
	var e := fixture(["LOC_PLOVER", "LOC_ALCOVE"], "LOC_PLOVER")
	e.submit("WEST")
	check(e.state.current_location == "LOC_ALCOVE", "special 1 empty load")
	e.submit("EAST")
	check(e.state.current_location == "LOC_PLOVER", "special 1 reverse direction")
	add_object(e, "EMERALD", GameState.CARRIED)
	e.submit("WEST")
	check(e.state.current_location == "LOC_ALCOVE", "special 1 emerald alone")
	add_object(e, "LAMP", GameState.CARRIED)
	e.submit("EAST")
	check(e.state.current_location == "LOC_ALCOVE" and e.state.travel_outcome == GameState.TravelOutcome.SPOKE, "special 1 excess load blocked")
	e = fixture(["LOC_PLOVER", "LOC_FOOF6", "LOC_Y2"], "LOC_PLOVER")
	add_object(e, "EMERALD", GameState.CARRIED)
	e.submit("PLOVER")
	check(e.state.object_place["EMERALD"] == "LOC_PLOVER", "special 2 drops emerald at origin")
	check(e.state.current_location == "LOC_Y2" and e.state.turn == 1, "special 2 resumes distinct source row and HERE")
	check(e.visit_log == PackedStringArray(["LOC_FOOF6", "LOC_Y2"]), "special 2 transient order")
	e = fixture(["LOC_NECHASM"], "LOC_NECHASM")
	add_object(e, "TROLL", "LOC_NOWHERE", "TROLL_UNPAID")
	e.submit("OVER")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEPENDENCY_PENDING, "special 3 recognized as explicit dependency")
	check(e.state.travel_dependency.contains("special_3") and e.state.current_location == "LOC_NECHASM", "special 3 never invents crossing")
	check(e.state.state_of("TROLL") == "TROLL_UNPAID", "special 3 pending has no partial object mutation")

func _test_conditions() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_MISTHALL", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "NUGGET", "LOC_NUGGET")
	var loc := e.world.location("LOC_PITTOP")
	# Repeat an identical source record to exercise conditional-skip equivalence.
	loc.travel.insert(5, loc.travel[4])
	e.submit("DOWN")
	check(e.state.current_location == "LOC_MISTHALL", "failed carry skips equivalent repeats to source alternative")
	e = fixture(["LOC_PITTOP", "LOC_MISTHALL", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "NUGGET", "LOC_NUGGET")
	loc = e.world.location("LOC_PITTOP")
	# Mutation fixture: same destination, different condition must not be skipped.
	var alternative := TravelRule.new()
	alternative.target = "LOC_NECKBROKE"
	loc.travel.insert(5, alternative)
	e.submit("DOWN")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEATH_PENDING, "same destination with different condition remains eligible")
	e = fixture(["LOC_SWCHASM"], "LOC_SWCHASM")
	add_object(e, "TROLL", "LOC_SWCHASM", "TROLL_UNPAID")
	e.submit("OVER")
	check(e.state.travel_outcome == GameState.TravelOutcome.SPOKE and e.state.current_location == "LOC_SWCHASM", "with predicate selects source speak before special")
	e = fixture(["LOC_LONGWEST", "LOC_DIFFERENT1"], "LOC_LONGWEST")
	var rng_before := e.rng.state
	e.submit("SOUTH")
	check(e.state.current_location == "LOC_DIFFERENT1", "nodwarves does not prohibit player passage")
	check(e.rng.state != rng_before, "historical player PCT(100) consumes a condition draw")
	e = Interpreter.new(WorldData.load_default())
	e.submit("DEPRESSION")
	var before := e.state.current_location
	var lines := e.submit("ENTER")
	check(e.state.current_location == before and e.state.travel_outcome == GameState.TravelOutcome.SPOKE, "speak is not a location or movement")
	check(not lines.is_empty() and e.state.turn == 2, "speak counts one input")
	e = fixture(["LOC_Y2"], "LOC_Y2")
	lines = e.submit("PLOVER")
	check(e.state.travel_outcome == GameState.TravelOutcome.DEPENDENCY_PENDING and e.state.travel_dependency.contains("EMERALD"), "missing object never masquerades as carried or absent")
	check(lines == [e.world.message("NOT_CONNECTED")], "dependency returns typed command response without script error")
