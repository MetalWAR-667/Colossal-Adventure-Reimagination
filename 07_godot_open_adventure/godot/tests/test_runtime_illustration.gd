# Integrated main-scene regression. Optional real-render evidence: -- --output <folder>.
extends SceneTree

var checks := 0
var failures: Array[String] = []
var viewport: SubViewport
var main: Control
var output := ""
var metrics: Dictionary = {}


func _initialize() -> void:
	call_deferred("_run")


func check(value: bool, label: String) -> void:
	checks += 1
	if not value:
		failures.append(label)
		printerr("FAIL: " + label)


func settle() -> void:
	for i in 4:
		await process_frame


func key(code: Key) -> void:
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = code
		event.pressed = pressed
		viewport.push_input(event)


func command(text: String) -> float:
	main.terminal.input.grab_focus()
	main.terminal.input.edit()
	main.terminal.input.text = text
	var start := Time.get_ticks_usec()
	key(KEY_ENTER)
	return (Time.get_ticks_usec() - start) / 1000.0


func capture(name: String) -> void:
	if output.is_empty():
		return
	await RenderingServer.frame_post_draw
	check(viewport.get_texture().get_image().save_png(output.path_join(name + ".png")) == OK, "capture " + name)


func layout(label: String) -> void:
	var image: Rect2 = main.illustration.get_global_rect()
	var text: Rect2 = main.terminal.output.get_global_rect()
	var graph: Rect2 = main.map_view.get_global_rect()
	var input: Rect2 = main.terminal.input.get_global_rect()
	check(image.end.y <= text.position.y, label + ": narration below illustration")
	check(text.end.y <= graph.position.y, label + ": graph below narration")
	check(graph.end.y <= input.position.y, label + ": input below graph and exits")
	check(input.end.y <= viewport.size.y, label + ": input inside viewport")
	check(main.status_label.get_global_rect().end.y <= viewport.size.y, label + ": status inside viewport")
	check(main.map_view._canvas.size.y >= 120, label + ": graph visible")
	check(image.size.y >= 180, label + ": stable image region")
	metrics[label + "_layout"] = {"image": str(image), "text": str(text), "graph": str(graph), "input": str(input)}


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() == 2 and args[0] == "--output":
		output = args[1]
		if DisplayServer.get_name() == "headless":
			printerr("Rendered evidence requires graphics")
			quit(1)
			return
		DirAccess.make_dir_recursive_absolute(output)
	viewport = SubViewport.new()
	viewport.size = Vector2i(1920, 1080)
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	main = load("res://scenes/main.tscn").instantiate()
	viewport.add_child(main)
	# Preserve the CAR-ART-003 pilot/fallback fixture after the authorized batch
	# migration. Current production selection is covered by test_ch01_vector_art.
	main.illustration.progressive_sources = {"LOC_START": IllustrationView.PROGRESSIVE_SOURCES["LOC_START"]}
	await settle()
	var view: Control = main.illustration.playback
	check(view != null and main.illustration.presentation_kind == "progressive", "pilot selected through adapter")
	var terminal: Terminal = main.terminal
	var map: MapView = main.map_view
	var state: GameState = main.interpreter.state
	var signals: int = terminal.command_entered.get_connections().size()
	var turn: int = state.turn
	var history := terminal.output.get_parsed_text()
	check(not view.model.prepared, "command exercise occurs during preparation")
	metrics.look_during_preparation_ms = command("LOOK")
	check(terminal.output.get_parsed_text().length() > history.length() and terminal.output.get_parsed_text().contains("> LOOK"), "real Enter delivers LOOK while preparing")
	check(state.turn == turn, "LOOK preserves existing turn semantics")
	check(main.illustration.playback == view, "same room command reuses preparation")
	var deadline := Time.get_ticks_msec() + 10000
	while not view.model.prepared and Time.get_ticks_msec() < deadline:
		await process_frame
	check(view.model.prepared and view.model.error.is_empty(), "bounded preparation completes without error")
	if not view.model.prepared:
		quit(1)
		return
	check(view.model.running, "first session presentation starts playback")
	check(main.illustration._texture == null and main.illustration.get_child_count() == 1, "progressive room has no duplicate legacy picture")
	while view.model.elapsed < 0.6 and Time.get_ticks_msec() < deadline:
		await process_frame
	await settle()
	layout("1920x1080")
	await capture("01_contours_1920")
	var elapsed: float = view.model.elapsed
	command("LOOK")
	check(view.model.running and view.model.elapsed >= elapsed, "LOOK during playback does not restart animation")
	check(terminal.input.text.is_empty(), "Enter clears command input")
	while view.model.running and Time.get_ticks_msec() < deadline:
		await process_frame
	check(view.model.complete, "wall-clock playback completes")
	metrics.prepare_seconds = view.prepare_seconds
	metrics.playback_seconds = view.last_wall_seconds
	check(view.last_wall_seconds >= 3.5 and view.last_wall_seconds < 4.0, "playback near 3.5 seconds")
	var final_fill: PackedByteArray = view.model.image.get_data()
	await capture("02_complete_text_graph_1920")
	if not output.is_empty():
		await RenderingServer.frame_post_draw
		var region := Rect2i(main.illustration.get_global_rect())
		var animated := viewport.get_texture().get_image().get_region(region)
		view.skip()
		await settle()
		await RenderingServer.frame_post_draw
		check(animated.get_data() == viewport.get_texture().get_image().get_region(region).get_data(), "integrated rendered final equals skip pixel for pixel")
	command("E")
	await settle()
	check(state.current_location == "LOC_BUILDING", "movement parser unchanged")
	check(main.illustration.presentation_kind == "legacy", "other room uses legacy adapter")
	check(not view.visible and not view.model.active, "legacy room cancels and hides progressive image")
	check(main.illustration._texture != null, "legacy texture available")
	await capture("03_legacy_building_1920")
	command("OUT")
	await settle()
	check(view.model.complete and not view.model.running, "revisit shows final immediately")
	check(view.model.image.get_data() == final_fill, "revisit preserves exact final fill")
	# Voluntary replay only in this test: no new runtime control is introduced.
	view.replay()
	await settle()
	var transition_started := Time.get_ticks_usec()
	metrics.transition_dispatch_ms = command("E")
	if not output.is_empty():
		await process_frame
		await RenderingServer.frame_post_draw
		metrics.transition_to_next_render_ms = (Time.get_ticks_usec() - transition_started) / 1000.0
	await settle()
	check(not view.model.running and view.room.is_empty(), "room change cancels old playback")
	await capture("04_transition_during_playback_1920")
	await create_timer(0.15).timeout
	check(main.illustration.current_room == "LOC_BUILDING" and not view.visible, "old frame never replaces new room")
	command("OUT")
	await settle()
	view.replay()
	terminal.input.text = "texto parcial"
	map.zoom_level = 1.4
	map.pan_offset = Vector2(12, 9)
	key(KEY_TAB)
	await settle()
	check(main.debug_mode and not main.illustration.is_visible_in_tree(), "Tab debug contains no illustration")
	check(view.model.complete and not view.model.running, "Tab finishes pending animation")
	check(not map.navigation_enabled, "debug navigation remains read only")
	check(terminal.input.text == "texto parcial", "Tab preserves partial input")
	await capture("05_debug_1920")
	command("INVENTORY")
	key(KEY_TAB)
	await settle()
	check(not main.debug_mode and main.illustration.is_visible_in_tree(), "Tab restores normal illustration")
	check(main.terminal == terminal and main.map_view == map and main.interpreter.state == state, "single authoritative components survive Tab")
	check(signals == terminal.command_entered.get_connections().size(), "terminal signals remain single")
	check(map.zoom_level == 1.4 and map.pan_offset == Vector2(12, 9), "Tab retains graph camera")
	check(view.model.image.get_data() == final_fill, "Tab retains complete final fill")
	map._on_mode_toggled()
	check(map.view_mode == MapView.ViewMode.GLOBAL, "guide mode remains operative")
	map._reset_view()
	check(map.zoom_level == 1.0, "center control remains operative")
	map._on_mode_toggled()
	for id: String in main.world.art.scenes:
		if id != "LOC_START":
			main.illustration.show_room(id)
			check(main.illustration.presentation_kind == "legacy" and main.illustration._texture != null, "legacy source preserved: " + id)
	main._refresh_status()
	for i in 80:
		terminal.append_lines(["Respuesta larga de prueba %d" % i])
	viewport.size = Vector2i(1280, 720)
	await settle()
	layout("1280x720")
	check(terminal.output.selection_enabled and terminal.output.scroll_following, "scrolling selectable history preserved")
	await capture("06_complete_long_history_1280")
	command("E")
	await settle()
	await capture("07_legacy_1280")
	key(KEY_TAB)
	await settle()
	check(terminal.input.get_global_rect().end.y <= 720, "smaller debug input remains accessible")
	await capture("08_debug_1280")
	key(KEY_TAB)
	await settle()
	# Exercise the existing walkthrough signal, then the canvas hit-test path.
	for button in map._exit_buttons_flow.get_children():
		if button is Button and button.text.contains("START"):
			button.pressed.emit()
			break
	check(state.current_location == "LOC_START", "walkthrough button still moves via the interpreter")
	await settle()
	var bounds: Rect2 = map._calculate_bounds()
	var scale: float = minf(map._canvas.size.x / bounds.size.x, map._canvas.size.y / bounds.size.y) * map.zoom_level
	var offset: Vector2 = (map._canvas.size - bounds.size * scale) * 0.5 - bounds.position * scale + map.pan_offset
	var box: Rect2 = map._node_screen_box(map._get_node("LOC_BUILDING"), scale, offset)
	map._handle_click_at(box.end - Vector2(2, 2))
	check(state.current_location == "LOC_BUILDING", "graph node hit still moves via the interpreter")
	# Exercise leave/revisit and Tab completion before the cache is prepared.
	var pending := IllustrationView.new(main.world)
	pending.progressive_sources = main.illustration.progressive_sources
	viewport.add_child(pending)
	pending.hide()
	pending.show_room("LOC_START")
	pending.show_room("LOC_BUILDING")
	deadline = Time.get_ticks_msec() + 10000
	while not pending.playback.model.prepared and Time.get_ticks_msec() < deadline:
		await process_frame
	check(not pending.playback.model.active and pending.presentation_kind == "legacy", "leaving during preparation never starts stale playback")
	pending.show_room("LOC_START")
	check(pending.playback.model.complete, "revisit after interrupted preparation is immediate")
	pending.free()
	pending = IllustrationView.new(main.world)
	pending.progressive_sources = main.illustration.progressive_sources
	viewport.add_child(pending)
	pending.hide()
	pending.show_room("LOC_START")
	pending.complete_pending()
	deadline = Time.get_ticks_msec() + 10000
	while not pending.playback.model.prepared and Time.get_ticks_msec() < deadline:
		await process_frame
	check(pending.playback.model.complete and not pending.playback.model.running, "Tab completion request survives preparation")
	pending.free()
	metrics.godot = Engine.get_version_info().string
	metrics.display = DisplayServer.get_name()
	metrics.device = RenderingServer.get_video_adapter_name()
	metrics.checks = checks
	metrics.failures = failures
	metrics.human_visual_acceptance = "PENDING"
	if not output.is_empty():
		var file := FileAccess.open(output.path_join("metrics.json"), FileAccess.WRITE)
		file.store_string(JSON.stringify(metrics, "\t") + "\n")
	print("CAR-ART-003: %d checks, %d failures; %s" % [checks, failures.size(), JSON.stringify(metrics)])
	main.free()
	viewport.free()
	quit(0 if failures.is_empty() else 1)
