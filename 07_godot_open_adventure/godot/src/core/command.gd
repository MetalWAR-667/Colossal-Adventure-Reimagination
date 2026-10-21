# A parsed player command.
class_name Command
extends RefCounted

enum Kind {
	MOTION,   ## a travel motion, possibly with a destination noun
	ACTION,   ## a non-travel action such as TAKE or OPEN
	UNKNOWN,  ## nothing in the vocabulary matched
}

var raw: String = ""
var verb_stem: String = ""
var noun_stem: String = ""
var noun_text: String = ""
var kind: int = Kind.UNKNOWN
var motion: String = ""
var action: String = ""


func is_motion() -> bool:
	return kind == Kind.MOTION


func is_action() -> bool:
	return kind == Kind.ACTION


func has_noun() -> bool:
	return noun_stem != ""
