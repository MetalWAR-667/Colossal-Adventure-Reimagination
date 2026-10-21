#!/usr/bin/env python3
"""
Build a deterministic world graph from the parsed Open Adventure IR.

The graph preserves every source travel rule, classifies locations by their
observed role in the database, and computes connection statistics.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from oa_parser import parse_open_adventure


# Locations that exist only as transient/death/special destinations.
# These are identified heuristically by their description and travel behaviour.
SPECIAL_DESTINATION_PATTERNS: dict[str, list[str]] = {
    "death": [
        "LOC_NOWHERE",
        "LOC_NECKBROKE",
        "LOC_NOMAKE",
        "LOC_GRUESOME",
        "LOC_FOOTSLIP",
    ],
    "magic_teleport": [
        "LOC_FOOF1",
        "LOC_FOOF2",
        "LOC_FOOF3",
        "LOC_FOOF4",
        "LOC_FOOF5",
        "LOC_FOOF6",
    ],
    "message_transient": [
        "LOC_DOME",
        "LOC_SNAKEBLOCK",
        "LOC_NOCLIMB",
        "LOC_PLANTTOP",
        "LOC_BUILDING1",
        "LOC_BADDIRECTION",
    ],
    "special_return": [
        "LOC_SEWER",
    ],
}

SPECIAL_IDS: set[str] = set()
for group in SPECIAL_DESTINATION_PATTERNS.values():
    SPECIAL_IDS.update(group)


def _build_motion_word_map(motions: list[dict[str, Any]]) -> dict[str, str]:
    """Map motion symbol (e.g. 'WEST') to a display label (e.g. 'west')."""
    label_map: dict[str, str] = {}
    for mot in motions:
        words = mot.get("words", [])
        label = words[0] if words else mot["source_id"]
        label_map[mot["source_id"]] = label
    return label_map


def _classify_location(loc: dict[str, Any]) -> str:
    """Classify a location based on source identifier and travel rules."""
    loc_id = loc["source_id"]
    if loc_id in SPECIAL_IDS:
        if loc_id == "LOC_NOWHERE":
            return "null"
        return "special"

    travel = loc.get("travel", [])
    # A location is transient if every outbound rule has empty verbs and a goto
    # that immediately sends the player elsewhere (or to nowhere).
    if travel and all(not r.get("verbs") and r.get("action_type") == "goto" for r in travel):
        return "transient"

    return "playable"


def _edge_label(verbs: list[str], motion_map: dict[str, str]) -> str:
    """Build a readable edge label from verb symbols."""
    labels = []
    for v in verbs:
        labels.append(motion_map.get(v, v))
    return ", ".join(labels) if labels else "(implicit)"


def build_graph(ir: dict[str, Any]) -> dict[str, Any]:
    """Construct the world graph and attach classification metadata."""
    motion_map = _build_motion_word_map(ir["motions"])
    locations = ir["locations"]

    loc_index = {loc["source_id"]: loc for loc in locations}

    for loc in locations:
        loc["role"] = _classify_location(loc)
        loc["chapter_id"] = None  # filled by chapter assignment module
        loc["objects_here"] = []  # filled below

    # Attach objects to their start location(s).
    for obj in ir["objects"]:
        for loc_id in obj.get("locations", []):
            if loc_id and loc_id in loc_index:
                loc_index[loc_id]["objects_here"].append(obj["source_id"])

    edges: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    connection_counter: Counter[str] = Counter()

    for loc in locations:
        src = loc["source_id"]
        for rule in loc.get("travel", []):
            action_type = rule.get("action_type")
            target = rule.get("action_target")
            cond = rule.get("cond")
            verbs = rule.get("verbs", [])

            if action_type is None:
                continue

            if action_type == "goto":
                if target is None:
                    unresolved.append({"source": src, "rule": rule, "reason": "goto missing target"})
                    continue
                if target not in loc_index:
                    unresolved.append({"source": src, "rule": rule, "reason": f"target {target} unknown"})
                    continue
                edge = {
                    "source": src,
                    "target": target,
                    "label": _edge_label(verbs, motion_map),
                    "verbs": verbs,
                    "condition": cond,
                    "action_type": "goto",
                }
                edges.append(edge)
                if cond is None:
                    connection_counter["direct"] += 1
                else:
                    ct = cond.get("type")
                    if ct == "probability":
                        connection_counter["random"] += 1
                    elif ct in ("carry", "with", "not", "nodwarves"):
                        connection_counter["conditional"] += 1
                    else:
                        connection_counter["conditional"] += 1
            elif action_type == "speak":
                # Movement produces a message; no location change.
                edges.append({
                    "source": src,
                    "target": None,
                    "label": _edge_label(verbs, motion_map),
                    "verbs": verbs,
                    "condition": cond,
                    "action_type": "speak",
                    "message": target,
                })
                connection_counter["speak"] += 1
            elif action_type == "special":
                # Hard-coded special movement case in the original C code.
                edges.append({
                    "source": src,
                    "target": None,
                    "label": _edge_label(verbs, motion_map),
                    "verbs": verbs,
                    "condition": cond,
                    "action_type": "special",
                    "special_case": target,
                })
                connection_counter["special"] += 1
            else:
                unresolved.append({"source": src, "rule": rule, "reason": f"unknown action type {action_type}"})

    role_counts = Counter(loc["role"] for loc in locations)

    return {
        "source_file": ir["source_file"],
        "motion_map": motion_map,
        "locations": locations,
        "objects": ir["objects"],
        "messages": ir["messages"],
        "edges": edges,
        "unresolved": unresolved,
        "statistics": {
            "total_locations": len(locations),
            "playable_locations": role_counts.get("playable", 0),
            "special_locations": role_counts.get("special", 0),
            "transient_locations": role_counts.get("transient", 0),
            "null_locations": role_counts.get("null", 0),
            "direct_edges": connection_counter["direct"],
            "conditional_edges": connection_counter["conditional"],
            "random_edges": connection_counter["random"],
            "speak_edges": connection_counter["speak"],
            "special_edges": connection_counter["special"],
            "total_travel_rules": len(edges),
            "unresolved_rules": len(unresolved),
        },
    }


def save_graph(graph: dict[str, Any], path: Path) -> None:
    """Persist the graph IR as deterministic JSON."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, sort_keys=True, ensure_ascii=False)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    graph = build_graph(ir)
    print(json.dumps(graph["statistics"], indent=2))
