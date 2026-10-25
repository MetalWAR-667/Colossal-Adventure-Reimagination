# Presentation adapter: progressive pilot or unchanged legacy illustration.
class_name IllustrationView
extends Control

const ProgressiveView = preload("res://experiments/vector_playback/playback_view.gd")
const PROGRESSIVE_SOURCES := {
	"LOC_START": "res://experiments/vector_playback/loc_start.json",
}

var world: WorldData
var playback: Control
var current_room := ""
var presentation_kind := "legacy"
var _presented_rooms: Dictionary = {}
var _texture: ImageTexture
var _caption: String = ""


func _init(world_data: WorldData) -> void:
	world = world_data
	custom_minimum_size = Vector2(320, 0)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func show_room(location_id: String) -> void:
	if location_id == current_room:
		return
	current_room = location_id
	_caption = location_id.replace("LOC_", "")
	if PROGRESSIVE_SOURCES.has(location_id):
		presentation_kind = "progressive"
		_texture = null
		if playback == null:
			playback = ProgressiveView.new()
			playback.source_path = PROGRESSIVE_SOURCES[location_id]
			playback.illustration_id = location_id
			playback.autoplay_on_ready = false
			playback.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			add_child(playback)
		playback.show()
		playback.show_room(location_id)
		if _presented_rooms.has(location_id):
			playback.skip()
		_presented_rooms[location_id] = true
		queue_redraw()
		return
	presentation_kind = "legacy"
	if playback != null:
		playback.show_room("")
		playback.hide()
	var scene_id := location_id
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
