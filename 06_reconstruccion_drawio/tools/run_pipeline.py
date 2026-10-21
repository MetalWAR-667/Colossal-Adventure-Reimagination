#!/usr/bin/env python3
"""
End-to-end pipeline for Open Adventure YAML → draw.io reconstruction.

Usage:
    python tools/run_pipeline.py

Produces:
    output/Open_Adventure_World.drawio
    output/open_adventure_graph.json
    reports/SCHEMA_ANALYSIS.md
    reports/CHAPTER_PROPOSAL.md
    reports/VALIDATION_REPORT.md
"""

from __future__ import annotations

import json
from pathlib import Path

from oa_chapters import assign_chapters, chapter_assignment_report
from oa_drawio import write_drawio
from oa_graph import build_graph, save_graph
from oa_parser import parse_open_adventure
from oa_schema import schema_analysis_report
from oa_validate import validate


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    yaml_path = root / "Open_Adventure.yaml"
    output_dir = root / "output"
    reports_dir = root / "reports"
    output_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    print("[1/5] Parsing YAML...")
    ir = parse_open_adventure(yaml_path)

    print("[2/5] Building graph...")
    graph = build_graph(ir)

    print("[3/5] Assigning chapters...")
    graph = assign_chapters(graph)

    print("[4/5] Generating draw.io document...")
    drawio_path = output_dir / "Open_Adventure_World.drawio"
    write_drawio(graph, drawio_path)

    print("[5/5] Validating and writing reports...")
    graph_json_path = output_dir / "open_adventure_graph.json"
    save_graph(graph, graph_json_path)

    validation_report = validate(graph, drawio_path)

    (reports_dir / "SCHEMA_ANALYSIS.md").write_text(
        schema_analysis_report(ir), encoding="utf-8"
    )
    (reports_dir / "CHAPTER_PROPOSAL.md").write_text(
        chapter_assignment_report(graph), encoding="utf-8"
    )
    (reports_dir / "VALIDATION_REPORT.md").write_text(
        _validation_markdown(validation_report), encoding="utf-8"
    )

    print("Done.")
    print(f"  draw.io: {drawio_path}")
    print(f"  graph JSON: {graph_json_path}")
    print(f"  validation: {validation_report['overall']}")


def _validation_markdown(report: dict) -> str:
    lines = [
        "# Validation Report — Open Adventure draw.io reconstruction\n",
        f"**Overall:** `{report['overall']}`\n",
        f"**File:** `{report['drawio_file']}`\n",
        "## Checks\n",
    ]
    for name, result in report["checks"].items():
        status = result.get("result", "?")
        lines.append(f"### {name}: `{status}`")
        detail = json.dumps({k: v for k, v in result.items() if k != "result"}, indent=2)
        lines.append(f"```json\n{detail}\n```\n")
    gi = report.get("graphical_inspection", {})
    lines.append("## Graphical inspection")
    if gi.get("available"):
        lines.append(f"Available renderers: {gi['renderers']}")
    else:
        lines.append("No diagrams.net renderer detected on this machine. "
                     "Graphical inspection must be performed manually by opening "
                     "`output/Open_Adventure_World.drawio` in diagrams.net.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
