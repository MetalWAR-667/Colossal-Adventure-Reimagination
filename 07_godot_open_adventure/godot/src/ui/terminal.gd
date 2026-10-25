# Terminal panel: the scrolling story text plus the command line.
class_name Terminal
extends VBoxContainer

signal command_entered(command: String)

var output: RichTextLabel
var input: LineEdit
var _font: SystemFont


func _ready() -> void:
	_font = SystemFont.new()
	_font.font_names = PackedStringArray(["Consolas", "Courier New", "DejaVu Sans Mono", "monospace"])

	add_theme_constant_override("separation", 6)

	output = RichTextLabel.new()
	output.bbcode_enabled = true
	output.selection_enabled = true
	output.scroll_following = true
	output.size_flags_vertical = Control.SIZE_EXPAND_FILL
	output.custom_minimum_size = Vector2(0, 320)
	output.add_theme_font_override("normal_font", _font)
	output.add_theme_font_override("bold_font", _font)
	output.add_theme_font_override("mono_font", _font)
	output.add_theme_font_size_override("normal_font_size", 16)
	output.add_theme_color_override("default_color", Color(0.85, 0.87, 0.82))
	add_child(output)

	input = LineEdit.new()
	input.placeholder_text = "Escribe una orden (HELP para más)"
	# Keep the edit session alive after Enter; focus alone is not enough to
	# make LineEdit accept the next command immediately.
	input.keep_editing_on_text_submit = true
	input.add_theme_font_override("font", _font)
	input.add_theme_font_size_override("font_size", 16)
	input.text_submitted.connect(_on_text_submitted)
	add_child(input)


func _on_text_submitted(text: String) -> void:
	var command := text.strip_edges()
	input.clear()
	if command.is_empty():
		focus_input_deferred()
		return
	command_entered.emit(command)
	# The signal handlers may update/reparent other controls before the
	# submission event finishes. Restore focus after that event has settled.
	focus_input_deferred()


func append_lines(lines: Array[String]) -> void:
	for line in lines:
		output.append_text("[color=#d8dccf]%s[/color]\n" % line)
	output.append_text("\n")


func append_echo(command: String) -> void:
	output.append_text("[color=#7fb0d8]> %s[/color]\n" % command)


func append_note(text: String) -> void:
	output.append_text("[color=#e0c070]%s[/color]\n" % text)


func focus_input() -> void:
	input.grab_focus()


func focus_input_deferred() -> void:
	input.call_deferred("grab_focus")
