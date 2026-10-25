# CAR-ART-005: source-state selection, actual parser commands and LINE/FILL.
# Optional graphics evidence: -- --output <folder> --frames <temporary folder>.
extends SceneTree

const View = preload("res://experiments/vector_playback/playback_view.gd")
const VARIANTS := ["GRATE_CLOSED", "GRATE_OPEN"]
var checks := 0
var failures: Array[String] = []
var output := ""
var frames := ""
var viewport: SubViewport
var main: Control
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


func state_snapshot(state: GameState) -> PackedByteArray:
	return var_to_bytes([
		state.current_location, state.previous_location, state.visited.duplicate(true),
		state.object_place.duplicate(true), state.object_state.duplicate(true),
		state.turn, state.treasures_taken, state.finished,
	])


func prepared(view: Control) -> void:
	var deadline := Time.get_ticks_msec() + 15000
	while not view.model.prepared and view.model.error.is_empty() and Time.get_ticks_msec() < deadline:
		await process_frame
	check(view.model.prepared and view.model.error.is_empty(), "prepared " + view.illustration_id + ": " + view.model.error)


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


func command(value: String) -> void:
	main.terminal.input.grab_focus()
	main.terminal.input.edit()
	main.terminal.input.text = value
	key(KEY_ENTER)


func capture(name: String) -> void:
	if output.is_empty():
		return
	var shot := await image()
	check(shot.save_png(output.path_join(name)) == OK, "capture " + name)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() == 4 and args[0] == "--output" and args[2] == "--frames":
		output = args[1]
		frames = args[3]
		if DisplayServer.get_name() == "headless":
			printerr("Rendered evidence requires graphics")
			quit(1)
			return
		DirAccess.make_dir_recursive_absolute(output)
	viewport = SubViewport.new()
	viewport.size = Vector2i(736, 400)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var world := WorldData.load_default()
	check(world.locations.has("LOC_GRATE"), "canonical location LOC_GRATE")
	var grate: WorldObject = world.world_object("GRATE")
	check(grate != null and grate.initial_state == "GRATE_CLOSED" and grate.states.has("GRATE_OPEN"), "source-defined object states")
	var final_digests: Dictionary = {}
	for variant: String in VARIANTS:
		var source := "res://data/vector_ch01/" + variant.to_lower() + ".json"
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source))
		check(data.room == variant and data.format == "CAR-ART-002-experimental-v1", "identity and existing format " + variant)
		var view := View.new()
		view.source_path = source
		view.illustration_id = variant
		view.size = Vector2(736, 400)
		viewport.add_child(view)
		await prepared(view)
		if not view.model.prepared:
			quit(1)
			return
		check(view.model.grid == Vector2i(736,400) and is_equal_approx(view.model.duration, 3.5), "canvas and duration " + variant)
		check(not view.model.owners.has(-1), "complete background " + variant)
		for i in view.model.regions.size():
			var order: PackedInt32Array = view.model.regions[i].order
			var sorted := order.duplicate()
			sorted.sort()
			check(order.size() == int(data.regions[i].raster_area) and digest(sorted.to_byte_array()) == data.regions[i].mask_sha256, "%s region %d independent raster" % [variant,i])
			check(order[0] == int(data.regions[i].seed[1])*736 + int(data.regions[i].seed[0]), "%s region %d seed" % [variant,i])
		var record := {"variant":variant,"paths":view.model.lines.size(),"regions":view.model.regions.size(),"prepare_seconds":view.prepare_seconds,"playback_seconds":0.0,"samples":[]}
		if not output.is_empty():
			var sample_time := 0.0
			var deadline := Time.get_ticks_msec() + 10000
			DirAccess.make_dir_recursive_absolute(frames.path_join(variant))
			while view.model.running and Time.get_ticks_msec() < deadline:
				await RenderingServer.frame_post_draw
				if view.model.elapsed >= sample_time:
					var name := "%02d.png" % record.samples.size()
					check(viewport.get_texture().get_image().save_png(frames.path_join(variant).path_join(name)) == OK, "sample " + variant)
					record.samples.append(name)
					sample_time += 0.35
				await process_frame
		else:
			view.set_process(false)
			for i in 260:
				view.model.advance(1.0/60.0)
				if view.model.complete:
					break
			view._update_picture()
		check(view.model.complete, "complete playback " + variant)
		record.playback_seconds = view.last_wall_seconds
		var full := view.model.image.get_data()
		final_digests[variant] = digest(full)
		var contours := var_to_bytes(view.model.visible_paths())
		var rendered: Image
		if not output.is_empty():
			rendered = await image()
			check(rendered.save_png(output.path_join(variant.to_lower() + "_final.png")) == OK, "final image " + variant)
			check(view.last_wall_seconds >= 3.5 and view.last_wall_seconds < 4.0, "wall duration " + variant)
		for at in [0.4, 2.5, 3.2]:
			view.replay()
			view.model.advance(at)
			view.skip()
			check(full == view.model.image.get_data() and contours == var_to_bytes(view.model.visible_paths()), "final equals skip %.1f %s" % [at,variant])
		if not output.is_empty():
			var skipped := await image()
			check(rendered.get_data() == skipped.get_data(), "rendered final equals skip " + variant)
		view.free()
		records.append(record)
	check(final_digests["GRATE_CLOSED"] != final_digests["GRATE_OPEN"], "distinct state drawings")

	# Actual main scene and real typed command dispatch.
	viewport.size = Vector2i(1920, 1080)
	main = load("res://scenes/main.tscn").instantiate()
	viewport.add_child(main)
	await settle()
	var interpreter: Interpreter = main.interpreter
	var state: GameState = interpreter.state
	check(state.state_of("GRATE") == "GRATE_CLOSED", "initial GameState is closed")
	command("DEPRESSION")
	await settle()
	check(state.current_location == "LOC_GRATE", "parser reaches canonical location")
	check(main.illustration.presentation_kind == "progressive" and main.illustration.playback.illustration_id == "GRATE_CLOSED", "closed state selects closed JSON")
	var closed: Control = main.illustration.playback
	var state_before := state_snapshot(state)
	main._refresh_status()
	check(state_snapshot(state) == state_before and main.illustration.playback == closed, "presentation read does not mutate GameState or restart")
	command("UNLOCK GRATE")
	check(state.state_of("GRATE") == "GRATE_CLOSED" and main.illustration.playback == closed, "unlock without keys preserves closed state")
	for move: String in ["BUILD", "E", "TAKE KEYS", "OUT", "DEPRESSION"]:
		command(move)
	check(state.current_location == "LOC_GRATE" and state.is_carried("KEYS"), "parser retrieves keys and returns")
	await prepared(closed)
	closed.replay()
	check(closed.model.running, "closed LINE/FILL running before unlock")
	command("UNLOCK GRATE")
	check(state.state_of("GRATE") == "GRATE_OPEN" and state.current_location == "LOC_GRATE", "interpreter opens grate without movement")
	check(main.illustration.playback != closed and main.illustration.playback.illustration_id == "GRATE_OPEN", "state change chooses open JSON in same room")
	check(not closed.visible and not closed.model.active, "old closed animation canceled and hidden")
	var opened: Control = main.illustration.playback
	check(main.illustration._playbacks["GRATE_CLOSED"] == closed and main.illustration._playbacks["GRATE_OPEN"] == opened, "one cached view per state variant")
	await prepared(opened)
	if not opened.model.prepared:
		quit(1)
		return
	if not output.is_empty():
		var deadline := Time.get_ticks_msec() + 3000
		while opened.model.elapsed < 0.7 and Time.get_ticks_msec() < deadline:
			await process_frame
		await capture("state_transition_open_contours.png")
		while opened.model.elapsed < 2.3 and Time.get_ticks_msec() < deadline:
			await process_frame
		await capture("state_transition_open_gate.png")
	command("LOCK GRATE")
	check(state.state_of("GRATE") == "GRATE_CLOSED" and main.illustration.playback == closed, "lock chooses closed JSON without movement")
	check(not opened.visible and not opened.model.active, "old open animation canceled and hidden")
	command("UNLOCK GRATE")
	check(state.state_of("GRATE") == "GRATE_OPEN" and main.illustration.playback == opened, "reopen reuses open variant")
	await settle()
	check(opened.model.complete and not opened.model.running, "revisit opens at final image without stale animation")
	state_before = state_snapshot(state)
	main._refresh_status()
	check(state_snapshot(state) == state_before and main.illustration.playback == opened, "open presentation remains read-only and stable")
	command("LOOK")
	check(main.illustration.playback == opened and state.state_of("GRATE") == "GRATE_OPEN", "LOOK preserves state and selected art")
	await capture("runtime_grate_open.png")
	key(KEY_TAB)
	await settle()
	check(main.debug_mode and not main.illustration.is_visible_in_tree(), "TAB keeps debug composition")
	command("LOCK GRATE")
	await settle()
	check(main.debug_mode and state.state_of("GRATE") == "GRATE_CLOSED" and main.illustration.playback == closed, "parser changes visible variant while debug composition stays active")
	key(KEY_TAB)
	await settle()
	check(not main.debug_mode and closed.visible and closed.model.complete, "TAB restores current closed art")
	command("UNLOCK GRATE")
	command("BUILD")
	command("DEPRESSION")
	check(state.current_location == "LOC_GRATE" and state.state_of("GRATE") == "GRATE_OPEN" and main.illustration.playback == opened, "return to grate shows current open state")
	command("LOCK GRATE")
	await settle()
	check(state.state_of("GRATE") == "GRATE_CLOSED" and main.illustration.playback == closed, "closing after return shows current state")
	await capture("runtime_grate_closed.png")
	check(main.interpreter == interpreter, "one interpreter remains authoritative")
	if not output.is_empty():
		var file := FileAccess.open(output.path_join("metrics.json"), FileAccess.WRITE)
		file.store_string(JSON.stringify({"godot":Engine.get_version_info().string,"device":RenderingServer.get_video_adapter_name(),"variants":records,"checks":checks,"failures":failures,"manual_validation":"PENDING","source_state":"GameState.state_of(GRATE)"}, "\t") + "\n")
	print("CAR-ART-005: %d checks, %d failures" % [checks,failures.size()])
	main.free()
	viewport.free()
	quit(0 if failures.is_empty() else 1)
