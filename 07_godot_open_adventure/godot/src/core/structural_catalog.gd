# Canonical structural data loader and query catalog (CAR-CORE-002 / R3).
#
# Reads and safely validates res://data/structural_world.json without enlarging
# the playable game boundary. Exposes read-only queries for historical research,
# tooling and future chapter reconstruction.
class_name StructuralCatalog
extends RefCounted

const EXPECTED_SCHEMA_VERSION := 1
const EXPECTED_CUT_ID := "CAR-CORE-002-R2"
const EXPECTED_DOCUMENT_STATUS := "INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE"
const EXPECTED_LOCATIONS := 185
const EXPECTED_TRAVEL_RECORDS := 623
const EXPECTED_OBJECTS := 70
const EXPECTED_CHAPTERS := 11
const EXPECTED_DWARFLOCS := 6

var _is_loaded: bool = false
var _last_error: String = ""

var _meta: Dictionary = {}
var _counts: Dictionary = {}
var _all_chapter_ids: PackedStringArray = PackedStringArray()
var _chapters_by_id: Dictionary = {}
var _all_location_ids: PackedStringArray = PackedStringArray()
var _locations_by_id: Dictionary = {}
var _all_object_ids: PackedStringArray = PackedStringArray()
var _objects_by_id: Dictionary = {}
var _travel_records: Array[Dictionary] = []
var _travel_by_location: Dictionary = {}
var _dwarflocs: PackedStringArray = PackedStringArray()
var _structural_dependencies: Dictionary = {}


static func load_default(path: String = "res://data/structural_world.json") -> StructuralCatalog:
	var catalog := StructuralCatalog.new()
	catalog.load_from_file(path)
	return catalog


func load_from_file(path: String) -> bool:
	if not FileAccess.file_exists(path):
		return _fail("StructuralCatalog: file not found at " + path)
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		return _fail("StructuralCatalog: file is empty at " + path)
	return load_from_string(text)


