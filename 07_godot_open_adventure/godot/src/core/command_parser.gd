# Turns a typed line into a [Command].
#
# The source compares vocabulary by five-letter stems (`DOWNS` matches
# "downstream", `INWAR` matches "inwards"), so the parser does the same: only
# the first five letters of a word take part in the match.
class_name CommandParser
extends RefCounted

const STEM_LENGTH := 5

var _motion_lookup: Dictionary = {}
var _action_lookup: Dictionary = {}


func _init(world: WorldData) -> void:
	for word in world.motion_verbs.keys():
		_motion_lookup[String(word).to_upper()] = String(world.motion_verbs[word])
	for word in world.action_verbs.keys():
		_action_lookup[String(word).to_upper()] = String(world.action_verbs[word])


static func stem(word: String) -> String:
	var trimmed := word.strip_edges().to_upper()
	if trimmed.length() <= STEM_LENGTH:
		return trimmed
	return trimmed.substr(0, STEM_LENGTH)


## Parse one input line.  `motion_first` is true when the word is both a
## motion and an action, so the caller can fall back to the action if no
## travel rule matches the motion.
func parse(line: String) -> Command:
	var command := Command.new()
	command.raw = line.strip_edges()

	var tokens := _tokenize(command.raw)
	if tokens.is_empty():
		return command

	command.verb_stem = stem(tokens[0])
	if tokens.size() > 1:
		command.noun_text = " ".join(tokens.slice(1))
		command.noun_stem = stem(tokens[1])

	var motion := String(_motion_lookup.get(command.verb_stem, ""))
	var action := String(_action_lookup.get(command.verb_stem, ""))

	if motion != "":
		command.kind = Command.Kind.MOTION
		command.motion = motion
		command.action = action
	elif action != "":
		command.kind = Command.Kind.ACTION
		command.action = action
	else:
		command.kind = Command.Kind.UNKNOWN
	return command


## True when the word is both a motion and an action: the interpreter then
## retries as an action when no travel rule matched.
func has_action_fallback(command: Command) -> bool:
	return command.is_motion() and command.action != ""


func _tokenize(line: String) -> PackedStringArray:
	var tokens := PackedStringArray()
	var cleaned := line.to_upper()
	for separator in [".", ",", "!", "?", ";", ":", "\"", "'"]:
		cleaned = cleaned.replace(separator, " ")
	for token in cleaned.split(" ", false):
		tokens.append(token)
	return tokens
