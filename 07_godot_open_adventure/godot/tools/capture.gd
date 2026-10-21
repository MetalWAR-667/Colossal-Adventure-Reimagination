# Screenshot helper: renders the main scene and stores a PNG in the project.
#
#   Godot_v4.7.x-stable_win64_console.exe --path godot --script res://tools/capture.gd
#
# The window opens for a few frames; the capture is written to
# `godot/captures/main.png`.
extends SceneTree

const FRAMES_BEFORE_CAPTURE := 30
const OUTPUT_PATH := "res://captures/main.png"

var _frames: int = 0


func _initialize() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	root.add_child(scene.instantiate())


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < FRAMES_BEFORE_CAPTURE:
		return false
	var image := root.get_texture().get_image()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://captures"))
	var error := image.save_png(OUTPUT_PATH)
	if error != OK:
		printerr("capture failed with error %d" % error)
	else:
		print("capture written to %s (%dx%d)" % [OUTPUT_PATH, image.get_width(), image.get_height()])
	quit(0)
	return true
