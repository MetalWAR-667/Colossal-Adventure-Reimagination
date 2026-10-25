# Run with graphics, not --headless. Captures actual rendered/time-driven frames.
# Output defaults to user://car_art_002; optional -- --output <absolute folder>.
extends SceneTree

const View = preload("res://experiments/vector_playback/playback_view.gd")


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if DisplayServer.get_name() == "headless":
		push_error("Rendered evidence requires a graphics driver; do not use --headless.")
		quit(1)
		return
	var output := ProjectSettings.globalize_path("user://car_art_002")
	var args := OS.get_cmdline_user_args()
	if args.size() == 2 and args[0] == "--output":
		output = args[1]
	DirAccess.make_dir_recursive_absolute(output)
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 400)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var view := View.new()
	view.size = Vector2(640, 400)
	viewport.add_child(view)
	while not view.model.prepared and view.model.error.is_empty():
		await process_frame
	if not view.model.error.is_empty():
		push_error(view.model.error)
		quit(1)
		return
	view.replay()
	var frames := 0
	var samples: Array[Dictionary] = []
	var next_sample := 0.0
	var start := Time.get_ticks_usec()
	var max_frame_ms := 0.0
	var last_tick := start
	while view.model.running:
		await RenderingServer.frame_post_draw
		var now := Time.get_ticks_usec()
		max_frame_ms = maxf(max_frame_ms, (now-last_tick)/1000.0)
		last_tick = now
		frames += 1
		if view.model.elapsed >= next_sample:
			var file := "frame_%03d.png" % samples.size()
			var image := viewport.get_texture().get_image()
			if image.is_empty() or image.save_png(output.path_join(file)) != OK:
				push_error("Cannot capture rendered image")
				quit(1)
				return
			samples.append({"file": file, "elapsed": view.model.elapsed})
			next_sample += 0.1
		await process_frame
	await RenderingServer.frame_post_draw
	var full := viewport.get_texture().get_image()
	full.save_png(output.path_join("final.png"))
	var wall := (Time.get_ticks_usec()-start)/1000000.0
	var completion := view.last_wall_seconds
	view.replay()
	view.model.advance(2.5)
	view.skip()
	await process_frame
	await RenderingServer.frame_post_draw
	var skipped := viewport.get_texture().get_image()
	var same := full.get_data() == skipped.get_data()
	var log := {"godot": Engine.get_version_info().string, "display": DisplayServer.get_name(),
		"renderer": RenderingServer.get_current_rendering_method(), "device": RenderingServer.get_video_adapter_name(),
		"grid": [640,400], "target_seconds": view.model.duration, "wall_seconds": wall,
		"view_completion_seconds": completion, "rendered_frames": frames,
		"max_frame_ms_including_capture": max_frame_ms, "prepare_seconds": view.prepare_seconds,
		"max_prepare_us": view.max_prepare_us, "max_update_us": view.max_update_us,
		"max_draw_submission_us": view.max_draw_us, "full_equals_skip_rendered_bytes": same,
		"samples": samples, "visual_human_acceptance": "PENDING"}
	var file := FileAccess.open(output.path_join("metrics.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify(log, "\t") + "\n")
	file.close()
	print(JSON.stringify(log))
	viewport.queue_free()
	await process_frame
	quit(0 if same else 1)
