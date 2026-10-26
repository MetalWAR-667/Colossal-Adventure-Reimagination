# CAR-CORE-002 / R2: complete structural data projection isolation.
# Confirms that res://data/structural_world.json is complete, valid, and inert,
# without enlarging the playable boundary of WorldData or Interpreter.
extends SceneTree

const STRUCTURAL_PATH := "res://data/structural_world.json"

var checks := 0
var failures := 0


func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		printerr("FAIL: " + label)


func _initialize() -> void:
	check(FileAccess.file_exists(STRUCTURAL_PATH), "structural_world.json exists in res://data/")
	var raw_text := FileAccess.get_file_as_string(STRUCTURAL_PATH)
	check(not raw_text.is_empty(), "structural_world.json is non-empty")

	var data: Dictionary = JSON.parse_string(raw_text)
	check(not data.is_empty(), "structural_world.json parses valid JSON")

	var meta: Dictionary = data.get("meta", {})
	check(meta.get("cut_id") == "CAR-CORE-002-R2", "cut_id matches CAR-CORE-002-R2")
	check(meta.get("document_status") == "INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE", "document_status is inert")
	check(int(meta.get("schema_version", 0)) == 1, "schema_version is 1")

	var counts: Dictionary = meta.get("counts", {})
	check(int(counts.get("locations", 0)) == 185, "counts.locations is 185")
	check(int(counts.get("travel_records", 0)) == 623, "counts.travel_records is 623")
	check(int(counts.get("objects", 0)) == 70, "counts.objects is 70")
	check(int(counts.get("chapters", 0)) == 11, "counts.chapters is 11")

	var locations: Array = data.get("locations", [])
	var travel: Array = data.get("travel", [])
	var objects: Array = data.get("objects", [])
	var chapters: Array = data.get("chapters", [])
	check(locations.size() == 185, "structural locations array has 185 elements")
	check(travel.size() == 623, "structural travel array has 623 elements")
	check(objects.size() == 70, "structural objects array has 70 elements")
	check(chapters.size() == 11, "structural chapters array has 11 elements")

	# WorldData load_default must remain strictly limited to Chapter 01
	var world := WorldData.load_default()
	var interpreter := Interpreter.new(world)
	check(world.locations.size() == 42, "playable locations strictly preserved at 42")
	check(world.objects.size() == 8, "playable objects strictly preserved at 8")

	var outside := 0
	var inaccessible := true
	var undescribable := true
	var unmapped := true
	var blocked := true

	for raw in locations:
		var loc: Dictionary = raw
		var id := String(loc.get("id", ""))
		if world.locations.has(id):
			continue
		outside += 1
		inaccessible = inaccessible and not world.is_in_chapter(id) and world.location(id) == null
		undescribable = undescribable and world.describe(id).is_empty() and world.describe_short(id).is_empty()
		for node in world.map_nodes:
			unmapped = unmapped and node["id"] != id
		for edge in world.map_edges:
			unmapped = unmapped and edge["from"] != id and edge["to"] != id
		var rule := TravelRule.new()
		rule.target = id
		var result: Dictionary = interpreter._execute_move(rule)
		blocked = blocked and not result["moved"] and interpreter.state.current_location == "LOC_START" and interpreter.state.turn == 0

	check(outside == 143, "exactly 143 inert locations outside playable boundary")
	check(inaccessible, "all 143 inert locations excluded from player lookups")
	check(undescribable, "no descriptions accessible in runtime for inert locations")
	check(unmapped, "no inert locations in playable map nodes or edges")
	check(blocked, "movement to all inert locations strictly rejected")

	# Playable sequence check: ensure CH_01 game loop and boundary gate remain intact
	for line in ["E", "TAKE KEYS", "OUT", "DEPRESSION", "UNLOCK GRATE", "ENTER"]:
		interpreter.submit(line)
	check(interpreter.state.current_location == "LOC_BELOWGRATE", "ENTER descends into LOC_BELOWGRATE after unlocking GRATE")
	check(interpreter.state.state_of("GRATE") == "GRATE_OPEN", "GRATE unlocking works normally")

	print("%s: %d CAR-CORE-002 / R2 structural isolation checks; %d inert locations examined" % [
		"PASS" if failures == 0 else "FAIL",
		checks,
		outside
	])
	quit(0 if failures == 0 else 1)
