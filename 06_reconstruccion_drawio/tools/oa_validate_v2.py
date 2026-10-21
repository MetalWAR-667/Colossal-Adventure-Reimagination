#!/usr/bin/env python3
"""
Validation suite for the compass-oriented V2 draw.io document.

Extends Mission 001 validation with layout-specific checks: box overlap,
compass presence, and directional-constraint reporting.
"""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_drawio_v2 import generate_v2_drawio, write_v2_drawio
from oa_layout import layout_all_chapters


def _load_graph(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _extract_cells(mxfile: ET.Element) -> tuple[list[ET.Element], list[ET.Element], list[dict[str, Any]]]:
    """Return vertices, edges, and location objects across all diagrams."""
    vertices: list[ET.Element] = []
    edges: list[ET.Element] = []
    loc_objects: list[dict[str, Any]] = []
    for diagram in mxfile.findall("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None:
            continue
        root = model.find("root")
        if root is None:
            continue
        for obj in root.iter("object"):
            if obj.get("source_id"):
                loc_objects.append({k: v for k, v in obj.attrib.items()})
        for cell in root.iter("mxCell"):
            if cell.get("vertex") == "1":
                vertices.append(cell)
            elif cell.get("edge") == "1":
                edges.append(cell)
    return vertices, edges, loc_objects


def _box_geometry(cell: ET.Element) -> tuple[float, float, float, float] | None:
    geom = cell.find("mxGeometry")
    if geom is None:
        return None
    try:
        x = float(geom.get("x", 0))
        y = float(geom.get("y", 0))
        w = float(geom.get("width", 0))
        h = float(geom.get("height", 0))
        return (x, y, w, h)
    except (TypeError, ValueError):
        return None


def _boxes_overlap(a: tuple[float, float, float, float],
                   b: tuple[float, float, float, float]) -> bool:
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or
                a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


def _count_location_overlaps_per_diagram(mxfile: ET.Element) -> tuple[int, list[tuple[str, str, str]]]:
    """Check overlaps between location boxes (object wrappers) within each page."""
    total = 0
    pairs: list[tuple[str, str, str]] = []
    for diagram in mxfile.findall("diagram"):
        diag_name = diagram.get("name", "?")
        root = diagram.find("mxGraphModel/root")
        if root is None:
            continue
        boxes: list[tuple[str, tuple[float, float, float, float]]] = []
        for obj in root.iter("object"):
            bid = obj.get("source_id")
            cell = obj.find("mxCell")
            if bid and cell is not None:
                geom = _box_geometry(cell)
                if geom:
                    boxes.append((bid, geom))
        for i, (aid, a) in enumerate(boxes):
            for bid, b in boxes[i + 1:]:
                if _boxes_overlap(a, b):
                    total += 1
                    pairs.append((diag_name, aid, bid))
    return total, pairs


def validate_v2(graph_path: Path, drawio_path: Path) -> dict[str, Any]:
    graph = _load_graph(graph_path)
    layouts = layout_all_chapters(graph)

    report: dict[str, Any] = {
        "drawio_file": str(drawio_path.resolve()),
        "checks": {},
    }

    # 1. XML well-formedness.
    try:
        tree = ET.parse(drawio_path)
        mxfile = tree.getroot()
        report["checks"]["xml_well_formed"] = {"result": "PASS", "root_tag": mxfile.tag}
    except ET.ParseError as exc:
        report["checks"]["xml_well_formed"] = {"result": "FAIL", "error": str(exc)}
        return report

    # 2. Page structure.
    diagrams = mxfile.findall("diagram")
    page_names = [d.get("name") for d in diagrams]
    report["checks"]["page_structure"] = {
        "result": "PASS",
        "page_count": len(diagrams),
        "pages": page_names,
    }

    vertices, edges, loc_objects = _extract_cells(mxfile)

    # 3. Location coverage.
    node_ids = {n["source_id"] for n in loc_objects}
    source_ids = {loc["source_id"] for loc in graph["locations"]}
    missing = source_ids - node_ids
    extra = node_ids - source_ids
    report["checks"]["location_coverage"] = {
        "result": "PASS" if not missing else "FAIL",
        "source_locations": len(source_ids),
        "nodes_found": len(node_ids),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }

    # 4. Chapter preservation.
    chapter_map = {loc["source_id"]: loc.get("chapter_id") for loc in graph["locations"]}
    mismatches = []
    for node in loc_objects:
        sid = node.get("source_id")
        expected = chapter_map.get(sid)
        actual = node.get("chapter_id")
        if expected and actual != expected:
            mismatches.append({"source_id": sid, "expected": expected, "actual": actual})
    report["checks"]["chapter_preservation"] = {
        "result": "PASS" if not mismatches else "FAIL",
        "mismatches": mismatches,
    }

    # 5. Description round-trip.
    description_mismatches = []
    source_long = {loc["source_id"]: (loc.get("description", {}).get("long") or "") for loc in graph["locations"]}
    for node in loc_objects:
        sid = node.get("source_id")
        expected = source_long.get(sid, "")
        actual = node.get("description_en", "")
        if expected != actual:
            description_mismatches.append({
                "source_id": sid,
                "expected_len": len(expected),
                "actual_len": len(actual),
            })
    report["checks"]["description_roundtrip"] = {
        "result": "PASS" if not description_mismatches else "FAIL",
        "mismatch_count": len(description_mismatches),
        "samples": description_mismatches[:5],
    }

    # 6. Edge reference integrity.
    valid_ids = {c.get("id") for c in vertices}
    bad_edges = []
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src not in valid_ids or tgt not in valid_ids:
            bad_edges.append({"id": edge.get("id"), "source": src, "target": tgt})
    report["checks"]["edge_integrity"] = {
        "result": "PASS" if not bad_edges else "FAIL",
        "total_edges": len(edges),
        "bad_edges": bad_edges[:10],
    }

    # 7. Travel rule count against canonical graph.
    canonical_edges = len(graph["edges"])
    report["checks"]["travel_rule_count"] = {
        "result": "PASS" if len(edges) == canonical_edges else "FAIL",
        "canonical_rules": canonical_edges,
        "drawio_edges": len(edges),
    }

    # 8. Location box overlap check (per diagram).
    overlap_count, overlap_pairs = _count_location_overlaps_per_diagram(mxfile)
    report["checks"]["box_overlap"] = {
        "result": "PASS" if overlap_count == 0 else "FAIL",
        "overlap_count": overlap_count,
        "samples": overlap_pairs[:10],
    }

    # 9. Compass presence on chapter pages.
    missing_compass = []
    for diagram in diagrams:
        if diagram.get("id") == "index":
            continue
        root = diagram.find("mxGraphModel/root")
        has_compass = any(c.get("id") == "compass" for c in root.iter("mxCell")) if root is not None else False
        if not has_compass:
            missing_compass.append(diagram.get("name"))
    report["checks"]["compass_presence"] = {
        "result": "PASS" if not missing_compass else "FAIL",
        "missing": missing_compass,
    }

    # 10. Determinism.
    original_text = drawio_path.read_bytes()
    tmp_path = drawio_path.with_suffix(".tmp.drawio")
    write_v2_drawio(graph, layouts, tmp_path)
    regenerated_text = tmp_path.read_bytes()
    tmp_path.unlink(missing_ok=True)
    report["checks"]["determinism"] = {
        "result": "PASS" if original_text == regenerated_text else "FAIL",
        "original_hash": hashlib.sha256(original_text).hexdigest()[:16],
        "regenerated_hash": hashlib.sha256(regenerated_text).hexdigest()[:16],
    }

    # 11. Layout metrics from layout engine.
    report["checks"]["layout_metrics"] = {
        "result": "PASS",
        "total_satisfied": layouts["summary"]["total_satisfied"],
        "total_violated": layouts["summary"]["total_violated"],
        "per_chapter": {
            cid: {
                "width": layout["width"],
                "height": layout["height"],
                "satisfied": layout["constraint_evaluation"]["satisfied"],
                "violated": layout["constraint_evaluation"]["violated"],
            }
            for cid, layout in layouts["chapters"].items()
        },
    }

    overall = all(c.get("result") == "PASS" for c in report["checks"].values())
    report["overall"] = "PASS" if overall else "FAIL"
    report["manual_validation_required"] = True
    return report


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    report = validate_v2(
        root / "output" / "open_adventure_graph.json",
        root / "output" / "Open_Adventure_World_V2.drawio",
    )
    print(json.dumps(report, indent=2))
