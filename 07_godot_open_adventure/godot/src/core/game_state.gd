# Mutable state of a play session: where the player is, what they carry and
# the state of every object of the chapter.
class_name GameState
extends RefCounted

const CARRIED := ""  ## sentinel used as "object place" for carried items

enum TravelOutcome { IDLE, ARRIVED, SPOKE, REJECTED, FRONTIER, DEATH_PENDING, DEPENDENCY_PENDING, CYCLE_ERROR }

var current_location: String = ""
var previous_location: String = ""
var previous_previous_location: String = ""  ## historical oldlc2
var pending_location: String = ""  ## historical newloc, including unresolved outcomes
var travel_outcome: TravelOutcome = TravelOutcome.IDLE
var travel_dependency: String = ""
var visited: Dictionary = {}
var object_place: Dictionary = {}
var object_state: Dictionary = {}
var turn: int = 0
var treasures_taken: int = 0
var finished: bool = false


func reset(world: WorldData) -> void:
	current_location = _start_location(world)
	previous_location = ""
	previous_previous_location = ""
	pending_location = current_location
	travel_outcome = TravelOutcome.IDLE
	travel_dependency = ""
	visited = {}
	object_place = {}
	object_state = {}
	turn = 0
	treasures_taken = 0
	finished = false
	for object_id in world.objects.keys():
		var obj: WorldObject = world.objects[object_id]
		object_place[object_id] = obj.locations[0] if obj.locations.size() > 0 else CARRIED
		object_state[object_id] = obj.initial_state


func _start_location(world: WorldData) -> String:
	if world.locations.has("LOC_START"):
		return "LOC_START"
	var keys := world.locations.keys()
	return String(keys[0]) if keys.size() > 0 else ""


func is_here(object_id: String) -> bool:
	return String(object_place.get(object_id, "")) == current_location


func is_carried(object_id: String) -> bool:
	return String(object_place.get(object_id, "")) == CARRIED


func carried_objects() -> PackedStringArray:
	var result := PackedStringArray()
	for object_id in object_place.keys():
		if is_carried(String(object_id)):
			result.append(String(object_id))
	result.sort()
	return result


func objects_here() -> PackedStringArray:
	var result := PackedStringArray()
	for object_id in object_place.keys():
		if is_here(String(object_id)):
			result.append(String(object_id))
	result.sort()
	return result


func state_of(object_id: String) -> String:
	return String(object_state.get(object_id, ""))


func set_state(object_id: String, state_name: String) -> void:
	object_state[object_id] = state_name


func move_to(location_id: String, update_history: bool = true) -> void:
	if update_history:
		previous_previous_location = previous_location
		previous_location = current_location
	current_location = location_id
	pending_location = location_id
	visited[location_id] = true


func has_visited(location_id: String) -> bool:
	return visited.has(location_id)
