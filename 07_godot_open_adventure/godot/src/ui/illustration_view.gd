# Shows the pixel-art illustration of the current room.
class_name IllustrationView
extends Control

var world: WorldData
var _texture: ImageTexture
var _caption: String = ""


func _init(world_data: WorldData) -> void:
	world = world_data
	custom_minimum_size = Vector2(320, 220)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL


func show_room(location_id: String) -> void:
	_caption = location_id.replace("LOC_", "")
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


func _draw() -> void:
	var rect := Rect2(Vector2.ZERO, size)
	draw_rect(rect, Color(0.04, 0.05, 0.08))
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
