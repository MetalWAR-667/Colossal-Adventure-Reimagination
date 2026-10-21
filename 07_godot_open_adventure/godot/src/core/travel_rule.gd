# Travel rule extracted from the Open Adventure YAML.
#
# Semantics follow `playermove()` in codigo_fuente_open_adventure/main.c:
# a rule matches a motion verb, may carry a condition, and either moves the
# player (`goto`) or prints a message (`speak`).
class_name TravelRule
extends RefCounted

enum ActionType {
	GOTO,
	SPEAK,
}

var verbs: PackedStringArray = PackedStringArray()
var motion_names: PackedStringArray = PackedStringArray()
var action_type: int = ActionType.GOTO
var target: String = ""
var cond_type: String = "always"
var cond_object: String = ""
var cond_state: String = ""
var cond_percent: int = 0
var target_in_chapter: bool = true


static func from_dict(data: Dictionary) -> TravelRule:
	var rule := TravelRule.new()
	rule.verbs = PackedStringArray(data.get("verbs", []))
	var kind := String(data.get("action_type", "goto"))
	rule.action_type = ActionType.SPEAK if kind == "speak" else ActionType.GOTO
	rule.target = String(data.get("target", ""))
	rule.target_in_chapter = bool(data.get("target_in_chapter", true))
	var cond: Dictionary = data.get("cond", {"type": "always"})
	rule.cond_type = String(cond.get("type", "always"))
	rule.cond_object = String(cond.get("object", ""))
	rule.cond_state = String(cond.get("state", ""))
	rule.cond_percent = int(cond.get("percent", 0))
	return rule


## True when the rule has no motion words: the source encodes those as the
## implicit `HERE` motion, which catches every verb.
func is_here() -> bool:
	return verbs.is_empty()


func matches_verb(verb: String) -> bool:
	if is_here():
		return true
	return motion_names.has(verb) or verbs.has(verb)


## Two rules are equivalent for the purpose of the conditional-skip walk in
## `playermove()`: same condition and same destination.
func is_equivalent_to(other: TravelRule) -> bool:
	return (
		cond_type == other.cond_type
		and cond_object == other.cond_object
		and cond_state == other.cond_state
		and action_type == other.action_type
		and target == other.target
	)
