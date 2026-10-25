#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""
Canonical Room Inventory Generator & Deterministic Validator (CAR-CORE-002 / R1).

Produces a single, reproducible structural reference from authoritative sources:
  - 06_reconstruccion_drawio/Open_Adventure.yaml (historical source of truth)
  - 06_reconstruccion_drawio/tools/oa_chapters.py (editorial chapter partitioning)
  - 06_reconstruccion_drawio/output/Open_Adventure_World_V3.drawio (reconstructed geometry)

Emits versioned canonical manifests:
  - manifest.json: Root metadata, counts, source hashes, and artifact checksums
  - locations.json: 185 canonical locations in source order with roles, flags, geometry
  - travel.json: 623 travel records in source order with conditions and chapter crosses
  - objects.json: 70 static object entries with portability, multi-states, multi-locations
  - chapters.json: 11 canonical chapters with 100% coverage and zero fallback
  - structural_dependencies.json: Derived structural dependencies matrix (OBSERVED / INFERRED / PENDING)

Usage:
    python oa_canonical_inventory.py --check
    python oa_canonical_inventory.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import xml.etree.ElementTree as ET
import yaml

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent.parent
OA_DIR = REPO_ROOT / "06_reconstruccion_drawio"
YAML_PATH = OA_DIR / "Open_Adventure.yaml"
DRAWIO_PATH = OA_DIR / "output" / "Open_Adventure_World_V3.drawio"
DEFAULT_OUTPUT_DIR = TOOLS_DIR.parent / "canonical_inventory"

sys.path.insert(0, str(OA_DIR / "tools"))
from oa_chapters import CHAPTERS, PATTERN_ASSIGNMENTS, FOOF_TARGETS, _build_reverse_lookup  # noqa: E402
from oa_graph import SPECIAL_DESTINATION_PATTERNS, SPECIAL_IDS  # noqa: E402

SCHEMA_VERSION = 1
CUT_ID = "CAR-CORE-002-R1"

KNOWN_FLAGS = (
    "DEEP",
    "NOBACK",
    "LIT",
    "ALLALIKE",
    "FOREST",
    "NOARRR",
    "ALLDIFFERENT",
    "ABOVE",
    "FLUID",
    "OILY",
)


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    """Compute SHA-256 hex digest of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def dump_json(obj: Any) -> str:
    """Format JSON deterministically with sorted keys, 2 spaces indentation and LF."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def parse_drawio_geometry(drawio_path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Extract geometry and page metadata for all 185 locations from draw.io."""
    if not drawio_path.exists():
        raise FileNotFoundError(f"Draw.io file not found: {drawio_path}")

    tree = ET.parse(drawio_path)
    mxfile = tree.getroot()
    diagrams = list(mxfile.findall("diagram"))

    drawio_data: dict[str, dict[str, Any]] = {}
    page_names: dict[str, str] = {}

    for diag in diagrams:
        pid = diag.get("id")
        pname = diag.get("name")
        if not pid:
            continue
        page_names[pid] = pname or pid
        if pid == "INDEX":
            continue

        root = diag.find("mxGraphModel/root")
        if root is None:
            continue

        for obj in root.iter("object"):
            sid = obj.get("source_id")
            if not sid:
                continue
            if sid in drawio_data:
                raise ValueError(f"Duplicate source_id in draw.io: {sid}")

            geom = obj.find("mxCell/mxGeometry")
            if geom is None:
                raise ValueError(f"Missing mxGeometry for source_id {sid} on page {pid}")

            drawio_data[sid] = {
                "page_id": pid,
                "page_name": pname or pid,
                "cell_id": obj.get("id") or "",
                "x": float(geom.get("x", "0")),
                "y": float(geom.get("y", "0")),
                "width": float(geom.get("width", "0")),
                "height": float(geom.get("height", "0")),
                "label": obj.get("label", ""),
            }

    return drawio_data, page_names


