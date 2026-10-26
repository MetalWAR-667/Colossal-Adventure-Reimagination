# CUT A: the exported global graph must not enlarge any playable consumer.
# Run separately; the existing 448-check suite remains unchanged.
extends SceneTree

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WorldData.DATASET_PATH))
	var graph: Dictionary = data["simulation_graph"]
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	check(graph["locations"].size() == 185, "global locations present")
	check(world.locations.size() == 42, "playable locations unchanged (34 CH_01 + 8 CH_ENTRY)")
	check(world.objects.size() == 8, "playable objects unchanged")
	var outside := 0
	var inaccessible := true
	var undescribable := true
	var unmapped := true
	var blocked := true
	var narrative_absent := true
	for raw in graph["locations"]:
		var id := String(raw["id"])
		narrative_absent = narrative_absent and not raw.has("description_en")
		if data["locations"].has(id) or WorldData.AUTHORIZED_ADDITIONAL_LOCATIONS.has(id):
			continue
		outside += 1
		inaccessible = inaccessible and not world.is_in_chapter(id) and world.location(id) == null
		undescribable = undescribable and world.describe(id).is_empty() and world.describe_short(id).is_empty()
		for node in world.map_nodes:
			unmapped = unmapped and node["id"] != id
		for edge in world.map_edges:
			unmapped = unmapped and edge["from"] != id and edge["to"] != id
		# Even a direct request through the player's existing movement boundary
		# cannot authorize a simulation-only room. No production method changes.
		var rule := TravelRule.new()
		rule.target = id
		var result: Dictionary = interpreter._execute_move(rule)
		blocked = blocked and not result["moved"] and interpreter.state.current_location == "LOC_START" and interpreter.state.turn == 0
	check(outside == 143, "143 global IDs remain outside playable world")
	check(inaccessible, "all simulation-only locations excluded from player lookups")
	check(undescribable, "no descriptions for simulation-only locations")
	check(unmapped, "no simulation-only map nodes or enabled edges")
	check(blocked, "all simulation-only destinations rejected by player movement")
	check(narrative_absent, "simulation projection contains no location narrative")
	check(world.motion_verbs == data["verbs"]["motions"] and world.action_verbs == data["verbs"]["actions"], "parser tables still come only from playable fields")
	for line in ["E", "TAKE KEYS", "OUT", "DEPRESSION", "UNLOCK GRATE", "ENTER"]:
		interpreter.submit(line)
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "real ENTER command descends to LOC_BELOWGRATE after unlock")
	check(interpreter.state.state_of("GRATE") == "GRATE_OPEN", "CH_01 unlock behavior preserved")
	print("%s: %d CUT A isolation checks; %d simulation-only IDs examined" % ["PASS" if failures == 0 else "FAIL", checks, outside])
	quit(0 if failures == 0 else 1)
