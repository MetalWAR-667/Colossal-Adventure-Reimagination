# One object of the Open Adventure dungeon (lamp, keys, grate, urn, ...).
class_name WorldObject
extends RefCounted

var id: String = ""
var source_index: int = -1
var words: PackedStringArray = PackedStringArray()
var inventory_label: String = ""
var descriptions: PackedStringArray = PackedStringArray()
var changes: PackedStringArray = PackedStringArray()
var texts: PackedStringArray = PackedStringArray()
var states: PackedStringArray = PackedStringArray()
var initial_state: String = ""
var locations: PackedStringArray = PackedStringArray()
var immovable: bool = false
var treasure: bool = false


static func from_dict(data: Dictionary) -> WorldObject:
	var obj := WorldObject.new()
	obj.id = String(data.get("id", ""))
	obj.source_index = int(data.get("source_index", -1))
	obj.words = PackedStringArray(data.get("words", []))
	obj.inventory_label = String(data.get("inventory_label", ""))
	obj.descriptions = PackedStringArray(data.get("descriptions", []))
	obj.changes = PackedStringArray(data.get("changes", []))
	obj.texts = PackedStringArray(data.get("texts", []))
	obj.states = PackedStringArray(data.get("states", []))
	obj.initial_state = String(data.get("initial_state", ""))
	obj.locations = PackedStringArray(data.get("locations", []))
	obj.immovable = bool(data.get("immovable", false))
	obj.treasure = bool(data.get("treasure", false))
	return obj


func state_index(state_name: String) -> int:
	return states.find(state_name)


func description_for(state_name: String) -> String:
	var index := state_index(state_name)
	if index >= 0 and index < descriptions.size():
		return descriptions[index]
	return descriptions[0] if descriptions.size() > 0 else ""


func text_for(state_name: String) -> String:
	var index := state_index(state_name)
	if index >= 0 and index < texts.size():
		return texts[index]
	return texts[0] if not texts.is_empty() else ""