def build_canonical_inventory(
    yaml_path: Path = YAML_PATH,
    drawio_path: Path = DRAWIO_PATH,
) -> dict[str, Any]:
    """Build the complete, verified canonical room inventory."""
    if not yaml_path.exists():
        raise FileNotFoundError(f"YAML source not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        ir = yaml.safe_load(f)

    # 1. Editorial chapters reverse lookup
    ch_lookup = _build_reverse_lookup(PATTERN_ASSIGNMENTS)
    for foof, dest in FOOF_TARGETS.items():
        if foof not in ch_lookup and dest in ch_lookup:
            ch_lookup[foof] = ch_lookup[dest]

    yaml_locations = ir.get("locations") or []
    if len(yaml_locations) != 185:
        raise ValueError(f"Expected 185 locations in source YAML, got {len(yaml_locations)}")

    for name, _ in yaml_locations:
        if name not in ch_lookup:
            raise ValueError(f"Location {name} unassigned to any canonical chapter")

    # 2. Draw.io geometry correspondence
    drawio_data, page_names = parse_drawio_geometry(drawio_path)
    if len(drawio_data) != 185:
        raise ValueError(f"Expected 185 draw.io locations, got {len(drawio_data)}")

    yaml_loc_names = {name for name, _ in yaml_locations}
    drawio_loc_names = set(drawio_data.keys())
    if yaml_loc_names != drawio_loc_names:
        missing = yaml_loc_names - drawio_loc_names
        extra = drawio_loc_names - yaml_loc_names
        raise ValueError(f"Draw.io mismatch: missing={missing}, extra={extra}")

    for name in yaml_loc_names:
        expected_ch = ch_lookup[name]
        actual_page = drawio_data[name]["page_id"]
        if expected_ch != actual_page:
            raise ValueError(
                f"Chapter mismatch for {name}: expected {expected_ch}, got page {actual_page}"
            )

    # 3. Object catalog source parsing & indexing
    yaml_objects = ir.get("objects") or []
    if len(yaml_objects) != 70:
        raise ValueError(f"Expected 70 objects in source YAML, got {len(yaml_objects)}")

    initial_objects_by_loc: dict[str, list[str]] = {name: [] for name, _ in yaml_locations}
    for obj_name, obj_spec in yaml_objects:
        if obj_name == "NO_OBJECT":
            continue
        obj_spec = obj_spec or {}
        raw_locs = obj_spec.get("locations")
        if raw_locs:
            loc_list = [raw_locs] if isinstance(raw_locs, str) else list(raw_locs)
            for loc_id in loc_list:
                if loc_id in initial_objects_by_loc:
                    initial_objects_by_loc[loc_id].append(obj_name)

    # 4. Canonical locations construction
    death_ids = set(SPECIAL_DESTINATION_PATTERNS["death"]) - {"LOC_NOWHERE"}
    locations_out: list[dict[str, Any]] = []
    role_counts = {"ordinary": 0, "special": 0, "transient": 0, "lethal": 0, "null": 0}
    flag_totals = {flag: 0 for flag in KNOWN_FLAGS}
    forced_locations_list: list[str] = []

    for idx, (name, spec) in enumerate(yaml_locations):
        spec = spec or {}
        rules = spec.get("travel") or []
        desc = spec.get("description") or {}
        raw_conds = spec.get("conditions") or {}

        # Flags computation
        flags = {}
        for flag in KNOWN_FLAGS:
            is_set = bool(raw_conds.get(flag, False))
            flags[flag] = is_set
            if is_set:
                flag_totals[flag] += 1

        # Historical forced motion derivation (init.c and CUT A contract)
        is_forced = bool(
            idx != 0
            and desc.get("long") is not None
            and bool(rules)
            and not rules[0].get("verbs")
        )
        if is_forced:
            forced_locations_list.append(name)

        is_null = (name == "LOC_NOWHERE")
        is_lethal = (name in death_ids)
        is_transient = bool(
            not is_null
            and not is_lethal
            and rules
            and all(not r.get("verbs") and (r.get("action") or [""])[0] == "goto" for r in rules)
            and name in {"LOC_CRACK", "LOC_CLIMBSTALK", "LOC_PARALLEL1", "LOC_PARALLEL2", "LOC_CLIFFTOP"}
        )
        is_special = bool(
            name in SPECIAL_IDS and not is_null and not is_lethal and not is_transient
        )
        is_ordinary = (not is_null and not is_lethal and not is_transient and not is_special)

        if is_null:
            role = "null"
        elif is_lethal:
            role = "lethal"
        elif is_transient:
            role = "transient"
        elif is_special:
            role = "special"
        else:
            role = "ordinary"

        role_counts[role] += 1

        long_val = desc.get("long")
        short_val = desc.get("short")
        has_long = (long_val is not None)
        has_short = (short_val is not None)

        hints_list: list[str] = []
        if "hints" in spec:
            for h in spec["hints"]:
                hints_list.append(h.get("name") if isinstance(h, dict) else str(h))

        locations_out.append({
            "id": name,
            "source_index": idx,
            "chapter_id": ch_lookup[name],
            "structural_role": role,
            "is_ordinary": is_ordinary,
            "is_special": is_special,
            "is_transient": is_transient,
            "is_forced": is_forced,
            "is_lethal": is_lethal,
            "is_null": is_null,
            "flags": flags,
            "raw_conditions": raw_conds,
            "has_long_description": has_long,
            "has_short_description": has_short,
            "long_description": long_val,
            "short_description": short_val,
            "maptag": desc.get("maptag"),
            "sound": spec.get("sound"),
            "loud": bool(spec.get("loud", False)),
            "outbound_travel_count": len(rules),
            "initial_objects": initial_objects_by_loc[name],
            "hints": hints_list,
            "drawio": drawio_data[name],
        })

    # 5. Canonical travel construction (623 records)
    travel_out: list[dict[str, Any]] = []
    global_idx = 0
    cond_counts = {"always": 0, "not": 0, "pct": 0, "carry": 0, "with": 0, "nodwarves": 0}
    action_counts = {"goto": 0, "speak": 0, "special": 0}
    cross_chapter_records: list[dict[str, Any]] = []

    for loc_idx, (name, spec) in enumerate(yaml_locations):
        rules = (spec or {}).get("travel") or []
        src_ch = ch_lookup[name]
        for rule_idx, rule in enumerate(rules):
            action = rule.get("action") or []
            if len(action) != 2:
                raise ValueError(f"Invalid travel action format in {name}: {action}")
            act_type, target = action[0], action[1]
            if act_type not in action_counts:
                raise ValueError(f"Unsupported action type: {act_type}")
            action_counts[act_type] += 1

            raw_cond = rule.get("cond")
            obj_deps: list[str] = []
            state_deps: list[dict[str, str]] = []
            sys_deps: list[str] = []

            if raw_cond is None:
                c_type = "always"
                norm_cond = {"type": "always"}
            elif raw_cond == ["nodwarves"]:
                c_type = "nodwarves"
                norm_cond = {"type": "no_dwarves"}
                sys_deps.append("nodwarves")
            elif raw_cond[0] == "pct":
                c_type = "pct"
                norm_cond = {"type": "pct", "percent": int(raw_cond[1])}
                sys_deps.append("probability_rng")
            elif raw_cond[0] == "carry":
                c_type = "carry"
                norm_cond = {"type": "carry", "object": str(raw_cond[1])}
                obj_deps.append(str(raw_cond[1]))
            elif raw_cond[0] == "with":
                c_type = "with"
                norm_cond = {"type": "with", "object": str(raw_cond[1])}
                obj_deps.append(str(raw_cond[1]))
            elif raw_cond[0] == "not":
                c_type = "not"
                norm_cond = {
                    "type": "not_state",
                    "object": str(raw_cond[1]),
                    "state": str(raw_cond[2]),
                }
                obj_deps.append(str(raw_cond[1]))
                state_deps.append({"object": str(raw_cond[1]), "state": str(raw_cond[2])})
            else:
                raise ValueError(f"Unknown condition in {name}: {raw_cond}")

            cond_counts[c_type] += 1

            if act_type == "goto":
                if target not in yaml_loc_names:
                    raise ValueError(f"Unresolved goto destination: {target} from {name}")
                resolution = "location"
                dest_loc: str | None = target
                dest_ch: str | None = ch_lookup[target]
                is_cross = (dest_ch != src_ch)
            elif act_type == "speak":
                resolution = "message"
                dest_loc = None
                dest_ch = None
                is_cross = False
            elif act_type == "special":
                resolution = "special_handler"
                dest_loc = None
                dest_ch = None
                is_cross = False
                sys_deps.append(f"special_handler_{target}")
            else:
                raise ValueError(f"Unknown action type: {act_type}")

            record = {
                "global_travel_index": global_idx,
                "source_location_id": name,
                "source_location_index": loc_idx,
                "source_rule_index": rule_idx,
                "verbs": list(rule.get("verbs") or []),
                "action_type": act_type,
                "target": target,
                "target_resolution": resolution,
                "condition_type": c_type,
                "source_condition": raw_cond,
                "condition": norm_cond,
                "destination_location_id": dest_loc,
                "destination_chapter_id": dest_ch,
                "is_cross_chapter": is_cross,
                "object_dependencies": obj_deps,
                "state_dependencies": state_deps,
                "system_dependencies": sys_deps,
            }
            travel_out.append(record)
            if is_cross:
                cross_chapter_records.append(record)
            global_idx += 1

    if global_idx != 623:
        raise ValueError(f"Expected 623 travel records, got {global_idx}")

    # 6. Canonical objects catalog (70 entries)
    cond_refs_by_obj: dict[str, list[dict[str, Any]]] = {n: [] for n, _ in yaml_objects}
    for tr in travel_out:
        for od in tr["object_dependencies"]:
            if od in cond_refs_by_obj:
                cond_refs_by_obj[od].append({
                    "global_travel_index": tr["global_travel_index"],
                    "source_location_id": tr["source_location_id"],
                    "condition": tr["source_condition"],
                })

    objects_out: list[dict[str, Any]] = []
    portable_count = 0
    immobile_count = 0
    sentinel_count = 0
    multi_loc_count = 0
    multi_state_count = 0
    absent_count = 0
    treasure_count = 0

    for idx, (name, spec) in enumerate(yaml_objects):
        if name == "NO_OBJECT":
            sentinel_count += 1
            absent_count += 1
            objects_out.append({
                "id": "NO_OBJECT",
                "source_index": idx,
                "is_sentinel": True,
                "words": [],
                "inventory_label": None,
                "immovable": False,
                "is_portable": False,
                "treasure": False,
                "raw_locations": None,
                "primary_location": None,
                "fixed_locations": [],
                "all_initial_locations": [],
                "has_multiple_locations": False,
                "is_initially_absent": True,
                "states": [],
                "has_multiple_states": False,
                "initial_state": None,
                "descriptions": [],
                "changes": [],
                "texts": [],
                "sounds": [],
                "referenced_in_travel_conditions": [],
            })
            continue

        spec = spec or {}
        is_immobile = bool(spec.get("immovable", False))
        if is_immobile:
            immobile_count += 1
        else:
            portable_count += 1

        is_treasure = bool(spec.get("treasure", False))
        if is_treasure:
            treasure_count += 1

        raw_locs = spec.get("locations")
        if raw_locs is None:
            all_locs: list[str] = []
            primary_loc = None
            fixed_locs: list[str] = []
            is_absent = True
            has_multi_loc = False
        elif isinstance(raw_locs, list):
            all_locs = list(raw_locs)
            primary_loc = all_locs[0] if all_locs else None
            fixed_locs = all_locs[1:]
            has_multi_loc = (len(all_locs) > 1)
            is_absent = (
                all_locs == ["LOC_NOWHERE", "LOC_NOWHERE"]
                or all_locs == ["LOC_NOWHERE"]
                or len(all_locs) == 0
            )
        else:
            all_locs = [str(raw_locs)]
            primary_loc = str(raw_locs)
            fixed_locs = []
            has_multi_loc = False
            is_absent = (primary_loc == "LOC_NOWHERE")

        if has_multi_loc:
            multi_loc_count += 1
        if is_absent:
            absent_count += 1

        states = [str(s) for s in (spec.get("states") or [])]
        has_multi_state = (len(states) > 1)
        if has_multi_state:
            multi_state_count += 1
        init_state = states[0] if states else None

        objects_out.append({
            "id": name,
            "source_index": idx,
            "is_sentinel": False,
            "words": [str(w) for w in (spec.get("words") or [])],
            "inventory_label": spec.get("inventory"),
            "immovable": is_immobile,
            "is_portable": not is_immobile,
            "treasure": is_treasure,
            "raw_locations": raw_locs,
            "primary_location": primary_loc,
            "fixed_locations": fixed_locs,
            "all_initial_locations": all_locs,
            "has_multiple_locations": has_multi_loc,
            "is_initially_absent": is_absent,
            "states": states,
            "has_multiple_states": has_multi_state,
            "initial_state": init_state,
            "descriptions": [str(d) for d in (spec.get("descriptions") or [])],
            "changes": [str(c) for c in (spec.get("changes") or [])],
            "texts": [str(t) for t in (spec.get("texts") or [])],
            "sounds": [str(s) for s in (spec.get("sounds") or [])],
            "referenced_in_travel_conditions": cond_refs_by_obj[name],
        })

    # 7. Canonical chapters (11)
    ch_members: dict[str, list[str]] = {cid: [] for cid in CHAPTERS}
    for loc in locations_out:
        ch_members[loc["chapter_id"]].append(loc["id"])

    chapters_out: list[dict[str, Any]] = []
    for order, (cid, meta) in enumerate(CHAPTERS.items(), start=1):
        chapters_out.append({
            "id": cid,
            "order": order,
            "title": meta["title"],
            "description": meta["description"],
            "member_count": len(ch_members[cid]),
            "members": sorted(ch_members[cid]),
            "drawio_page_id": cid,
            "drawio_page_name": page_names.get(cid, meta["title"]),
        })

    # 8. Structural dependencies matrix
    special_travel_rules = [tr for tr in travel_out if tr["action_type"] == "special"]
    obj_travel_deps = [
        {
            "object_id": obj["id"],
            "reference_count": len(obj["referenced_in_travel_conditions"]),
            "references": obj["referenced_in_travel_conditions"],
        }
        for obj in objects_out
        if obj["referenced_in_travel_conditions"]
    ]

    dwarflocs = list(ir.get("dwarflocs") or [])
    deep_locations = [loc["id"] for loc in locations_out if loc["flags"]["DEEP"]]
    noarrr_locations = [loc["id"] for loc in locations_out if loc["flags"]["NOARRR"]]
    nodwarves_rules = [tr for tr in travel_out if tr["condition_type"] == "nodwarves"]

    structural_deps = {
        "schema_version": SCHEMA_VERSION,
        "classification_guide": {
            "OBSERVED": "Directly attested in authoritative source files (YAML, draw.io).",
            "INFERRED": "Technical deduction supported by historical source rules.",
            "PENDING": "Execution semantics documented but awaiting future cut implementation.",
        },
        "cross_chapter_transitions": {
            "status": "OBSERVED",
            "total_count": len(cross_chapter_records),
            "records": [
                {
                    "global_travel_index": tr["global_travel_index"],
                    "source_location_id": tr["source_location_id"],
                    "source_chapter_id": ch_lookup[tr["source_location_id"]],
                    "destination_location_id": tr["destination_location_id"],
                    "destination_chapter_id": tr["destination_chapter_id"],
                    "verbs": tr["verbs"],
                    "condition_type": tr["condition_type"],
                    "source_condition": tr["source_condition"],
                }
                for tr in cross_chapter_records
            ],
        },
        "object_travel_dependencies": {
            "status": "OBSERVED",
            "distinct_objects_count": len(obj_travel_deps),
            "distinct_objects": sorted(od["object_id"] for od in obj_travel_deps),
            "total_conditioned_rules_referencing_objects": sum(
                od["reference_count"] for od in obj_travel_deps
            ),
            "dependencies": obj_travel_deps,
        },
        "special_travel_destinations": {
            "status": "OBSERVED_AND_PENDING",
            "total_count": len(special_travel_rules),
            "rules": [
                {
                    "global_travel_index": tr["global_travel_index"],
                    "source_location_id": tr["source_location_id"],
                    "special_handler_id": tr["target"],
                    "verbs": tr["verbs"],
                    "condition": tr["source_condition"],
                    "status": (
                        "INFERRED / OBSERVED"
                        if tr["target"] in (1, 2)
                        else "PENDING / NOT IMPLEMENTED (troll bridge crossing)"
                    ),
                }
                for tr in special_travel_rules
            ],
        },
        "forced_locations": {
            "status": "INFERRED",
            "total_count": len(forced_locations_list),
            "derivation_rule": "source_index != 0 and long_description is not None and travel rules[0].verbs == []",
            "locations": forced_locations_list,
        },
        "lethal_locations": {
            "status": "INFERRED",
            "total_count": len(death_ids),
            "locations": sorted(death_ids),
            "null_sentinel_location": "LOC_NOWHERE",
            "death_obituaries_count": len(ir.get("obituaries") or []),
        },
        "historical_flags": {
            "status": "OBSERVED",
            "totals": flag_totals,
            "locations_by_flag": {
                flag: [loc["id"] for loc in locations_out if loc["flags"][flag]]
                for flag in KNOWN_FLAGS
            },
        },
        "object_state_dependencies": {
            "status": "OBSERVED",
            "multi_state_objects_count": multi_state_count,
            "multi_state_objects": [obj["id"] for obj in objects_out if obj["has_multiple_states"]],
            "state_conditioned_travel_rules_count": cond_counts["not"],
        },
        "actor_relevant_data": {
            "status": "OBSERVED",
            "dwarf_start_locations": dwarflocs,
            "deep_locations_count": len(deep_locations),
            "noarrr_locations_count": len(noarrr_locations),
            "nodwarves_rules_count": len(nodwarves_rules),
            "nodwarves_rules": [
                {
                    "global_travel_index": tr["global_travel_index"],
                    "source_location_id": tr["source_location_id"],
                    "destination_location_id": tr["destination_location_id"],
                    "verbs": tr["verbs"],
                }
                for tr in nodwarves_rules
            ],
        },
        "runtime_pending_systems": {
            "status": "PENDING",
            "documented_systems": [
                {
                    "system": "special_3_troll_bridge",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "Historical troll bridge crossing from LOC_SWCHASM and LOC_NECHASM.",
                },
                {
                    "system": "dwarf_and_pirate_actors",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "Historical dwarf movement (dwarfmove) and pirate encounter (spotted_by_pirate).",
                },
                {
                    "system": "cave_closing_and_endgame",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "Cave closing checks (closecheck) and repository room relocation.",
                },
                {
                    "system": "global_treasure_scoring",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "End-of-game score calculation based on all 20 historical treasures.",
                },
                {
                    "system": "dynamic_hints",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "Dynamic turn thresholds and conditional question triggers.",
                },
                {
                    "system": "darkness_lamp_full_lifecycle",
                    "status": "PENDING / NOT AUTHORIZED",
                    "description": "Persistent dark room simulation across chapters 02-11.",
                },
            ],
        },
    }

    # Consolidated manifests dict
    locations_payload = {
        "schema_version": SCHEMA_VERSION,
        "location_count": len(locations_out),
        "role_counts": role_counts,
        "flag_totals": flag_totals,
        "forced_locations_count": len(forced_locations_list),
        "locations": locations_out,
    }

    travel_payload = {
        "schema_version": SCHEMA_VERSION,
        "travel_record_count": len(travel_out),
        "condition_counts": cond_counts,
        "action_type_counts": action_counts,
        "cross_chapter_count": len(cross_chapter_records),
        "records": travel_out,
    }

    objects_payload = {
        "schema_version": SCHEMA_VERSION,
        "object_count": len(objects_out),
        "counts": {
            "portable": portable_count,
            "immobile": immobile_count,
            "sentinel": sentinel_count,
            "multiple_locations": multi_loc_count,
            "multiple_states": multi_state_count,
            "initially_absent_or_nowhere": absent_count,
            "treasures": treasure_count,
        },
        "objects": objects_out,
    }

    chapters_payload = {
        "schema_version": SCHEMA_VERSION,
        "chapter_count": len(chapters_out),
        "total_locations": len(locations_out),
        "chapters": chapters_out,
    }

    # Root manifest
    try:
        yaml_rel = str(yaml_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        yaml_rel = str(yaml_path).replace("\\", "/")

    try:
        drawio_rel = str(drawio_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        drawio_rel = str(drawio_path).replace("\\", "/")

    manifest_payload = {
        "cut_id": CUT_ID,
        "title": "Canonical Room Inventory",
        "document_status": "CLOSED / PASS",
        "schema_version": SCHEMA_VERSION,
        "sources": {
            "yaml": {
                "path": yaml_rel,
                "sha256": sha256_file(yaml_path),
            },
            "drawio": {
                "path": drawio_rel,
                "sha256": sha256_file(drawio_path),
            },
        },
        "canonical_counts": {
            "locations": len(locations_out),
            "travel_records": len(travel_out),
            "objects": len(objects_out),
            "chapters": len(chapters_out),
            "portable_objects": portable_count,
            "immobile_objects": immobile_count,
            "sentinel_objects": sentinel_count,
            "multiple_location_objects": multi_loc_count,
            "multiple_state_objects": multi_state_count,
            "absent_or_nowhere_objects": absent_count,
            "treasure_objects": treasure_count,
            "cross_chapter_travel_records": len(cross_chapter_records),
            "condition_counts": cond_counts,
            "action_type_counts": action_counts,
            "structural_role_counts": role_counts,
            "forced_locations": len(forced_locations_list),
        },
        "artifacts": {
            "locations.json": {
                "record_count": len(locations_out),
                "sha256": sha256_text(dump_json(locations_payload)),
            },
            "travel.json": {
                "record_count": len(travel_out),
                "sha256": sha256_text(dump_json(travel_payload)),
            },
            "objects.json": {
                "record_count": len(objects_out),
                "sha256": sha256_text(dump_json(objects_payload)),
            },
            "chapters.json": {
                "record_count": len(chapters_out),
                "sha256": sha256_text(dump_json(chapters_payload)),
            },
            "structural_dependencies.json": {
                "record_count": len(cross_chapter_records),
                "sha256": sha256_text(dump_json(structural_deps)),
            },
        },
    }

    return {
        "manifest": manifest_payload,
        "locations": locations_payload,
        "travel": travel_payload,
        "objects": objects_payload,
        "chapters": chapters_payload,
        "structural_dependencies": structural_deps,
    }


def export_canonical_inventory(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    yaml_path: Path = YAML_PATH,
    drawio_path: Path = DRAWIO_PATH,
) -> dict[str, Path]:
    """Export the canonical inventory into versioned JSON documents."""
    data = build_canonical_inventory(yaml_path=yaml_path, drawio_path=drawio_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    files_written = {}
    for filename, payload in (
        ("manifest.json", data["manifest"]),
        ("locations.json", data["locations"]),
        ("travel.json", data["travel"]),
        ("objects.json", data["objects"]),
        ("chapters.json", data["chapters"]),
        ("structural_dependencies.json", data["structural_dependencies"]),
    ):
        target_path = output_dir / filename
        formatted = dump_json(payload)
        with open(target_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(formatted)
        files_written[filename] = target_path

    return files_written


def verify_canonical_inventory(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    yaml_path: Path = YAML_PATH,
    drawio_path: Path = DRAWIO_PATH,
) -> tuple[bool, list[str]]:
    """Verify that committed files match regenerated data byte-for-byte."""
    errors: list[str] = []
    try:
        data = build_canonical_inventory(yaml_path=yaml_path, drawio_path=drawio_path)
    except Exception as exc:
        return False, [f"Failed to generate in-memory inventory: {exc}"]

    expected_files = (
        ("manifest.json", data["manifest"]),
        ("locations.json", data["locations"]),
        ("travel.json", data["travel"]),
        ("objects.json", data["objects"]),
        ("chapters.json", data["chapters"]),
        ("structural_dependencies.json", data["structural_dependencies"]),
    )

    for filename, payload in expected_files:
        target_path = output_dir / filename
        if not target_path.exists():
            errors.append(f"Missing artifact: {target_path}")
            continue

        disk_bytes = target_path.read_bytes()
        expected_text = dump_json(payload)
        expected_bytes = expected_text.encode("utf-8")

        if disk_bytes != expected_bytes:
            errors.append(
                f"Mismatch in {filename}: disk sha256={hashlib.sha256(disk_bytes).hexdigest()[:16]}, "
                f"expected={hashlib.sha256(expected_bytes).hexdigest()[:16]}"
            )

    return (len(errors) == 0, errors)


def main() -> None:
    parser = argparse.ArgumentParser(description="Canonical Room Inventory Manager")
    parser.add_argument("--check", action="store_true", help="Verify committed artifacts match source")
    parser.add_argument("--write", action="store_true", help="Generate and overwrite committed artifacts")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    if args.write:
        written = export_canonical_inventory(output_dir=args.output_dir)
        print(f"PASS: exported {len(written)} canonical inventory artifacts to {args.output_dir}")
        for name, p in written.items():
            print(f"  - {name} ({p.stat().st_size} bytes)")
        return

    # Default to check
    ok, errors = verify_canonical_inventory(output_dir=args.output_dir)
    if not ok:
        print("FAIL: canonical inventory verification failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("PASS: all canonical inventory artifacts match regenerated authoritative source data.")


if __name__ == "__main__":
    main()
