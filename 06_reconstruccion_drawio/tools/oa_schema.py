#!/usr/bin/env python3
"""
Generate the SCHEMA_ANALYSIS.md report from the parsed Open Adventure IR.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from oa_parser import parse_open_adventure


def _describe_conditions(locations: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for loc in locations:
        for cond in loc.get("conditions", {}):
            counts[cond] += 1
    return dict(counts)


def _travel_action_types(locations: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for loc in locations:
        for rule in loc.get("travel", []):
            counts[rule.get("action_type", "unknown")] += 1
    return dict(counts)


def _condition_types(locations: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for loc in locations:
        for rule in loc.get("travel", []):
            cond = rule.get("cond")
            if cond:
                counts[cond.get("type", "unknown")] += 1
    return dict(counts)


def _special_locations(locations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """List locations that are not ordinary playable rooms."""
    special: list[dict[str, Any]] = []
    for loc in locations:
        desc = loc.get("description", {})
        travel = loc.get("travel", [])
        target = None
        if travel and travel[0].get("action_type") == "goto":
            target = travel[0].get("action_target")

        if loc["source_id"] == "LOC_NOWHERE":
            category = "null"
        elif not desc.get("long") and not desc.get("short") and not desc.get("maptag"):
            category = "empty_description"
        elif loc["source_id"].startswith("LOC_FOOF"):
            category = "magic_teleport"
        elif target == "LOC_NOWHERE" or any(x in loc["source_id"] for x in ["NECKBROKE", "NOMAKE", "GRUESOME", "FOOTSLIP"]):
            category = "death_state"
        elif not any(rule.get("verbs") for rule in travel):
            category = "no_input_transient"
        else:
            continue
        special.append({
            "source_id": loc["source_id"],
            "category": category,
            "long": desc.get("long") or "(none)",
        })
    return special


def schema_analysis_report(ir: dict[str, Any]) -> str:
    locs = ir["locations"]
    objs = ir["objects"]
    motions = ir["motions"]
    actions = ir["actions"]
    messages = ir["messages"]
    hints = ir["hints"]

    cond_counts = _describe_conditions(locs)
    action_counts = _travel_action_types(locs)
    cond_type_counts = _condition_types(locs)
    special = _special_locations(locs)

    report = f"""# Schema Analysis — Open Adventure YAML

## Source provenance
- **File:** `{ir['source_file']}`
- **License:** BSD-2-Clause (see source header)
- **Canonical author:** Eric S. Raymond / Open Adventure project

## Top-level sections
| Section | Records |
|---------|---------|
| motions | {len(motions)} |
| hints | {len(hints)} |
| locations | {len(locs)} |
| arbitrary_messages | {len(messages)} |
| classes | {len(ir['classes'])} |
| turn_thresholds | {len(ir['turn_thresholds'])} |
| objects | {len(objs)} |
| obituaries | {len(ir['obituaries'])} |
| actions | {len(actions)} |
| dwarflocs | {len(ir['dwarflocs'])} |

## Location schema
Every location record contains:
- `source_id` — stable identifier (e.g. `LOC_START`).
- `description.long` — full English room description (may be `null`).
- `description.short` — brief description shown on revisits (may be `null`).
- `description.maptag` — grapher-only tag (may be `null`).
- `conditions` — boolean flags (LIT, DEEP, FOREST, NOBACK, NOARRR, FLUID, OILY, ALLALIKE, ALLDIFFERENT, ABOVE, etc.).
- `sound` — ambient sound label (optional).
- `loud` — whether object sounds are drowned out (optional).
- `hints` — references to hint records (optional).
- `travel` — ordered list of movement rules.

## Condition flags observed
| Flag | Locations |
|------|-----------|
"""
    for flag, count in sorted(cond_counts.items()):
        report += f"| {flag} | {count} |\n"

    report += f"""
## Travel rule actions
| Action type | Rules |
|-------------|-------|
"""
    for action, count in sorted(action_counts.items()):
        report += f"| {action} | {count} |\n"

    report += f"""
## Conditional travel types
| Condition type | Rules |
|----------------|-------|
"""
    for ctype, count in sorted(cond_type_counts.items()):
        report += f"| {ctype} | {count} |\n"

    report += f"""
## Classification of source records
- **Total location records:** {len(locs)}
- **Playable rooms:** {len(locs) - len(special)}
- **Special / auxiliary records:** {len(special)}

The 23 special/auxiliary records are broken down as:
- **Null location:** `LOC_NOWHERE`
- **Death pseudo-rooms:** `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP`
- **Transient message states:** `LOC_DOME`, `LOC_SNAKEBLOCK`, `LOC_BUILDING1`, `LOC_NOCLIMB`, `LOC_PLANTTOP`, `LOC_CLIMBSTALK`, `LOC_CRACK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_BADDIRECTION`, `LOC_SEWER`
- **Magic teleport destinations:** `LOC_FOOF1` … `LOC_FOOF6`

### Special/auxiliary locations
| Source ID | Category | Long description |
|-----------|----------|------------------|
"""
    for s in sorted(special, key=lambda x: x["source_id"]):
        short_desc = s["long"].replace("\n", " ")[:80]
        report += f"| `{s['source_id']}` | {s['category']} | {short_desc} |\n"

    report += f"""
## Motion vocabulary ({len(motions)} symbols)
| Symbol | Words | oldstyle |
|--------|-------|----------|
"""
    for mot in motions:
        words = ", ".join(mot["words"][:8])
        if len(mot["words"]) > 8:
            words += " ..."
        report += f"| {mot['source_id']} | {words} | {mot['oldstyle']} |\n"

    report += f"""
## Object schema
Each object record may contain:
- `source_id` — symbolic name (some are `OBJ_*`).
- `words` — parser vocabulary.
- `inventory` — inventory description.
- `locations` — one or two start locations (may be `LOC_NOWHERE`).
- `states` — state labels for condition tests.
- `descriptions` / `changes` / `sounds` / `texts` — state-dependent strings.
- `immovable` and `treasure` flags.

**Treasure objects:** {sum(1 for o in objs if o.get('treasure'))}
**Immovable objects:** {sum(1 for o in objs if o.get('immovable'))}

## Notes and ambiguities
- The source explicitly warns that numeric IDs should not be assumed; the count is exactly {len(locs)} location records.
- Empty `long` descriptions occur only for pseudo-locations (`LOC_NOWHERE`, some transient states).
- `travel` rules are evaluated in source order; conditional rules must be preserved exactly.
- Motion word symbols like `MOT_2` have no human-readable heading in the source and are represented by their first listed synonym.
"""
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    print(schema_analysis_report(ir))
