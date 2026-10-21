# Renders every illustration of the art pack into one contact sheet.
#
#   Godot_v4.7.x-stable_win64_console.exe --headless --path godot \
#       --script res://tools/capture_scenes.gd
#
# The sheet is written to `godot/captures/scenes.png` and is used to review
# the vector art without opening the game window.
extends SceneTree

const ZOOM := 3
const COLUMNS := 3
const OUTPUT_PATH := "res://captures/scenes.png"


func _initialize() -> void:
	var world := WorldData.load_default()
	var meta: Dictionary = world.art.get("meta", {})
	var palette: Dictionary = meta.get("palette", {})
	var scenes: Dictionary = world.art.get("scenes", {})

	var ids: Array = scenes.keys()
	ids.sort()
	var rows := int(ceil(float(ids.size()) / float(COLUMNS)))
	var cell := Vector2i(64 * ZOOM, 40 * ZOOM)
	var sheet := Image.create(cell.x * COLUMNS, cell.y * rows, false, Image.FORMAT_RGBA8)
	sheet.fill(Color(0.05, 0.05, 0.08))

	for index in ids.size():
		var id := String(ids[index])
		var illustration := RoomIllustration.from_dict(scenes[id], palette)
		var image := illustration.render_image()
		image.resize(cell.x, cell.y, Image.INTERPOLATE_NEAREST)
		var column := index % COLUMNS
		var row := index / COLUMNS
		sheet.blit_rect(image, Rect2i(Vector2i.ZERO, Vector2i(cell)), Vector2i(column * cell.x, row * cell.y))

	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://captures"))
	var error := sheet.save_png(OUTPUT_PATH)
	if error != OK:
		printerr("scene sheet failed with error %d" % error)
	else:
		print("scene sheet written to %s (%d scenes)" % [OUTPUT_PATH, ids.size()])
	quit(0)
