#!/usr/bin/env python3
"""
End-to-end pipeline for Mission 002 — compass-oriented V2 draw.io map.

Usage:
    python tools/run_v2.py

Produces:
    output/Open_Adventure_World_V2.drawio
    reports/LAYOUT_V2_REPORT.md
"""

from __future__ import annotations

import json
from pathlib import Path

from oa_drawio_v2 import write_v2_drawio
from oa_layout import layout_all_chapters
from oa_validate_v2 import validate_v2


def _layout_report_markdown(layouts: dict[str, Any]) -> str:
    lines = ["## Directional layout metrics\n"]
    lines.append("| Chapter | Nodes | Width | Height | Satisfied | Violated |")
    lines.append("|---------|-------|-------|--------|-----------|----------|")
    for cid, layout in layouts["chapters"].items():
        ce = layout["constraint_evaluation"]
        lines.append(
            f"| {cid} | {len(layout['positions'])} | {layout['width']} | {layout['height']} | "
            f"{ce['satisfied']} | {ce['violated']} |"
        )
    lines.append("")
    lines.append(f"**Total directional constraints satisfied:** {layouts['summary']['total_satisfied']}")
    lines.append(f"**Total directional constraints violated:** {layouts['summary']['total_violated']}")
    lines.append("")
    lines.append("Violations are expected in cyclic areas such as the forest, the all-alike maze, "
                 "and the all-different maze, where compass-labeled edges intentionally create "
                 "non-planar or non-Euclidean paths. The underlying travel rules are preserved "
                 "regardless of layout orientation.\n")

    lines.append("### Sample constraint violations\n")
    shown = 0
    for cid, layout in layouts["chapters"].items():
        for v in layout["constraint_evaluation"]["violations"][:3]:
            lines.append(f"- `{v['source']} --{v['direction']}--> {v['target']}` delta={v['delta']} (in {cid})")
            shown += 1
            if shown >= 20:
                break
        if shown >= 20:
            break
    lines.append("")
    return "\n".join(lines)


def _validation_report_markdown(report: dict[str, Any]) -> str:
    lines = ["## Automated validation\n"]
    lines.append(f"**Overall:** `{report['overall']}`\n")
    lines.append("| Check | Result | Notes |")
    lines.append("|-------|--------|-------|")
    for name, result in report["checks"].items():
        status = result.get("result", "?")
        notes = ""
        if name == "location_coverage":
            notes = f"{result['nodes_found']}/{result['source_locations']} nodes"
        elif name == "description_roundtrip":
            notes = f"{result['mismatch_count']} mismatches"
        elif name == "edge_integrity":
            notes = f"{result['total_edges']} edges, {len(result['bad_edges'])} bad"
        elif name == "travel_rule_count":
            notes = f"{result['drawio_edges']}/{result['canonical_rules']} rules"
        elif name == "box_overlap":
            notes = f"{result['overlap_count']} overlaps"
        elif name == "determinism":
            notes = f"hash {result['original_hash']}"
        elif name == "layout_metrics":
            notes = f"satisfied {result['total_satisfied']}, violated {result['total_violated']}"
        lines.append(f"| {name} | {status} | {notes} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    graph_path = root / "output" / "open_adventure_graph.json"
    drawio_path = root / "output" / "Open_Adventure_World_V2.drawio"
    report_path = root / "reports" / "LAYOUT_V2_REPORT.md"

    print("[1/4] Loading Mission 001 graph...")
    with graph_path.open("r", encoding="utf-8") as f:
        graph = json.load(f)

    print("[2/4] Computing compass-oriented layout...")
    layouts = layout_all_chapters(graph)

    print("[3/4] Writing V2 draw.io document...")
    write_v2_drawio(graph, layouts, drawio_path)

    print("[4/4] Validating and writing report...")
    report = validate_v2(graph_path, drawio_path)

    md = f"""# Layout V2 Report — Compass-Oriented Open Adventure Map

**Mission:** MISSION 002 — Compass-Oriented Cartography  
**Agent:** 007 — RPG Archaeology  
**Status:** `{'PASS' if report['overall'] == 'PASS' else 'FAIL'}` automated checks; **MANUAL_VALIDATION_REQUIRED** for visual usability.

## Scope

This report covers the second-generation `.drawio` map produced from the
Mission 001 intermediate graph. The underlying gameplay graph was not rebuilt;
only layout, node presentation, and connection rendering were changed.

## Output files

- `output/Open_Adventure_World_V2.drawio`
- `output/open_adventure_graph.json` (unchanged from Mission 001)

{_validation_report_markdown(report)}
{_layout_report_markdown(layouts)}
## Visual inspection

No diagrams.net renderer was detected on this machine. Open
`output/Open_Adventure_World_V2.drawio` in diagrams.net to verify:

1. Location boxes are readable and non-overlapping.
2. Compass legends are visible on every chapter page.
3. Directional arrows follow the expected N/S/E/W orientation where feasible.
4. Conditional, vertical, special, and cross-page edges are clearly distinguishable.
5. Exit summaries inside location boxes match the original YAML travel rules.

## Notes

- North is up (smaller Y). South is down (larger Y). East is right (larger X). West is left (smaller X).
- UP/DOWN movement is drawn with solid blue edges and labelled explicitly, distinct from compass N/S.
- Magic teleport destinations (`LOC_FOOF*`) are placed in the chapter of their target and marked in exit summaries.
- Death and transient pseudo-locations are grouped on the "Special & Transient States" page with a grey background.
- Conflicting directional constraints were not resolved by altering gameplay data; they are reported above.
"""

    report_path.write_text(md, encoding="utf-8")

    print("Done.")
    print(f"  V2 draw.io: {drawio_path}")
    print(f"  report: {report_path}")
    print(f"  validation: {report['overall']}")


if __name__ == "__main__":
    main()
