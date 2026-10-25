# One location of the Open Adventure dungeon, as loaded from the chapter dataset.
class_name WorldLocation
extends RefCounted

var id: String = ""
var chapter_id: String = ""
var description_en: String = ""
var short_en: String = ""
var maptag: String = ""
var conditions: Dictionary = {}
var sound: String = ""
var travel: Array[TravelRule] = []


static func from_dict(data: Dictionary) -> WorldLocation:
	var loc := WorldLocation.new()
	loc.id = String(data.get("id", ""))
	loc.chapter_id = String(data.get("chapter_id", ""))
	loc.description_en = String(data.get("description_en", ""))
	loc.short_en = String(data.get("short_en", ""))
	loc.maptag = String(data.get("maptag", ""))
	loc.conditions = data.get("conditions", {})
	loc.sound = String(data.get("sound", "") if data.get("sound", null) != null else "")
	var rules: Array[TravelRule] = []
	for raw in data.get("travel", []):
		rules.append(TravelRule.from_dict(raw))
	loc.travel = rules
	return loc


func has_condition(name: String) -> bool:
	return bool(conditions.get(name, false))


func is_forced() -> bool:
	# init.c:initialise + make_dungeon.py: [] expands to HERE. All source
	# locations with travel have non-null long text ("" counts), except NOWHERE
	# which has no travel. This is checked against YAML in CUT A's tests.
	return id != "LOC_NOWHERE" and not travel.is_empty() and travel[0].is_here()


## `NOBACK` marks the twisty forest rooms where "go back" is impossible.
func forbids_back() -> bool:
	return has_condition("NOBACK")


func is_above_ground() -> bool:
	return has_condition("ABOVE") or has_condition("FOREST")


func has_water() -> bool:
	return has_condition("FLUID")
