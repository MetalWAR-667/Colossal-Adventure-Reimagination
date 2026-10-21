#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""
Exporter: Open Adventure YAML -> Godot 4 chapter dataset.

Reads the canonical dungeon description (Open Adventure `adventure.yaml`,
structurally equivalent to `06_reconstruccion_drawio/Open_Adventure.yaml`
after normalising line endings) and
emits a single deterministic JSON document consumed by the Godot project.

The chapter partition is the editorial one already produced by
`06_reconstruccion_drawio/tools/oa_chapters.py`; it is imported, never
re-invented.

Positions for the in-game map are read from the diagrams.net artifact
`06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio` (page
`01 - Surface World`), so the in-game map and the published diagram share one
layout.  Connectivity is NOT read from the diagram: it comes from the source
YAML, which stays the only authority for travel rules.

Usage:
    python tools/oa_export_godot.py [--check]

`--check` regenerates into memory and compares against the committed dataset
without writing, so it can be used as a verification step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent.parent
OA_DIR = ROOT / "06_reconstruccion_drawio"
YAML_CANDIDATES = [
    OA_DIR / "Open_Adventure.yaml",
    ROOT / "codigo_fuente_open_adventure" / "adventure.yaml",
]
DRAWIO_PATH = OA_DIR / "output" / "Open_Adventure_World_V3.drawio"
OUT_PATH = TOOLS_DIR.parent / "godot" / "data" / "chapter_01_surface.json"
CHAPTER_ID = "CH_SURFACE"
SCHEMA_VERSION = 1

sys.path.insert(0, str(OA_DIR / "tools"))
from oa_chapters import CHAPTERS, FOOF_TARGETS, PATTERN_ASSIGNMENTS  # noqa: E402


# --------------------------------------------------------------------------
# source loading
# --------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml_source() -> tuple[dict[str, Any], Path, list[dict[str, str]]]:
    """Load the dungeon YAML, checking that every candidate copy agrees."""
    sources: list[dict[str, str]] = []
    parsed: list[tuple[Path, Any]] = []
    for candidate in YAML_CANDIDATES:
        if not candidate.exists():
            continue
        digest = sha256(candidate)
        sources.append({"path": str(candidate.relative_to(ROOT)).replace("\\", "/"), "sha256": digest})
        parsed.append((candidate, yaml.safe_load(candidate.read_text(encoding="utf-8"))))

    if not parsed:
        raise SystemExit("No Open Adventure YAML found in the expected locations.")

    reference_path, reference = parsed[0]
    for other_path, other in parsed[1:]:
        if other != reference:
            raise SystemExit(
                "YAML copies disagree; refusing to pick a winner:\n"
                f"  {reference_path}\n  {other_path}"
            )
    return reference, reference_path, sources


# --------------------------------------------------------------------------
# chapter membership (editorial, imported from the 06 pipeline)
# --------------------------------------------------------------------------

def chapter_members(chapter_id: str) -> list[str]:
    members = set(PATTERN_ASSIGNMENTS[chapter_id])
    for foof_id, dest_id in FOOF_TARGETS.items():
        if dest_id in members:
            members.add(foof_id)
    return sorted(members)


# --------------------------------------------------------------------------
# conversion helpers
# --------------------------------------------------------------------------

def parse_cond(cond: Any) -> dict[str, Any]:
    """Normalise a YAML travel condition into a typed record."""
    if cond is None:
        return {"type": "always"}
    kind = str(cond[0])
    if kind == "not":
        return {"type": "not_state", "object": str(cond[1]), "state": str(cond[2])}
    if kind == "pct":
        return {"type": "pct", "percent": int(cond[1])}
    if kind == "carry":
        return {"type": "carry", "object": str(cond[1])}
    if kind == "with":
        return {"type": "with", "object": str(cond[1])}
    if kind == "nodwarves":
        return {"type": "no_dwarves"}
    raise ValueError(f"Unsupported travel condition: {cond!r}")


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def normalize_name(name: Any) -> str:
    """YAML 1.1 turns the action name `NO` into the boolean ``False``."""
    if name is False:
        return "NO"
    if name is True:
        return "YES"
    return str(name)


