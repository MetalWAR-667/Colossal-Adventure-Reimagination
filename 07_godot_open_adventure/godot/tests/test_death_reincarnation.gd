# CUT D source-derived death/reincarnation fixtures; never enable CH_02.
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
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WorldData.DATASET_PATH))
	var w := WorldData.load_default()
	w.locations.clear()
	w.objects.clear()
	w.map_nodes.clear()
	w.map_edges.clear()
	for row in data["simulation_graph"]["locations"]:
		if not ids.has(String(row["id"])):
			continue
		var travel: Array = []
		for r in row["travel"]:
			travel.append({"verbs": r["verbs"], "action_type": r["action_type"], "target": r["target"], "cond": {"type": "no_dwarves"} if r["nodwarves"] else r["condition"]})
		w.locations[row["id"]] = WorldLocation.from_dict({"id": row["id"], "conditions": row["source_conditions"].duplicate(true), "travel": travel})
	# Reincarnation returns to playable source rooms without opening any cave room.
	for id in ["LOC_START", "LOC_BUILDING"]:
		if not w.locations.has(id):
			w.locations[id] = WorldData.load_default().location(id)
	w._resolve_motion_names()
	var e := Interpreter.new(w)
	e.state.current_location = start
	e.state.pending_location = start
	return e


func add_object(e: Interpreter, id: String, place: String, prop: String = "STATE_FOUND") -> void:
	var obj := WorldObject.from_dict({"id": id, "locations": [place], "states": [prop], "initial_state": prop})
	e.world.objects[id] = obj
	e.state.object_place[id] = place
	e.state.object_state[id] = prop


func _initialize() -> void:
	_test_typed_deaths()
	_test_dialogue_and_limits()
	_test_reincarnation_objects()
	_test_history_and_followup()
	_test_score()
	print("%s: %d CUT D death/reincarnation checks, %d failures" % ["PASS" if failures == 0 else "FAIL", checks, failures])
	quit(0 if failures == 0 else 1)


func _kill_by_destination(e: Interpreter) -> Array[String]:
	if not e.state.object_place.has("NUGGET"):
		add_object(e, "NUGGET", GameState.CARRIED)
	else:
		e.state.object_place["NUGGET"] = GameState.CARRIED
	return e.submit("DOWN")


func _test_typed_deaths() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "NUGGET", GameState.CARRIED)
	var lines := _kill_by_destination(e)
	check(e.state.death_count == 1 and e.state.session_phase == GameState.SessionPhase.REINCARNATION_PENDING, "typed lethal destination is consumed once")
	check(e.state.last_death_cause == "lethal_destination" and e.state.last_death_location == "LOC_NECKBROKE", "lethal destination diagnosis is preserved")
	check(not lines.is_empty() and lines[-1] == String(e.world.obituaries[0]["query"]), "first obituary query follows source data")
	check(e._consume_death_pending().is_empty() and e.state.death_count == 1, "an already consumed typed death cannot count twice")
	var turn := e.state.turn
	var energy := e.state.lamp_energy
	e.submit("LOOK")
	check(e.state.death_count == 1 and e.state.turn == turn and e.state.lamp_energy == energy, "pending dialogue suspends commands turns and lamp")
	e = fixture(["LOC_DEBRIS", "LOC_AWKWARD"], "LOC_DEBRIS")
	add_object(e, "LAMP", "LOC_NOWHERE", "LAMP_DARK")
	e.state.was_dark = true
	e.rng.seed = 1
	while e.rng.randf() * 100.0 >= 35.0:
		e.rng.seed += 1
	# Restore the successful seed because the loop consumed its probe.
	var seed := e.rng.seed
	e.rng.seed = seed
	lines = e.submit("WEST")
	check(e.state.death_count == 1 and e.state.last_death_cause == "darkness_fall", "dark fall uses the same authoritative death consumer")
	check(lines.has(e.world.message("PIT_FALL")) and e.state.session_phase == GameState.SessionPhase.REINCARNATION_PENDING, "dark fall reports cause then obituary")


