# Batch data/runtime tests. Optional graphics evidence uses real timed playback.
# -- --output <folder> --frames <temporary folder>; never writes old evidence.
extends SceneTree

const View = preload("res://experiments/vector_playback/playback_view.gd")
const ROOMS := ["LOC_FOREST", "LOC_BUILDING", "LOC_ROADEND", "LOC_HILL", "LOC_VALLEY", "LOC_SLIT", "LOC_CLIFF", "LOC_LEDGE", "LOC_SEWER"]
var checks := 0
var failures: Array[String] = []
var output := ""
var frames := ""
var viewport: SubViewport
var records: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func check(value: bool, label: String) -> void:
	checks += 1
	if not value:
		failures.append(label)
		printerr("FAIL: " + label)


func digest(bytes: PackedByteArray) -> String:
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(bytes)
	return hash.finish().hex_encode()


func prepared(view: Control) -> void:
	var until := Time.get_ticks_msec() + 15000
	while not view.model.prepared and view.model.error.is_empty() and Time.get_ticks_msec() < until:
		await process_frame
	check(view.model.prepared and view.model.error.is_empty(), "preparation " + view.illustration_id + ": " + view.model.error)


func settle() -> void:
	for i in 4:
		await process_frame


func image() -> Image:
	await RenderingServer.frame_post_draw
	return viewport.get_texture().get_image()