def build_verb_tables(ir: dict[str, Any]) -> dict[str, Any]:
    """Collect the parser vocabulary, preserving the source's 5-char stems."""
    motions: dict[str, str] = {}
    for name, spec in ir["motions"]:
        for word in as_list(spec.get("words")):
            motions[word] = name
    actions: dict[str, str] = {}
    for name, spec in ir["actions"]:
        action_name = normalize_name(name)
        for word in as_list(spec.get("words")):
            actions.setdefault(word, action_name)
    return {
        "motions": dict(sorted(motions.items())),
        "actions": dict(sorted(actions.items())),
        "action_messages": {
            normalize_name(name): spec.get("message")
            for name, spec in ir["actions"]
            if spec.get("message")
        },
        "motion_messages": {},
    }


def build_objects(ir: dict[str, Any], member_ids: set[str]) -> dict[str, Any]:
    objects: dict[str, Any] = {}
    for index, (name, spec) in enumerate(ir["objects"]):
        locations = as_list(spec.get("locations"))
        if not any(loc in member_ids for loc in locations):
            continue
        states = as_list(spec.get("states"))
        objects[name] = {
            "id": name,
            "source_index": index,
            "words": as_list(spec.get("words")),
            "inventory_label": spec.get("inventory"),
            "descriptions": as_list(spec.get("descriptions")),
            "changes": as_list(spec.get("changes")),
            "states": states,
            "initial_state": states[0] if states else "",
            "locations": locations,
            "immovable": bool(spec.get("immovable", False)),
            "treasure": bool(spec.get("treasure", False)),
        }
    return dict(sorted(objects.items()))


def build_locations(ir: dict[str, Any], member_ids: set[str]) -> dict[str, Any]:
    locations: dict[str, Any] = {}
    for name, spec in ir["locations"]:
        if name not in member_ids:
            continue
        description = spec.get("description") or {}
        travel: list[dict[str, Any]] = []
        for rule in spec.get("travel") or []:
            action = list(rule.get("action") or [])
            action_type = action[0] if action else "goto"
            target = action[1] if len(action) > 1 else ""
            travel.append(
                {
                    "verbs": as_list(rule.get("verbs")),
                    "action_type": action_type,
                    "target": target,
                    "cond": parse_cond(rule.get("cond")),
                    "target_in_chapter": target in member_ids,
                }
            )
        locations[name] = {
            "id": name,
            "chapter_id": CHAPTER_ID,
            "description_en": description.get("long") or "",
            "short_en": description.get("short") or "",
            "maptag": description.get("maptag") or "",
            "conditions": {str(k): bool(v) for k, v in (spec.get("conditions") or {}).items()},
            "sound": spec.get("sound"),
            "travel": travel,
        }
    return dict(sorted(locations.items()))


def build_frontier(locations: dict[str, Any], member_ids: set[str]) -> dict[str, list[str]]:
    frontier: dict[str, set[str]] = {}
    for loc_id, loc in locations.items():
        for rule in loc["travel"]:
            target = rule["target"]
            if rule["action_type"] != "goto" or not target or target in member_ids:
                continue
            frontier.setdefault(target, set()).add(loc_id)
    return {target: sorted(sources) for target, sources in sorted(frontier.items())}


# --------------------------------------------------------------------------
# diagrams.net map extraction
# --------------------------------------------------------------------------

def extract_drawio_map(drawio_path: Path, member_ids: set[str]) -> dict[str, Any]:
    """Read node geometry for the chapter page of the diagrams.net artifact."""
    if not drawio_path.exists():
        return {"source": None, "nodes": [], "page_width": 0, "page_height": 0}

    tree = ET.parse(drawio_path)
    root = tree.getroot()
    page = None
    for diagram in root.findall("diagram"):
        if diagram.get("id") == CHAPTER_ID:
            page = diagram
            break
    if page is None:
        raise SystemExit(f"Chapter page {CHAPTER_ID} not found in {drawio_path}")

    model = page.find("mxGraphModel")
    assert model is not None
    nodes: list[dict[str, Any]] = []
    for cell in model.find("root"):
        source_id = cell.get("source_id")
        if not source_id or source_id not in member_ids:
            continue
        geometry = cell.find(".//mxGeometry")
        if geometry is None:
            continue
        nodes.append(
            {
                "id": source_id,
                "x": float(geometry.get("x", "0")),
                "y": float(geometry.get("y", "0")),
                "w": float(geometry.get("width", "0")),
                "h": float(geometry.get("height", "0")),
                "label": cell.get("label", ""),
            }
        )
    nodes.sort(key=lambda n: (n["y"], n["x"]))
    return {
        "source": str(drawio_path.relative_to(ROOT)).replace("\\", "/"),
        "page_width": float(model.get("pageWidth", "0")),
        "page_height": float(model.get("pageHeight", "0")),
        "nodes": nodes,
    }