func load_from_string(json_text: String) -> bool:
	_clear()
	if json_text.strip_edges().is_empty():
		return _fail("StructuralCatalog: JSON text is empty")

	var json := JSON.new()
	var parse_err := json.parse(json_text)
	if parse_err != OK:
		return _fail("StructuralCatalog: JSON parse error at line %d: %s" % [json.get_error_line(), json.get_error_message()])
	if typeof(json.data) != TYPE_DICTIONARY:
		return _fail("StructuralCatalog: root payload is not a JSON object")

	var data: Dictionary = json.data

	# 1. Root required keys
	var required_roots := [
		"meta",
		"all_chapter_ids",
		"chapters",
		"chapters_by_id",
		"all_location_ids",
		"locations",
		"locations_by_id",
		"travel",
		"all_object_ids",
		"objects",
		"objects_by_id",
		"dwarflocs",
		"structural_dependencies",
	]
	for root_key: String in required_roots:
		if not data.has(root_key):
			return _fail("StructuralCatalog: missing required root key '" + root_key + "'")

	# 2. Meta validation
	var meta_val: Variant = data["meta"]
	if typeof(meta_val) != TYPE_DICTIONARY:
		return _fail("StructuralCatalog: 'meta' is not a Dictionary")
	var meta: Dictionary = meta_val
	if int(meta.get("schema_version", 0)) != EXPECTED_SCHEMA_VERSION:
		return _fail("StructuralCatalog: incompatible schema_version %s (expected %d)" % [
			str(meta.get("schema_version")),
			EXPECTED_SCHEMA_VERSION
		])
	if String(meta.get("cut_id", "")) != EXPECTED_CUT_ID:
		return _fail("StructuralCatalog: unexpected cut_id '" + String(meta.get("cut_id", "")) + "'")
	if String(meta.get("document_status", "")) != EXPECTED_DOCUMENT_STATUS:
		return _fail("StructuralCatalog: unexpected document_status '" + String(meta.get("document_status", "")) + "'")

	# 3. Chapters validation
	var chapters_arr: Variant = data["chapters"]
	var chapters_map: Variant = data["chapters_by_id"]
	var ch_ids: Variant = data["all_chapter_ids"]
	if typeof(chapters_arr) != TYPE_ARRAY or typeof(chapters_map) != TYPE_DICTIONARY or typeof(ch_ids) != TYPE_ARRAY:
		return _fail("StructuralCatalog: invalid chapter collection types")

	if (chapters_arr as Array).size() != EXPECTED_CHAPTERS:
		return _fail("StructuralCatalog: expected %d chapters, got %d" % [EXPECTED_CHAPTERS, (chapters_arr as Array).size()])
	if (chapters_map as Dictionary).size() != EXPECTED_CHAPTERS:
		return _fail("StructuralCatalog: expected %d chapters_by_id entries, got %d" % [EXPECTED_CHAPTERS, (chapters_map as Dictionary).size()])
	if (ch_ids as Array).size() != EXPECTED_CHAPTERS:
		return _fail("StructuralCatalog: expected %d all_chapter_ids, got %d" % [EXPECTED_CHAPTERS, (ch_ids as Array).size()])

	var seen_chapters: Dictionary = {}
	var member_sum := 0
	for item: Variant in (chapters_arr as Array):
		if typeof(item) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: chapter item is not a Dictionary")
		var ch: Dictionary = item
		var cid := String(ch.get("id", ""))
		if cid.is_empty():
			return _fail("StructuralCatalog: chapter item missing id")
		if seen_chapters.has(cid):
			return _fail("StructuralCatalog: duplicate chapter id '" + cid + "'")
		seen_chapters[cid] = true
		if not (chapters_map as Dictionary).has(cid):
			return _fail("StructuralCatalog: chapter '" + cid + "' missing from chapters_by_id")
		var members: Variant = ch.get("members", [])
		if typeof(members) != TYPE_ARRAY:
			return _fail("StructuralCatalog: chapter '" + cid + "' members is not an Array")
		member_sum += (members as Array).size()

	if member_sum != EXPECTED_LOCATIONS:
		return _fail("StructuralCatalog: chapter members total %d (expected %d)" % [member_sum, EXPECTED_LOCATIONS])

	# 4. Locations validation
	var locs_arr: Variant = data["locations"]
	var locs_map: Variant = data["locations_by_id"]
	var loc_ids: Variant = data["all_location_ids"]
	if typeof(locs_arr) != TYPE_ARRAY or typeof(locs_map) != TYPE_DICTIONARY or typeof(loc_ids) != TYPE_ARRAY:
		return _fail("StructuralCatalog: invalid location collection types")

	if (locs_arr as Array).size() != EXPECTED_LOCATIONS:
		return _fail("StructuralCatalog: expected %d locations, got %d" % [EXPECTED_LOCATIONS, (locs_arr as Array).size()])
	if (locs_map as Dictionary).size() != EXPECTED_LOCATIONS:
		return _fail("StructuralCatalog: expected %d locations_by_id entries, got %d" % [EXPECTED_LOCATIONS, (locs_map as Dictionary).size()])
	if (loc_ids as Array).size() != EXPECTED_LOCATIONS:
		return _fail("StructuralCatalog: expected %d all_location_ids, got %d" % [EXPECTED_LOCATIONS, (loc_ids as Array).size()])

	var seen_locations: Dictionary = {}
	var loc_idx := 0
	var embedded_travel_count := 0
	for item: Variant in (locs_arr as Array):
		if typeof(item) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: location item is not a Dictionary")
		var loc: Dictionary = item
		var lid := String(loc.get("id", ""))
		if lid.is_empty():
			return _fail("StructuralCatalog: location item missing id")
		if seen_locations.has(lid):
			return _fail("StructuralCatalog: duplicate location id '" + lid + "'")
		seen_locations[lid] = true

		if int(loc.get("source_index", -1)) != loc_idx:
			return _fail("StructuralCatalog: location '" + lid + "' source_index mismatch")

		var expected_ch := String(loc.get("chapter_id", ""))
		if not seen_chapters.has(expected_ch):
			return _fail("StructuralCatalog: location '" + lid + "' references unknown chapter '" + expected_ch + "'")

		if not loc.has("flags") or typeof(loc["flags"]) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: location '" + lid + "' missing valid flags")
		if not loc.has("drawio") or typeof(loc["drawio"]) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: location '" + lid + "' missing valid drawio metadata")

		var loc_travel: Variant = loc.get("travel", [])
		if typeof(loc_travel) != TYPE_ARRAY:
			return _fail("StructuralCatalog: location '" + lid + "' travel is not an Array")
		embedded_travel_count += (loc_travel as Array).size()

		loc_idx += 1

	if embedded_travel_count != EXPECTED_TRAVEL_RECORDS:
		return _fail("StructuralCatalog: embedded travel count is %d (expected %d)" % [embedded_travel_count, EXPECTED_TRAVEL_RECORDS])

	# 5. Objects validation
	var objs_arr: Variant = data["objects"]
	var objs_map: Variant = data["objects_by_id"]
	var obj_ids: Variant = data["all_object_ids"]
	if typeof(objs_arr) != TYPE_ARRAY or typeof(objs_map) != TYPE_DICTIONARY or typeof(obj_ids) != TYPE_ARRAY:
		return _fail("StructuralCatalog: invalid object collection types")

	if (objs_arr as Array).size() != EXPECTED_OBJECTS:
		return _fail("StructuralCatalog: expected %d objects, got %d" % [EXPECTED_OBJECTS, (objs_arr as Array).size()])
	if (objs_map as Dictionary).size() != EXPECTED_OBJECTS:
		return _fail("StructuralCatalog: expected %d objects_by_id entries, got %d" % [EXPECTED_OBJECTS, (objs_map as Dictionary).size()])
	if (obj_ids as Array).size() != EXPECTED_OBJECTS:
		return _fail("StructuralCatalog: expected %d all_object_ids, got %d" % [EXPECTED_OBJECTS, (obj_ids as Array).size()])

	var seen_objects: Dictionary = {}
	var obj_idx := 0
	for item: Variant in (objs_arr as Array):
		if typeof(item) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: object item is not a Dictionary")
		var obj: Dictionary = item
		var oid := String(obj.get("id", ""))
		if oid.is_empty():
			return _fail("StructuralCatalog: object item missing id")
		if seen_objects.has(oid):
			return _fail("StructuralCatalog: duplicate object id '" + oid + "'")
		seen_objects[oid] = true

		if int(obj.get("source_index", -1)) != obj_idx:
			return _fail("StructuralCatalog: object '" + oid + "' source_index mismatch")

		if obj_idx == 0:
			if oid != "NO_OBJECT" or not bool(obj.get("is_sentinel", false)):
				return _fail("StructuralCatalog: object index 0 must be NO_OBJECT sentinel")

		obj_idx += 1

	# 6. Travel records validation
	var travel_arr: Variant = data["travel"]
	if typeof(travel_arr) != TYPE_ARRAY:
		return _fail("StructuralCatalog: 'travel' is not an Array")
	if (travel_arr as Array).size() != EXPECTED_TRAVEL_RECORDS:
		return _fail("StructuralCatalog: expected %d travel records, got %d" % [EXPECTED_TRAVEL_RECORDS, (travel_arr as Array).size()])

	var tr_idx := 0
	for item: Variant in (travel_arr as Array):
		if typeof(item) != TYPE_DICTIONARY:
			return _fail("StructuralCatalog: travel item is not a Dictionary")
		var tr: Dictionary = item
		if int(tr.get("global_travel_index", -1)) != tr_idx:
			return _fail("StructuralCatalog: travel record global_travel_index mismatch at index %d" % tr_idx)

		var src_id := String(tr.get("source_location_id", ""))
		if not seen_locations.has(src_id):
			return _fail("StructuralCatalog: travel record %d has unknown source location '%s'" % [tr_idx, src_id])

		var act_type := String(tr.get("action_type", ""))
		if act_type == "goto":
			var dest_id := String(tr.get("destination_location_id", ""))
			if not seen_locations.has(dest_id):
				return _fail("StructuralCatalog: travel record %d has unknown destination location '%s'" % [tr_idx, dest_id])
		elif act_type == "special":
			var target_int := int(tr.get("target", 0))
			if target_int not in [1, 2, 3]:
				return _fail("StructuralCatalog: travel record %d has invalid special target %d" % [tr_idx, target_int])
		elif act_type != "speak":
			return _fail("StructuralCatalog: travel record %d has unknown action_type '%s'" % [tr_idx, act_type])

		tr_idx += 1

	# 7. Dwarflocs validation
	var dlocs_val: Variant = data["dwarflocs"]
	if typeof(dlocs_val) != TYPE_ARRAY:
		return _fail("StructuralCatalog: 'dwarflocs' is not an Array")
	if (dlocs_val as Array).size() != EXPECTED_DWARFLOCS:
		return _fail("StructuralCatalog: expected %d dwarflocs, got %d" % [EXPECTED_DWARFLOCS, (dlocs_val as Array).size()])
	for dl_item: Variant in (dlocs_val as Array):
		var dl_id := String(dl_item)
		if not seen_locations.has(dl_id):
			return _fail("StructuralCatalog: dwarfloc '%s' is not a recognized location" % dl_id)

	# 8. Structural dependencies validation
	var deps_val: Variant = data["structural_dependencies"]
	if typeof(deps_val) != TYPE_DICTIONARY:
		return _fail("StructuralCatalog: 'structural_dependencies' is not a Dictionary")
	var deps: Dictionary = deps_val
	if not deps.has("cross_chapter_transitions"):
		return _fail("StructuralCatalog: 'structural_dependencies' missing cross_chapter_transitions")

	# Population of stores
	_meta = meta.duplicate(true)
	_counts = (meta.get("counts", {}) as Dictionary).duplicate(true)

	_all_chapter_ids = PackedStringArray()
	for cid_var: Variant in (ch_ids as Array):
		_all_chapter_ids.append(String(cid_var))
	_chapters_by_id = (chapters_map as Dictionary).duplicate(true)

	_all_location_ids = PackedStringArray()
	for lid_var: Variant in (loc_ids as Array):
		_all_location_ids.append(String(lid_var))
	_locations_by_id = (locs_map as Dictionary).duplicate(true)

	_all_object_ids = PackedStringArray()
	for oid_var: Variant in (obj_ids as Array):
		_all_object_ids.append(String(oid_var))
	_objects_by_id = (objs_map as Dictionary).duplicate(true)

	_travel_records.clear()
	_travel_by_location.clear()
	for tr_item: Variant in (travel_arr as Array):
		var tr_dict: Dictionary = (tr_item as Dictionary).duplicate(true)
		_travel_records.append(tr_dict)
		var sid := String(tr_dict.get("source_location_id", ""))
		if not _travel_by_location.has(sid):
			_travel_by_location[sid] = [] as Array[Dictionary]
		(_travel_by_location[sid] as Array[Dictionary]).append(tr_dict)

	_dwarflocs = PackedStringArray()
	for dl_item: Variant in (dlocs_val as Array):
		_dwarflocs.append(String(dl_item))

	_structural_dependencies = deps.duplicate(true)

	_is_loaded = true
	_last_error = ""
	return true