func _test_dialogue_and_limits() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	_kill_by_destination(e)
	var turn := e.state.turn
	var lines := e.submit("")
	check(lines == [e.world.message("PLEASE_ANSWER"), String(e.world.obituaries[0]["query"])], "empty reincarnation reply repeats source prompt")
	lines = e.submit("maybe")
	check(lines == [e.world.message("PLEASE_ANSWER"), String(e.world.obituaries[0]["query"])], "invalid reincarnation reply repeats source prompt")
	check(e.state.turn == turn and e.state.death_count == 1, "invalid replies neither count turns nor deaths")
	lines = e.submit("yes please")
	check(lines[0] == String(e.world.obituaries[0]["yes_response"]) and e.state.session_phase == GameState.SessionPhase.PLAYING, "affirmative first reply reincarnates")
	# Prefix behavior is the historical strncmp first-word contract.
	e.state.current_location = "LOC_PITTOP"
	e.state.pending_location = "LOC_PITTOP"
	_kill_by_destination(e)
	lines = e.submit("YELLOW")
	check(e.state.death_count == 2 and not e.state.finished and lines[0] == String(e.world.obituaries[1]["yes_response"]), "second death accepts historical y prefix")
	e.state.current_location = "LOC_PITTOP"
	e.state.pending_location = "LOC_PITTOP"
	_kill_by_destination(e)
	check(e.state.death_count == 3 and not e.state.finished, "third death still asks final obituary question")
	lines = e.submit("yes")
	check(e.state.finished and e.state.session_phase == GameState.SessionPhase.FINISHED and lines == [String(e.world.obituaries[2]["yes_response"])], "third affirmative gets final response then ends")
	var location := e.state.current_location
	check(e.submit("NORTH").is_empty() and e.state.current_location == location, "finished game rejects further movement")
	e = fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	_kill_by_destination(e)
	lines = e.submit("no")
	check(e.state.finished and lines == [e.world.message("OK_MAN")], "negative reply ends without reincarnation")
	e = fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	e.state.cave_closing = true
	lines = _kill_by_destination(e)
	check(e.state.finished and e.state.death_count == 1 and lines == [e.world.message("DEATH_CLOSING")], "closing-cave fixture terminates without an obituary question")


func _test_reincarnation_objects() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "LAMP", GameState.CARRIED, "LAMP_BRIGHT")
	add_object(e, "NUGGET", GameState.CARRIED)
	add_object(e, "CAGE", GameState.CARRIED)
	add_object(e, "STATIC", "LOC_START")
	add_object(e, "WATER", GameState.CARRIED)
	add_object(e, "OIL", GameState.CARRIED)
	e.state.lamp_energy = 117
	_kill_by_destination(e)
	e.submit("yes")
	check(e.state.object_place["LAMP"] == "LOC_START" and e.state.state_of("LAMP") == "LAMP_DARK", "carried lamp is extinguished and left outside")
	check(e.state.lamp_energy == 116, "reincarnation preserves post-command lamp energy")
	check(e.state.object_place["NUGGET"] == "LOC_PITTOP" and e.state.object_place["CAGE"] == "LOC_PITTOP", "ordinary carried objects drop at oldlc2")
	check(e.state.state_of("NUGGET") == "STATE_FOUND" and e.state.state_of("CAGE") == "STATE_FOUND", "dropped object properties remain unchanged")
	check(e.state.object_place["WATER"] == "LOC_NOWHERE" and e.state.object_place["OIL"] == "LOC_NOWHERE", "water and oil are destroyed")
	check(e.state.object_place["STATIC"] == "LOC_START", "uncarried objects remain unchanged")
	e = Interpreter.new(WorldData.load_default())
	e.state.object_place["BOTTLE"] = GameState.CARRIED
	e.state.set_state("BOTTLE", "WATER_BOTTLE")
	e.state.previous_previous_location = "LOC_START"
	e.state.travel_outcome = GameState.TravelOutcome.DEATH_PENDING
	e.state.travel_dependency = "fixture_death"
	e._consume_death_pending()
	e.submit("yes")
	check(e.state.state_of("BOTTLE") == "EMPTY_BOTTLE" and e.state.object_place["BOTTLE"] == "LOC_START", "CH_01 bottle representation destroys carried liquid before drop")
	e = fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	add_object(e, "LAMP", "LOC_BUILDING", "LAMP_BRIGHT")
	_kill_by_destination(e)
	e.submit("yes")
	check(e.state.object_place["LAMP"] == "LOC_BUILDING" and e.state.state_of("LAMP") == "LAMP_BRIGHT", "uncarried lamp is untouched")


func _test_history_and_followup() -> void:
	var e := fixture(["LOC_PITTOP", "LOC_NECKBROKE"], "LOC_PITTOP")
	_kill_by_destination(e)
	e.submit("yes")
	check(e.state.current_location == "LOC_BUILDING" and e.state.previous_location == "LOC_BUILDING" and e.state.pending_location == "LOC_BUILDING", "croak returns loc oldloc and newloc to BUILDING")
	check(e.state.previous_previous_location == "LOC_PITTOP" and e.state.travel_outcome == GameState.TravelOutcome.IDLE and e.state.travel_dependency.is_empty(), "death drop history remains but pending travel is cleared")
	var lines := e.submit("BACK")
	check(e.state.current_location == "LOC_BUILDING" and lines.has(e.world.message("FORGOT_PATH")), "BACK cannot escape to lethal history")
	lines = e.submit("OUT")
	check(e.state.current_location == "LOC_START" and not lines.is_empty(), "first ordinary command after reincarnation executes normally")


func _test_score() -> void:
	var e := Interpreter.new(WorldData.load_default())
	var base_without_survival := e._score() - 30
	for deaths in range(4):
		e.state.death_count = deaths
		check(e._score() == base_without_survival + (3 - deaths) * 10, "survival contribution after %d deaths is historical" % deaths)
	e.state.object_place["SAPPH"] = GameState.CARRIED
	check(e._score() == base_without_survival + 2, "non-survival treasure category remains intact")