def build_edges(locations: dict[str, Any], node_ids: set[str]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for loc_id, loc in locations.items():
        for rule in loc["travel"]:
            if rule["action_type"] != "goto" or rule["target"] not in node_ids:
                continue
            edges.append(
                {
                    "from": loc_id,
                    "to": rule["target"],
                    "verbs": list(rule["verbs"]),
                    "conditional": rule["cond"]["type"] != "always",
                }
            )
    edges.sort(key=lambda e: (e["from"], e["to"]))
    return edges


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def build_dataset() -> dict[str, Any]:
    ir, yaml_path, yaml_sources = load_yaml_source()
    members = chapter_members(CHAPTER_ID)
    member_ids = set(members)

    locations = build_locations(ir, member_ids)
    if set(locations) != member_ids:
        missing = sorted(member_ids - set(locations))
        raise SystemExit(f"Chapter members missing from the YAML: {missing}")

    map_data = extract_drawio_map(DRAWIO_PATH, member_ids)
    node_ids = {node["id"] for node in map_data["nodes"]}
    edges = build_edges(locations, node_ids)

    messages = {
        name: spec
        for name, spec in ir["arbitrary_messages"]
        if isinstance(spec, str)
    }

    dataset = {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "chapter_id": CHAPTER_ID,
            "chapter_title": CHAPTERS[CHAPTER_ID]["title"],
            "chapter_description": CHAPTERS[CHAPTER_ID]["description"],
            "chapter_member_count": len(members),
            "editorial_note": (
                "Chapter partition is editorial (06_reconstruccion_drawio/tools/oa_chapters.py). "
                "Travel rules, conditions and texts come from the Open Adventure YAML."
            ),
            "source_yaml": [
                {"path": src["path"], "sha256": src["sha256"]} for src in yaml_sources
            ],
            "primary_yaml_path": str(yaml_path.relative_to(ROOT)).replace("\\", "/"),
            "drawio_map_source": map_data["source"],
            "generator": "07_godot_open_adventure/tools/oa_export_godot.py",
        },
        "locations": locations,
        "objects": build_objects(ir, member_ids),
        "messages": messages,
        "classes": [
            {"threshold": int(spec.get("threshold", 0)), "message": spec.get("message")}
            for spec in ir["classes"]
        ],
        "num_deaths": len(ir["obituaries"]),
        "chest_index": next(
            (index for index, (name, _) in enumerate(ir["objects"]) if name == "CHEST"), -1
        ),
        "verbs": build_verb_tables(ir),
        "frontier": build_frontier(locations, member_ids),
        "map": {
            "page_width": map_data["page_width"],
            "page_height": map_data["page_height"],
            "nodes": map_data["nodes"],
            "edges": edges,
        },
    }
    return dataset


def validate(dataset: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    locations = dataset["locations"]
    for loc_id, loc in locations.items():
        for rule in loc["travel"]:
            target = rule["target"]
            if rule["action_type"] == "goto" and target not in locations:
                # Out-of-chapter targets are legitimate; they are listed as frontier.
                if target not in dataset["frontier"]:
                    problems.append(f"{loc_id}: travel target {target} is neither member nor frontier")
    if dataset["meta"]["chapter_member_count"] != len(locations):
        problems.append("chapter member count mismatch")
    node_ids = {node["id"] for node in dataset["map"]["nodes"]}
    if node_ids != set(locations):
        problems.append("drawio node set does not match chapter membership")
    return problems


def dump(dataset: dict[str, Any]) -> str:
    return json.dumps(dataset, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the committed dataset instead of writing")
    args = parser.parse_args()

    dataset = build_dataset()
    problems = validate(dataset)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    payload = dump(dataset)
    if args.check:
        if not OUT_PATH.exists():
            print(f"ERROR: {OUT_PATH} does not exist", file=sys.stderr)
            return 1
        current = OUT_PATH.read_text(encoding="utf-8")
        if current != payload:
            print("ERROR: committed dataset differs from regenerated output", file=sys.stderr)
            return 1
        print(f"OK: {OUT_PATH.relative_to(ROOT)} matches the regenerated dataset")
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    print(f"  locations : {len(dataset['locations'])}")
    print(f"  objects   : {len(dataset['objects'])}")
    print(f"  map nodes : {len(dataset['map']['nodes'])}")
    print(f"  map edges : {len(dataset['map']['edges'])}")
    print(f"  frontier  : {len(dataset['frontier'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
