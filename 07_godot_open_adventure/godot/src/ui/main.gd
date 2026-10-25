# Main scene: builds the window layout and connects the terminal to the engine.
extends Control

var world: WorldData
var interpreter: Interpreter
var terminal: Terminal
var illustration: IllustrationView
var map_view: MapView
var status_label: Label
var title_label: Label

var debug_mode: bool = false
var _normal_interface: MarginContainer
var _debug_interface: MarginContainer
var _normal_terminal_host: VBoxContainer
var _normal_map_host: VBoxContainer
var _debug_terminal_host: VBoxContainer
var _debug_map_host: VBoxContainer
var _terminal_output_minimum: Vector2


func _ready() -> void:
	world = WorldData.load_default()
	interpreter = Interpreter.new(world)
	_build_layout()
	_show_intro()
	terminal.focus_input_deferred()


func _build_layout() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var background := ColorRect.new()
	background.color = Color(0.05, 0.06, 0.09)
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	_normal_interface = MarginContainer.new()
	_normal_interface.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		_normal_interface.add_theme_constant_override(side, 14)
	add_child(_normal_interface)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 8)
	_normal_interface.add_child(root)

	title_label = Label.new()
	title_label.text = world.ui("title")
	title_label.add_theme_font_size_override("font_size", 20)
	title_label.add_theme_color_override("font_color", Color(0.92, 0.85, 0.6))
	root.add_child(title_label)

	var subtitle := Label.new()
	subtitle.text = world.ui("subtitle")
	subtitle.add_theme_font_size_override("font_size", 12)
	subtitle.add_theme_color_override("font_color", Color(0.65, 0.68, 0.72))
	root.add_child(subtitle)

	illustration = IllustrationView.new(world)
	root.add_child(illustration)
	resized.connect(_resize_illustration)
	_resize_illustration()

	_normal_terminal_host = VBoxContainer.new()
	_normal_terminal_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_normal_terminal_host.add_theme_constant_override("separation", 14)
	root.add_child(_normal_terminal_host)

	terminal = Terminal.new()
	terminal.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	terminal.size_flags_vertical = Control.SIZE_EXPAND_FILL
	terminal.command_entered.connect(_on_command)
	_normal_terminal_host.add_child(terminal)
	terminal.output.custom_minimum_size = Vector2(0, 80)
	terminal.output.size_flags_stretch_ratio = 0.5
	_terminal_output_minimum = terminal.output.custom_minimum_size

	_normal_map_host = VBoxContainer.new()
	_normal_map_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_normal_map_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_normal_map_host.size_flags_stretch_ratio = 1.5
	_normal_map_host.add_theme_constant_override("separation", 8)
	terminal.add_child(_normal_map_host)
	terminal.move_child(_normal_map_host, 1)

	map_view = MapView.new(world)
	map_view.exit_requested.connect(_on_command)
	_normal_map_host.add_child(map_view)
	map_view.custom_minimum_size.y = 240
	map_view._canvas.custom_minimum_size.y = 120

	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 12)
	status_label.add_theme_color_override("font_color", Color(0.75, 0.78, 0.82))
	root.add_child(status_label)

	_build_debug_interface()


func _resize_illustration() -> void:
	# Stable responsive region, independent of partial stroke/fill bounds.
	if illustration != null:
		illustration.custom_minimum_size.y = clampf(180.0 + (size.y - 720.0) * 0.45, 180.0, 360.0)


func _build_debug_interface() -> void:
	_debug_interface = MarginContainer.new()
	_debug_interface.set_anchors_preset(Control.PRESET_FULL_RECT)
	_debug_interface.visible = false
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		_debug_interface.add_theme_constant_override(side, 14)
	add_child(_debug_interface)

	var panel := ColorRect.new()
	panel.color = Color(0.03, 0.04, 0.07)
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_debug_interface.add_child(panel)

	var debug_root := VBoxContainer.new()
	debug_root.add_theme_constant_override("separation", 10)
	_debug_interface.add_child(debug_root)

	_debug_map_host = VBoxContainer.new()
	_debug_map_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	debug_root.add_child(_debug_map_host)

	_debug_terminal_host = VBoxContainer.new()
	_debug_terminal_host.custom_minimum_size = Vector2(0, 240)
	debug_root.add_child(_debug_terminal_host)


func _show_intro() -> void:
	terminal.append_note(world.chapter_title)
	terminal.append_note(world.chapter_description)
	terminal.append_lines([world.ui("welcome")])
	var description := world.describe(interpreter.state.current_location)
	if not description.is_empty():
		terminal.append_lines([description])
	_refresh_status()


func _on_command(command: String) -> void:
	terminal.append_echo(command)
	var location_before := interpreter.state.current_location
	var lines := interpreter.submit(command)
	var location_after := interpreter.state.current_location
	if location_after != location_before:
		map_view.set_observed_transition(location_before, location_after, command)
	if not lines.is_empty():
		terminal.append_lines(lines)
	_refresh_status()
	terminal.focus_input_deferred()


func _input(event: InputEvent) -> void:
	if event is not InputEventKey:
		return
	var key_event := event as InputEventKey
	if key_event.keycode != KEY_TAB or not key_event.pressed or key_event.echo:
		return
	_toggle_debug_mode()
	get_viewport().set_input_as_handled()


func _toggle_debug_mode() -> void:
	debug_mode = not debug_mode
	_normal_map_host.visible = not debug_mode
	if debug_mode:
		illustration.complete_pending()
		map_view.reparent(_debug_map_host, false)
		terminal.reparent(_debug_terminal_host, false)
		terminal.output.custom_minimum_size = Vector2(0, 180)
		terminal.output.size_flags_stretch_ratio = 1.0
		map_view.set_navigation_enabled(false)
		map_view.custom_minimum_size.y = 320
		map_view._canvas.custom_minimum_size.y = 180
		_normal_interface.visible = false
		_debug_interface.visible = true
	else:
		_debug_interface.visible = false
		map_view.reparent(_normal_map_host, false)
		terminal.reparent(_normal_terminal_host, false)
		_normal_terminal_host.move_child(terminal, 0)
		terminal.output.custom_minimum_size = _terminal_output_minimum
		terminal.output.size_flags_stretch_ratio = 0.5
		map_view.set_navigation_enabled(true)
		map_view.custom_minimum_size.y = 240
		map_view._canvas.custom_minimum_size.y = 120
		_normal_interface.visible = true
	terminal.focus_input_deferred()


func _refresh_status() -> void:
	var location_id := interpreter.state.current_location
	var where := location_id.replace("LOC_", "")
	title_label.text = "%s · %s" % [world.ui("title"), where]
	status_label.text = "%s · %s · turno %d · %s" % [
		world.chapter_title,
		where,
		interpreter.state.turn,
		world.ui("turn_line").replace("{turn}", str(interpreter.state.turn)),
	]
	illustration.show_room(location_id)
	if debug_mode:
		illustration.complete_pending()
	map_view.set_location(location_id, interpreter.state.visited, interpreter.state)