func _fail(reason: String) -> bool:
	_clear()
	_last_error = reason
	return false


func _clear() -> void:
	_is_loaded = false
	_last_error = ""
	_meta.clear()
	_counts.clear()
	_all_chapter_ids.clear()
	_chapters_by_id.clear()
	_all_location_ids.clear()
	_locations_by_id.clear()
	_all_object_ids.clear()
	_objects_by_id.clear()
	_travel_records.clear()
	_travel_by_location.clear()
	_dwarflocs.clear()
	_structural_dependencies.clear()


# ---------------------------------------------------------------------------
# Read-only defensive queries
# ---------------------------------------------------------------------------

func is_loaded() -> bool:
	return _is_loaded


func get_last_error() -> String:
	return _last_error


func get_catalog_meta() -> Dictionary:
	return _meta.duplicate(true)


func get_counts() -> Dictionary:
	return _counts.duplicate(true)


func has_location(location_id: String) -> bool:
	return _locations_by_id.has(location_id)


func get_location(location_id: String) -> Dictionary:
	if _locations_by_id.has(location_id):
		return (_locations_by_id[location_id] as Dictionary).duplicate(true)
	return {}


func get_location_ids() -> PackedStringArray:
	return _all_location_ids


func get_travel_records(location_id: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if _travel_by_location.has(location_id):
		for record: Dictionary in _travel_by_location[location_id]:
			result.append(record.duplicate(true))
	return result


func get_all_travel_records() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for record: Dictionary in _travel_records:
		result.append(record.duplicate(true))
	return result


func has_object(object_id: String) -> bool:
	return _objects_by_id.has(object_id)


func get_object(object_id: String) -> Dictionary:
	if _objects_by_id.has(object_id):
		return (_objects_by_id[object_id] as Dictionary).duplicate(true)
	return {}


func get_object_ids() -> PackedStringArray:
	return _all_object_ids


func has_chapter(chapter_id: String) -> bool:
	return _chapters_by_id.has(chapter_id)


func get_chapter(chapter_id: String) -> Dictionary:
	if _chapters_by_id.has(chapter_id):
		return (_chapters_by_id[chapter_id] as Dictionary).duplicate(true)
	return {}


func get_chapter_ids() -> PackedStringArray:
	return _all_chapter_ids


func get_dwarflocs() -> PackedStringArray:
	return _dwarflocs


func get_structural_dependencies() -> Dictionary:
	return _structural_dependencies.duplicate(true)
