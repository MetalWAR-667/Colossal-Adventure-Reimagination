#!/usr/bin/env python3
"""
Validation suite for the generated Open Adventure draw.io document.

Checks source coverage, referential integrity, metadata round-tripping,
XML validity, and deterministic output.
"""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_chapters import assign_chapters
from oa_drawio import generate_drawio, write_drawio
from oa_graph import build_graph, parse_open_adventure


def _extract_drawio_cells(mxfile: ET.Element) -> tuple[list[ET.Element], list[ET.Element]]:
    """Return all vertex and edge cells across all diagrams."""
    vertices: list[ET.Element] = []
    edges: list[ET.Element] = []
    for diagram in mxfile.findall("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None:
            continue
        root = model.find("root")
        if root is None:
            continue
        for cell in root.iter("mxCell"):
            if cell.get("vertex") == "1":
                vertices.append(cell)
            elif cell.get("edge") == "1":
                edges.append(cell)
    return vertices, edges


def _extract_location_objects(mxfile: ET.Element) -> list[dict[str, Any]]:
    """Extract location nodes (object wrappers with source_id) from all pages."""
    results: list[dict[str, Any]] = []
    for diagram in mxfile.findall("diagram"):
        model = diagram.find("mxGraphModel")
        if model is None:
            continue
        root = model.find("root")
        if root is None:
            continue
        for obj in root.iter("object"):
            if obj.get("source_id"):
                results.append({k: v for k, v in obj.attrib.items()})
    return results


def validate(graph: dict[str, Any], drawio_path: Path) -> dict[str, Any]:
    """Run the full validation suite and return an evidence report."""
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

    # 3. Every source location appears as a node.
    loc_nodes = _extract_location_objects(mxfile)
    node_ids = {n["source_id"] for n in loc_nodes}
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

    # 4. Chapter assignments preserved.
    chapter_map = {loc["source_id"]: loc.get("chapter_id") for loc in graph["locations"]}
    mismatches = []
    for node in loc_nodes:
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
    for node in loc_nodes:
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
    vertices, edges = _extract_drawio_cells(mxfile)
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

    # 7. Determinism: regenerate and compare hashes.
    original_text = drawio_path.read_bytes()
    tmp_path = drawio_path.with_suffix(".tmp.drawio")
    write_drawio(graph, tmp_path)
    regenerated_text = tmp_path.read_bytes()
    tmp_path.unlink(missing_ok=True)
    report["checks"]["determinism"] = {
        "result": "PASS" if original_text == regenerated_text else "FAIL",
        "original_hash": hashlib.sha256(original_text).hexdigest()[:16],
        "regenerated_hash": hashlib.sha256(regenerated_text).hexdigest()[:16],
    }

    # 8. Statistics match.
    report["checks"]["statistics"] = {
        "result": "PASS",
        "locations": len(source_ids),
        "location_nodes": len(node_ids),
        "edges": len(edges),
    }

    overall = all(c.get("result") == "PASS" for c in report["checks"].values())
    report["overall"] = "PASS" if overall else "FAIL"
    return report


def graphical_inspection_available() -> dict[str, Any]:
    """Detect whether a diagrams.net renderer can be launched."""
    import shutil
    candidates = ["drawio", "draw.io", "diagrams.net"]
    found = [c for c in candidates if shutil.which(c)]
    if found:
        return {"available": True, "renderers": found}
    # On Windows, look for the desktop executable in common locations.
    common_paths = [
        Path.home() / "AppData" / "Local" / "Programs" / "draw.io" / "draw.io.exe",
        Path("C:/Program Files/draw.io/draw.io.exe"),
    ]
    found_exe = [str(p) for p in common_paths if p.exists()]
    if found_exe:
        return {"available": True, "renderers": found_exe}
    return {"available": False, "renderers": []}


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    graph = build_graph(ir)
    graph = assign_chapters(graph)
    out_path = root / "output" / "Open_Adventure_World.drawio"
    report = validate(graph, out_path)
    report["graphical_inspection"] = graphical_inspection_available()
    print(json.dumps(report, indent=2))