func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.pressed = pressed
		viewport.push_input(event)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() == 4 and args[0] == "--output" and args[2] == "--frames":
		output = args[1]
		frames = args[3]
		if DisplayServer.get_name() == "headless":
			quit(1)
			return
	viewport = SubViewport.new()
	viewport.size = Vector2i(736, 400)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var world := WorldData.load_default()
	var forest_ids: Array[String] = []
	for id: String in world.locations:
		if id.begins_with("LOC_FOREST"):
			forest_ids.append(id)
	check(forest_ids.size() == 22 and not world.locations.has("LOC_FOREST"), "forest drawing alias maps 22 real locations")
	check(not IllustrationView.PROGRESSIVE_SOURCES.has("LOC_GRATE"), "human-excluded grate remains legacy fallback")
	for room: String in ROOMS:
		var source := "res://data/vector_ch01/" + room.to_lower() + ".json"
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source))
		check(data.room == room and data.format == "CAR-ART-002-experimental-v1", "identity/approved format " + room)
		check(world.locations.has(room) or room == "LOC_FOREST", "canonical identity " + room)
		var view := View.new()
		view.source_path = source
		view.illustration_id = room
		view.size = Vector2(736,400)
		viewport.add_child(view)
		await prepared(view)
		if not view.model.prepared:
			quit(1)
			return
		check(view.model.grid == Vector2i(736,400) and is_equal_approx(view.model.duration,3.5), "canvas and timing " + room)
		check(not view.model.owners.has(-1), "full coverage " + room)
		for i in view.model.regions.size():
			var order: PackedInt32Array = view.model.regions[i].order
			var sorted := order.duplicate()
			sorted.sort()
			check(order.size() == int(data.regions[i].raster_area) and digest(sorted.to_byte_array()) == data.regions[i].mask_sha256, "%s region %d independent mask equality" % [room,i])
			check(order[0] == int(data.regions[i].seed[1])*736 + int(data.regions[i].seed[0]), "%s region %d seed" % [room,i])
		var bounds_ok := true
		for line in view.model.lines:
			for p in line.points:
				bounds_ok = bounds_ok and p.x >= 0 and p.x <= 736 and p.y >= 0 and p.y <= 400
		check(bounds_ok, "all authored points inside frame " + room)
		var sample_files: Array[String] = []
		var sample_times: Array[float] = []
		if not output.is_empty():
			DirAccess.make_dir_recursive_absolute(output.path_join(room))
			DirAccess.make_dir_recursive_absolute(frames.path_join(room))
			var next_sample := 0.0
			var until := Time.get_ticks_msec() + 10000
			while view.model.running and Time.get_ticks_msec() < until:
				await RenderingServer.frame_post_draw
				if view.model.elapsed >= next_sample:
					var name := "%02d.png" % sample_files.size()
					check(viewport.get_texture().get_image().save_png(frames.path_join(room).path_join(name)) == OK, "playback sample " + room)
					sample_files.append(name)
					sample_times.append(view.model.elapsed)
					next_sample += 0.35
				await process_frame
		else:
			view.set_process(false)
			for i in 260:
				view.model.advance(1.0/60.0)
				if view.model.complete:
					break
			view._update_picture()
		check(view.model.complete, "complete playback " + room)
		var record := {"room":room,"lines":view.model.lines.size(),"regions":view.model.regions.size(),"prepare_seconds":view.prepare_seconds,"playback_seconds":view.last_wall_seconds,"samples":sample_files,"sample_elapsed":sample_times}
		var full: Image
		if not output.is_empty():
			full = await image()
			check(full.save_png(output.path_join(room).path_join("final.png")) == OK, "final capture " + room)
			check(view.last_wall_seconds >= 3.5 and view.last_wall_seconds < 4.0, "wall clock " + room)
		var geometry := var_to_bytes(view.model.visible_paths())
		var fill: PackedByteArray = view.model.image.get_data()
		for at in [0.4,2.5,3.2]:
			view.replay()
			view.model.advance(at)
			view.skip()
			check(fill == view.model.image.get_data() and geometry == var_to_bytes(view.model.visible_paths()), "skip exact fill/paths at %.1f %s" % [at,room])
		if not output.is_empty():
			var skipped: Image = await image()
			record.rendered_skip_equal = full.get_data() == skipped.get_data()
			check(record.rendered_skip_equal, "rendered final equals skip " + room)
		view.replay()
		view.show_room("NO_ART")
		view.model.advance(10.0)
		check(not view.model.active and view.paths.is_empty(), "cancel rejects stale art " + room)
		view.show_room(room)
		check(view.model.complete and not view.model.running, "revisit immediate " + room)
		view.free()
		records.append(record)
		print("VERIFIED " + room)
	# Current production registry, actual main scene and parser, not pilot fixture.
	viewport.size = Vector2i(1920,1080)
	var main: Control = load("res://scenes/main.tscn").instantiate()
	viewport.add_child(main)
	var places: Dictionary = main.interpreter.state.object_place.duplicate()
	var states: Dictionary = main.interpreter.state.object_state.duplicate()
	var interpreter: Interpreter = main.interpreter
	var old: Control
	for room: String in ROOMS:
		var canonical := "LOC_FOREST1" if room == "LOC_FOREST" else room
		# Fixture-only placement for inspection, never an added game travel rule.
		main.interpreter.state.current_location = canonical
		main.terminal.output.clear()
		main._refresh_status()
		check(main.illustration.presentation_kind == "progressive" and main.illustration.playback.illustration_id == room, "current registry routes " + canonical)
		if old != null:
			check(not old.visible and not old.model.running, "previous cached consumer hidden " + room)
		old = main.illustration.playback
		main.terminal.input.grab_focus()
		main.terminal.input.edit()
		main.terminal.input.text = "LOOK"
		key(KEY_ENTER)
		check(main.terminal.output.get_parsed_text().contains("> LOOK"), "real Enter during preparation " + room)
		key(KEY_TAB)
		await settle()
		check(main.debug_mode and not main.illustration.is_visible_in_tree(), "TAB hides " + room)
		await prepared(old)
		check(old.model.complete and not old.model.running, "TAB completes pending " + room)
		var published: bool = var_to_bytes(old.paths) == var_to_bytes(old.model.visible_paths())
		# The headless dummy server returns the creation image even after update.
		# GPU readback is asserted in the graphics run, not claimed headless.
		if DisplayServer.get_name() != "headless":
			published = published and old.texture.get_image().get_data() == old.model.image.get_data()
		check(published, "async completion publishes contours (and texture with graphics) " + room)
		key(KEY_TAB)
		await settle()
		check(not main.debug_mode and old.visible, "normal composition restored " + room)
		if not output.is_empty():
			var runtime: Image = await image()
			check(runtime.save_png(output.path_join(room).path_join("runtime.png")) == OK, "runtime capture " + room)
	for id: String in forest_ids:
		main.illustration.show_room(id)
		check(main.illustration.playback.illustration_id == "LOC_FOREST", "shared forest source " + id)
	main.interpreter.state.current_location = "LOC_GRATE"
	main._refresh_status()
	check(main.illustration.presentation_kind == "legacy" and main.illustration._texture != null, "GRATE fallback retained")
	check(main.interpreter == interpreter and places == interpreter.state.object_place and states == interpreter.state.object_state, "presentation does not change interpreter or object state")
	if not output.is_empty():
		DirAccess.make_dir_recursive_absolute(output.path_join("LOC_GRATE"))
		check(main.illustration._texture.get_image().save_png(output.path_join("LOC_GRATE/legacy.png")) == OK, "blocked grate legacy reference capture")
		var file := FileAccess.open(output.path_join("metrics.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify({"godot":Engine.get_version_info().string,"device":RenderingServer.get_video_adapter_name(),"rooms":records,"checks":checks,"failures":failures,"manual_validation":"PENDING","grate":"BLOCKED BY HUMAN DECISION"},"\t")+"\n")
	print("CAR-ART-004: %d checks, %d failures; nine scenes, GRATE excluded" % [checks,failures.size()])
	main.free()
	viewport.free()
	quit(0 if failures.is_empty() else 1)
