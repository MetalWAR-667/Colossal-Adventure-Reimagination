# Isolated presentation. No Interpreter, GameState, global keys or parser hooks.
extends Control

const Playback = preload("res://experiments/vector_playback/playback.gd")
var model := Playback.new()
var texture: ImageTexture
var paths: Array[Dictionary] = []
var room := ""
var visited: Dictionary = {}
var last_wall_seconds := 0.0
var max_prepare_us := 0
var max_update_us := 0
var max_draw_us := 0
var prepare_started := 0
var prepare_seconds := 0.0
var _started := 0
var _last_tick := 0
var _waiting := false


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://experiments/vector_playback/loc_start.json"))
	model.configure(data)
	texture = ImageTexture.create_from_image(model.image)
	prepare_started = Time.get_ticks_usec()
	show_room("LOC_START")


func show_room(id: String) -> void:
	if id == room:
		return
	model.cancel()
	room = id
	_waiting = id == "LOC_START"
	if _waiting and model.prepared:
		_enter_start()
	_update_picture()


func _enter_start() -> void:
	_waiting = false
	if visited.has("LOC_START"):
		model.skip()
	else:
		visited["LOC_START"] = true
		replay()


func replay() -> void:
	if room != "LOC_START" or not model.prepared:
		return
	model.replay()
	_started = Time.get_ticks_usec()
	_last_tick = _started
	last_wall_seconds = 0.0
	_update_picture()


func skip() -> void:
	if room == "LOC_START":
		model.skip()
		_update_picture()


func _process(_delta: float) -> void:
	if not model.error.is_empty():
		return
	if not model.prepared:
		var before := Time.get_ticks_usec()
		model.prepare_step()
		max_prepare_us = maxi(max_prepare_us, Time.get_ticks_usec() - before)
		if model.prepared:
			prepare_seconds = (Time.get_ticks_usec() - prepare_started) / 1000000.0
			if _waiting:
				_enter_start()
		return
	if model.running:
		var before := Time.get_ticks_usec()
		# The first callback may follow a replay click halfway through a frame.
		# Use time since that action, rather than charging the whole prior frame.
		model.advance((before - _last_tick) / 1000000.0)
		_last_tick = before
		_update_picture()
		max_update_us = maxi(max_update_us, Time.get_ticks_usec() - before)
		if model.complete:
			last_wall_seconds = (Time.get_ticks_usec() - _started) / 1000000.0


func _update_picture() -> void:
	if texture != null:
		texture.update(model.image)
	paths = model.visible_paths()
	queue_redraw()


func _draw() -> void:
	var before := Time.get_ticks_usec()
	if texture == null:
		return
	var scale := minf(size.x / model.grid.x, size.y / model.grid.y)
	var origin := (size - Vector2(model.grid) * scale) * 0.5
	draw_set_transform(origin, 0.0, Vector2.ONE * scale)
	draw_texture(texture, Vector2.ZERO)
	var ink := Color(String(model.data.ink))
	for path in paths:
		draw_polyline(path.points, ink, path.width, true)
		# Round caps, with CanvasItem anti-aliased line interiors.
		draw_circle(path.points[0], path.width * 0.5, ink, true, -1.0, true)
		draw_circle(path.points[-1], path.width * 0.5, ink, true, -1.0, true)
	draw_set_transform(Vector2.ZERO)
	max_draw_us = maxi(max_draw_us, Time.get_ticks_usec() - before)
