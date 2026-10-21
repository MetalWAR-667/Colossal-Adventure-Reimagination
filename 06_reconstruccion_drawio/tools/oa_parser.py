#!/usr/bin/env python3
"""
Open Adventure YAML parser.

Reads the canonical Open_Adventure.yaml and produces a deterministic
intermediate representation (IR) preserving identifiers, descriptions,
travel rules, conditions, objects, hints, sounds, and provenance.

No source data is invented or silently corrected.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML with anchors/merged references resolved."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping at root, got {type(data).__name__}")
    return data


def _normalise_omap(value: Any) -> list[tuple[str, Any]]:
    """PyYAML returns !!omap as a list of (key, value) tuples."""
    if value is None:
        return []
    if isinstance(value, list):
        normalised: list[tuple[str, Any]] = []
        for item in value:
            if isinstance(item, tuple) and len(item) == 2:
                normalised.append((str(item[0]), item[1]))
            elif isinstance(item, dict):
                # Fallback for alternate loaders.
                for k, v in item.items():
                    normalised.append((str(k), v))
            else:
                raise ValueError(f"Unexpected omap entry type: {type(item).__name__}")
        return normalised
    raise ValueError(f"Expected !!omap as list, got {type(value).__name__}")


def _extract_location_record(loc_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Build a clean, fully-traceable location record from the raw YAML node."""
    desc = raw.get("description") or {}
    long_text = desc.get("long")
    short_text = desc.get("short")
    maptag = desc.get("maptag")

    # Preserve YAML nulls explicitly so downstream can distinguish empty strings
    # from missing fields.
    record: dict[str, Any] = {
        "source_id": loc_id,
        "description": {
            "long": long_text if long_text is not None else None,
            "short": short_text if short_text is not None else None,
            "maptag": maptag if maptag is not None else None,
        },
        "conditions": dict(raw.get("conditions") or {}),
        "sound": raw.get("sound"),
        "loud": bool(raw.get("loud", False)),
        "hints": _resolve_hint_names(raw.get("hints", [])),
        "travel": [_normalise_travel_rule(t) for t in raw.get("travel", [])],
    }
    return record


def _resolve_hint_names(hints: list[Any]) -> list[str]:
    """Convert YAML hint references back to their human-readable names."""
    names: list[str] = []
    for h in hints:
        if isinstance(h, dict) and "name" in h:
            names.append(str(h["name"]))
        else:
            names.append(str(h))
    return names


def _normalise_travel_rule(rule: dict[str, Any]) -> dict[str, Any]:
    """Return a serialisable copy of a travel rule preserving source structure."""
    action = rule.get("action", [])
    cond = rule.get("cond")
    verbs = rule.get("verbs", [])
    return {
        "verbs": [str(v) for v in verbs],
        "cond": _serialise_condition(cond),
        "action_type": str(action[0]) if action else None,
        "action_target": str(action[1]) if len(action) > 1 else None,
        "action_full": [str(x) for x in action],
    }


def _serialise_condition(cond: Any) -> dict[str, Any] | None:
    """Convert a YAML condition list into a typed, human-readable record."""
    if cond is None:
        return None
    if not isinstance(cond, list) or len(cond) == 0:
        return {"type": "unknown", "raw": repr(cond)}

    head = str(cond[0])
    if head == "pct":
        return {"type": "probability", "percent": cond[1] if len(cond) > 1 else None}
    if head == "carry":
        return {"type": "carry", "object": str(cond[1]) if len(cond) > 1 else None}
    if head == "with":
        return {"type": "with", "object": str(cond[1]) if len(cond) > 1 else None}
    if head == "not":
        return {
            "type": "not",
            "object": str(cond[1]) if len(cond) > 1 else None,
            "state": str(cond[2]) if len(cond) > 2 else None,
        }
    if head == "nodwarves":
        return {"type": "nodwarves"}
    return {"type": "unknown", "raw": [str(x) for x in cond]}


def _extract_object_record(obj_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Build a clean object record from the raw YAML node."""
    locations = raw.get("locations")
    if locations is None:
        loc_list: list[str | None] = []
    elif isinstance(locations, list):
        loc_list = [str(x) for x in locations]
    else:
        loc_list = [str(locations)]

    return {
        "source_id": obj_id,
        "words": [str(w) for w in raw.get("words", [])] if raw.get("words") else [],
        "inventory": raw.get("inventory"),
        "locations": loc_list,
        "states": [str(s) for s in raw.get("states", [])],
        "descriptions": raw.get("descriptions") or [],
        "changes": raw.get("changes") or [],
        "sounds": raw.get("sounds") or [],
        "texts": raw.get("texts") or [],
        "immovable": bool(raw.get("immovable", False)),
        "treasure": bool(raw.get("treasure", False)),
    }


def _extract_motion_record(mot_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": mot_id,
        "words": [str(w) for w in raw.get("words", [])] if raw.get("words") else [],
        "oldstyle": raw.get("oldstyle", True),
    }


def _extract_action_record(act_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": act_id,
        "words": [str(w) for w in raw.get("words", [])] if raw.get("words") else [],
        "message": raw.get("message"),
        "oldstyle": raw.get("oldstyle", True),
        "noaction": bool(raw.get("noaction", False)),
    }


def parse_open_adventure(path: Path) -> dict[str, Any]:
    """Parse the Open Adventure YAML into a deterministic IR."""
    data = _load_yaml(path)

    ir: dict[str, Any] = {
        "source_file": str(path.resolve()),
        "motions": [],
        "actions": [],
        "hints": [],
        "locations": [],
        "objects": [],
        "messages": {},
        "classes": [],
        "turn_thresholds": [],
        "obituaries": [],
        "dwarflocs": [],
    }

    # Motions
    for mot_id, mot_raw in _normalise_omap(data.get("motions", [])):
        ir["motions"].append(_extract_motion_record(mot_id, mot_raw))

    # Hints (plain list of dicts with anchor references already resolved)
    for entry in data.get("hints", []):
        h = entry.get("hint", entry)
        ir["hints"].append({
            "name": str(h.get("name", "")),
            "number": h.get("number"),
            "turns": h.get("turns"),
            "penalty": h.get("penalty"),
            "question": h.get("question"),
            "hint": h.get("hint"),
        })

    # Locations
    for loc_id, loc_raw in _normalise_omap(data.get("locations", [])):
        ir["locations"].append(_extract_location_record(loc_id, loc_raw))

    # Objects
    for obj_id, obj_raw in _normalise_omap(data.get("objects", [])):
        ir["objects"].append(_extract_object_record(obj_id, obj_raw))

    # Arbitrary messages
    for msg_id, msg_text in _normalise_omap(data.get("arbitrary_messages", [])):
        ir["messages"][msg_id] = msg_text

    # Classes and turn thresholds
    ir["classes"] = [dict(c) for c in data.get("classes", [])]
    ir["turn_thresholds"] = [dict(t) for t in data.get("turn_thresholds", [])]
    ir["obituaries"] = [dict(o) for o in data.get("obituaries", [])]
    ir["dwarflocs"] = [str(x) for x in data.get("dwarflocs", [])]

    # Actions
    for act_id, act_raw in _normalise_omap(data.get("actions", [])):
        ir["actions"].append(_extract_action_record(act_id, act_raw))

    return ir


if __name__ == "__main__":
    import json
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    print(json.dumps({
        "locations": len(ir["locations"]),
        "objects": len(ir["objects"]),
        "motions": len(ir["motions"]),
        "actions": len(ir["actions"]),
        "messages": len(ir["messages"]),
        "hints": len(ir["hints"]),
    }, indent=2))
