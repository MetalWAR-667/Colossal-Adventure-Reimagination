# Presentation adapter: progressive pilot or unchanged legacy illustration.
class_name IllustrationView
extends Control

const ProgressiveView = preload("res://experiments/vector_playback/playback_view.gd")
const PROGRESSIVE_SOURCES := {
	"LOC_START": "res://experiments/vector_playback/loc_start.json",
	"LOC_FOREST": "res://data/vector_ch01/loc_forest.json",
	"LOC_BUILDING": "res://data/vector_ch01/loc_building.json",
	"LOC_ROADEND": "res://data/vector_ch01/loc_roadend.json",
	"LOC_HILL": "res://data/vector_ch01/loc_hill.json",
	"LOC_VALLEY": "res://data/vector_ch01/loc_valley.json",
	"LOC_SLIT": "res://data/vector_ch01/loc_slit.json",
	"LOC_CLIFF": "res://data/vector_ch01/loc_cliff.json",
	"LOC_LEDGE": "res://data/vector_ch01/loc_ledge.json",
	"LOC_SEWER": "res://data/vector_ch01/loc_sewer.json",
	"GRATE_CLOSED": "res://data/vector_ch01/grate_closed.json",
	"GRATE_OPEN": "res://data/vector_ch01/grate_open.json",
}

var world: WorldData
var playback: Control
var progressive_sources: Dictionary = PROGRESSIVE_SOURCES.duplicate()
var _playbacks: Dictionary = {}
var current_room := ""
var current_scene_id := ""
var presentation_kind := "legacy"
var _presented_rooms: Dictionary = {}
var _texture: ImageTexture
var _caption: String = ""


func _init(world_data: WorldData) -> void:
	world = world_data
	custom_minimum_size = Vector2(320, 0)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func show_room(location_id: String, visual_state: String = "") -> void:
	var scene_id := location_id
	if location_id.begins_with("LOC_FOREST") and progressive_sources.has("LOC_FOREST"):
		scene_id = "LOC_FOREST"
	elif (
		location_id == "LOC_GRATE"
		and visual_state in ["GRATE_CLOSED", "GRATE_OPEN"]
		and progressive_sources.has(visual_state)
	):
		scene_id = visual_state
	if location_id == current_room and scene_id == current_scene_id:
		return
	current_room = location_id
	current_scene_id = scene_id
	_caption = location_id.replace("LOC_", "")
	if playback != null:
		playback.show_room("")
		playback.hide()
	if progressive_sources.has(scene_id):
		presentation_kind = "progressive"
		_texture = null
		if not _playbacks.has(scene_id):
			playback = ProgressiveView.new()
			playback.source_path = progressive_sources[scene_id]
			playback.illustration_id = scene_id
			playback.autoplay_on_ready = false
			playback.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			add_child(playback)
			_playbacks[scene_id] = playback
		playback = _playbacks[scene_id]
		playback.show()
		playback.show_room(scene_id)
		if _presented_rooms.has(scene_id):
			playback.skip()
		_presented_rooms[scene_id] = true
		queue_redraw()
		return
	presentation_kind = "legacy"
	if not world.art.has("scenes"):
		return
	var scenes: Dictionary = world.art["scenes"]
	if location_id.begins_with("LOC_FOREST") and scenes.has("LOC_FOREST"):
		scene_id = "LOC_FOREST"
	if not scenes.has(scene_id):
		_texture = null
		queue_redraw()
		return

	var meta: Dictionary = world.art.get("meta", {})
	var palette: Dictionary = meta.get("palette", {})
	var illustration := RoomIllustration.from_dict(scenes[scene_id], palette)
	_texture = illustration.render()
	queue_redraw()


func complete_pending() -> void:
	if playback != null and presentation_kind == "progressive":
		playback.skip()


func _draw() -> void:
	var rect := Rect2(Vector2.ZERO, size)
	draw_rect(rect, Color(0.04, 0.05, 0.08))
	if presentation_kind == "progressive":
		return
	if _texture == null:
		draw_string(
			ThemeDB.fallback_font,
			Vector2(12, 24),
			"(sin ilustración para esta sala)",
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			12,
			Color(0.6, 0.6, 0.6)
		)
		return
	var texture_size := _texture.get_size()
	var scale := minf(rect.size.x / texture_size.x, rect.size.y / texture_size.y)
	var draw_size := texture_size * scale
	var origin := (rect.size - draw_size) * 0.5
	draw_texture_rect(_texture, Rect2(origin, draw_size), false, Color(1, 1, 1, 1))
	draw_string(
		ThemeDB.fallback_font,
		Vector2(8, 16),
		_caption,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
	 11,
		Color(0.8, 0.82, 0.86)
	)
