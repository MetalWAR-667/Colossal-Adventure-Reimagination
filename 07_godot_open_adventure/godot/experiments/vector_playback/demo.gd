extends Control

const View = preload("res://experiments/vector_playback/playback_view.gd")
var view: Control
var status: Label
var playback_buttons: Array[Button] = []


func _ready() -> void:
	var panel := VBoxContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var title := Label.new()
	title.text = "CAR-ART-002 · C — Línea solar · LOC_START · PROTOTIPO EXPERIMENTAL"
	panel.add_child(title)
	var note := Label.new()
	note.text = "Preparación acotada → 3,5 s a 1× · No integrado en el juego ni en su parser. Revisión humana pendiente."
	panel.add_child(note)
	view = View.new()
	view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.add_child(view)
	var buttons := HBoxContainer.new()
	panel.add_child(buttons)
	_button(buttons, "Reproducir / Replay", func(): view.replay())
	_button(buttons, "Omitir", func(): view.skip())
	_button(buttons, "Salir de LOC_START / Cancelar", func(): view.show_room("NO_ART"))
	_button(buttons, "Volver a LOC_START", func(): view.show_room("LOC_START"))
	status = Label.new()
	panel.add_child(status)


func _button(host: Control, text: String, action: Callable) -> void:
	var button := Button.new()
	button.text = text
	button.disabled = true
	playback_buttons.append(button)
	button.pressed.connect(action)
	host.add_child(button)


func _process(_delta: float) -> void:
	if view == null:
		return
	var model: RefCounted = view.model
	for button in playback_buttons:
		button.disabled = not model.prepared
	status.text = "%s · %.3f / %.1f s · preparación %.3f s · máx CPU prepare/update/draw: %d / %d / %d µs" % [
		model.error if not model.error.is_empty() else "preparando" if not model.prepared else "reproduciendo" if model.running else "final" if model.complete else "cancelado",
		model.elapsed, model.duration, view.prepare_seconds, view.max_prepare_us, view.max_update_us, view.max_draw_us]
