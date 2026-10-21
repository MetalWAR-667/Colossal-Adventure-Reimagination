#!/usr/bin/env python3
"""
Generate Open_Adventure_World_V2.drawio with compass-oriented layout.

This module reads the existing Mission 001 graph JSON, applies the layout
engine, and writes a new editable diagrams.net document with:
- compass legends,
- direction-aware placement,
- exit summaries inside location boxes,
- styled conditional / special / vertical connectors,
- explicit cross-page references.
"""

from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_drawio import _body_text, _edge_label, _escape, _heading, _style_for_edge
from oa_layout import layout_all_chapters


NODE_WIDTH = 280
NODE_HEIGHT = 150
CROSS_MARKER_SIZE = 28


def _exit_line(edge: dict[str, Any], graph: dict[str, Any]) -> str:
    """Build one line of the exit summary for a location box."""
    label = edge.get("label", "")
    # Take the first verb as the primary exit keyword.
    verbs = edge.get("verbs", [])
    keyword = verbs[0] if verbs else "?"
    action = edge.get("action_type")
    target = edge.get("target")
    cond = edge.get("condition")

    suffix = ""
    if cond:
        ct = cond.get("type")
        if ct == "probability":
            suffix = f" [{cond.get('percent')}%]"
        elif ct == "carry":
            suffix = f" [carry {cond.get('object')}]"
        elif ct == "with":
            suffix = f" [with {cond.get('object')}]"
        elif ct == "not":
            suffix = f" [not {cond.get('object')}={cond.get('state')}]"
        elif ct == "nodwarves":
            suffix = " [nodwarves]"

    if action == "goto" and target:
        target_ch = ""
        if target not in graph["chapters"].get(graph["_chapter_id"], {}).get("members", set()):
            # Cross-chapter destination: annotate chapter title.
            for cid, ch in graph["chapters"].items():
                if target in ch.get("members", []):
                    target_ch = f" [{ch['title'].split(' — ')[0]}]"
                    break
        return f"{keyword} → {target}{target_ch}{suffix}"
    if action == "speak":
        return f"{keyword} → say {edge.get('message', '')}{suffix}"
    if action == "special":
        return f"{keyword} → special({edge.get('special_case', '')}){suffix}"
    return f"{keyword}{suffix}"


def _v2_node_label(loc: dict[str, Any], graph: dict[str, Any], chapter_id: str) -> str:
    """Build the V2 location box label with description and exit summary."""
    heading = _heading(loc)
    body = _body_text(loc)

    # Collect outgoing edges from this location within the graph.
    exits = []
    cross_chapter_exits = []
    for e in graph.get("edges", []):
        if e["source"] != loc["source_id"]:
            continue
        line = _exit_line(e, graph)
        if e.get("target") and e["target"] not in graph["chapters"][chapter_id]["members"]:
            cross_chapter_exits.append(line)
        else:
            exits.append(line)

    label = f"<b>{_escape(loc['source_id'])} — {_escape(heading)}</b><br><br>{_escape(body).replace(chr(10), '<br>')}"
    if exits:
        label += "<br><br><b>EXITS</b><br>" + "<br>".join(_escape(x) for x in exits)
    if cross_chapter_exits:
        label += "<br><br><b>CROSS-PAGE</b><br>" + "<br>".join(_escape(x) for x in cross_chapter_exits)
    return label


def _add_compass(parent: ET.Element, x: float, y: float) -> None:
    """Add a small compass legend to the page."""
    compass_style = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Courier New;fontSize=12;"
    value = "       N\n       ↑\n   W ← + → E\n       ↓\n       S"
    cell = ET.SubElement(parent, "mxCell")
    cell.set("id", "compass")
    cell.set("style", compass_style)
    cell.set("vertex", "1")
    cell.set("parent", "1")
    cell.set("value", _escape(value))
    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", "120")
    geom.set("height", "90")
    geom.set("as", "geometry")


def _create_root() -> tuple[ET.Element, ET.Element]:
    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return root, root


def _add_v2_location_node(parent: ET.Element, loc: dict[str, Any], x: float, y: float,
                          node_id: str, graph: dict[str, Any], chapter_id: str,
                          treasure_objects: set[str], immovable_objects: set[str]) -> ET.Element:
    """Add a V2 location node with embedded bilingual metadata."""
    desc = loc.get("description", {})
    long_text = desc.get("long") or ""
    short_text = desc.get("short") or ""
    maptag = desc.get("maptag") or ""

    obj = ET.SubElement(parent, "object")
    obj.set("label", _v2_node_label(loc, graph, chapter_id))
    obj.set("source_id", loc["source_id"])
    obj.set("description_en", str(long_text))
    obj.set("description_es", "")
    obj.set("short_en", str(short_text))
    obj.set("maptag", str(maptag))
    obj.set("chapter_id", str(loc.get("chapter_id", "")))
    obj.set("source_reference", f"Open_Adventure.yaml locations/{loc['source_id']}")
    obj.set("review_status", loc.get("review_status", "ok"))
    obj.set("role", loc.get("role", ""))
    obj.set("conditions", ", ".join(f"{k}={v}" for k, v in sorted(loc.get("conditions", {}).items())))
    if loc.get("objects_here"):
        obj.set("objects_here", ", ".join(loc["objects_here"]))
    treasures = [o for o in loc.get("objects_here", []) if o in treasure_objects]
    immovables = [o for o in loc.get("objects_here", []) if o in immovable_objects]
    if treasures:
        obj.set("treasures_here", ", ".join(treasures))
    if immovables:
        obj.set("immovable_objects_here", ", ".join(immovables))
    if loc.get("sound"):
        obj.set("sound", str(loc["sound"]))
    if loc.get("loud"):
        obj.set("loud", "true")

    cell = ET.SubElement(obj, "mxCell")
    cell.set("id", node_id)
    # Pseudo-locations get a subtle grey fill so they are visually distinct.
    fill = "#F5F5F5" if loc.get("role") in ("special", "transient", "null") else "#FFFFFF"
    cell.set("style", f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#333333;arcSize=6;")
    cell.set("vertex", "1")
    cell.set("parent", "1")

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(NODE_WIDTH))
    geom.set("height", str(NODE_HEIGHT))
    geom.set("as", "geometry")
    return obj


def _add_v2_edge(parent: ET.Element, edge: dict[str, Any], source_id: str, target_id: str,
                 edge_counter: int, is_cross_page: bool) -> None:
    edge_cell = ET.SubElement(parent, "mxCell")
    eid = f"e{edge_counter}"
    edge_cell.set("id", eid)
    edge_cell.set("style", _style_for_edge(edge))
    edge_cell.set("edge", "1")
    edge_cell.set("parent", "1")
    edge_cell.set("source", source_id)
    edge_cell.set("target", target_id)

    label = _edge_label(edge)
    if label:
        edge_cell.set("value", label)
    if is_cross_page:
        edge_cell.set("sourcePort", "east")

    geom = ET.SubElement(edge_cell, "mxGeometry")
    geom.set("relative", "1")
    geom.set("as", "geometry")


def _build_v2_index_page(graph: dict[str, Any]) -> ET.Element:
    root, _ = _create_root()
    y = 40
    x = 40

    title = ET.SubElement(root, "mxCell")
    title.set("id", "title")
    title.set("style", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1")
    title.set("vertex", "1")
    title.set("parent", "1")
    title.set("value", "Open Adventure — Compass-Oriented World Map (V2)")
    geom = ET.SubElement(title, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", "520")
    geom.set("height", "40")
    geom.set("as", "geometry")
    y += 80

    legend = ET.SubElement(root, "mxCell")
    legend.set("id", "legend")
    legend.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11")
    legend.set("vertex", "1")
    legend.set("parent", "1")
    legend_text = (
        "Legend: black solid=direct; orange dashed=conditional; blue dotted=random; "
        "grey dashed=speak message; purple dashed=special movement; "
        "blue solid=UP/DOWN vertical. Cross-page edges use off-page markers. "
        "A compass legend is present on every chapter page."
    )
    legend.set("value", legend_text)
    geom = ET.SubElement(legend, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", "820")
    geom.set("height", "50")
    geom.set("as", "geometry")
    y += 80

    provenance = ET.SubElement(root, "mxCell")
    provenance.set("id", "provenance")
    provenance.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=10;fontStyle=2")
    provenance.set("vertex", "1")
    provenance.set("parent", "1")
    provenance_text = (
        "Source: Open_Adventure.yaml  |  License: BSD-2-Clause  |  "
        "Author: Eric S. Raymond / Open Adventure project  |  "
        "Generated by 007 RPG Archaeology tooling. "
        "This is a derived documentation artifact; the YAML source remains canonical."
    )
    provenance.set("value", provenance_text)
    geom = ET.SubElement(provenance, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", "820")
    geom.set("height", "40")
    geom.set("as", "geometry")
    y += 80

    for cid, ch in graph["chapters"].items():
        box = ET.SubElement(root, "mxCell")
        box.set("id", f"idx_{cid}")
        box.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1976D2;arcSize=6;")
        box.set("vertex", "1")
        box.set("parent", "1")
        box.set("value", f"<b>{_escape(ch['title'])}</b><br>{_escape(ch['description'])}<br><i>{ch['member_count']} locations</i>")
        geom = ET.SubElement(box, "mxGeometry")
        geom.set("x", str(x))
        geom.set("y", str(y))
        geom.set("width", str(NODE_WIDTH))
        geom.set("height", "90")
        geom.set("as", "geometry")

        x += NODE_WIDTH + 40
        if x > 40 + (NODE_WIDTH + 40) * 2:
            x = 40
            y += 120

    return root


def _build_v2_chapter_page(graph: dict[str, Any], chapter_id: str,
                           layout: dict[str, Any]) -> ET.Element:
    root, _ = _create_root()
    chapter = graph["chapters"][chapter_id]
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    positions = layout["positions"]

    # Title
    title = ET.SubElement(root, "mxCell")
    title.set("id", f"title_{chapter_id}")
    title.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1")
    title.set("vertex", "1")
    title.set("parent", "1")
    title.set("value", f"{chapter['title']}")
    geom = ET.SubElement(title, "mxGeometry")
    geom.set("x", "40")
    geom.set("y", "10")
    geom.set("width", "520")
    geom.set("height", "30")
    geom.set("as", "geometry")

    # Compass
    _add_compass(root, 40, 50)

    # Nodes
    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}
    node_ids: dict[str, str] = {}
    for loc_id in chapter["members"]:
        loc = loc_index[loc_id]
        x, y = positions.get(loc_id, (40, 40))
        node_id = f"{chapter_id}_{loc_id}"
        node_ids[loc_id] = node_id
        # Inject current chapter ID into graph for cross-page summary lookup.
        graph["_chapter_id"] = chapter_id
        _add_v2_location_node(root, loc, x, y, node_id, graph, chapter_id,
                              treasure_objects, immovable_objects)

    # Edges
    edge_counter = 0
    for edge in graph["edges"]:
        src = edge["source"]
        tgt = edge.get("target")
        if src not in node_ids:
            continue
        edge_counter += 1
        if tgt is not None and tgt in node_ids:
            _add_v2_edge(root, edge, node_ids[src], node_ids[tgt], edge_counter, is_cross_page=False)
        else:
            # Cross-page or speak/special marker.
            marker_id = f"{node_ids[src]}_out_{edge_counter}"
            marker = ET.SubElement(root, "mxCell")
            marker.set("id", marker_id)
            marker.set("style", "shape=offpageConnector;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F57C00;size=0.5;")
            marker.set("vertex", "1")
            marker.set("parent", "1")
            label = _edge_label(edge)
            if label:
                marker.set("value", _escape(label))
            geom = ET.SubElement(marker, "mxGeometry")
            sx, sy = positions[src]
            geom.set("x", str(sx + NODE_WIDTH + 20))
            geom.set("y", str(sy + NODE_HEIGHT / 2 - CROSS_MARKER_SIZE / 2))
            geom.set("width", str(CROSS_MARKER_SIZE))
            geom.set("height", str(CROSS_MARKER_SIZE))
            geom.set("as", "geometry")
            _add_v2_edge(root, edge, node_ids[src], marker_id, edge_counter, is_cross_page=True)

    return root


def _pretty_drawio(xml_text: str) -> str:
    import xml.dom.minidom as md
    dom = md.parseString(xml_text.encode("utf-8"))
    pretty = dom.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    lines = [line for line in pretty.splitlines() if line.strip()]
    return "\n".join(lines) + "\n"


def generate_v2_drawio(graph: dict[str, Any], layouts: dict[str, Any]) -> ET.Element:
    """Build the complete V2 <mxfile> document."""
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "Open Adventure RPG Archaeology tooling")
    mxfile.set("modified", "2026-10-16T00:00:00.000Z")
    mxfile.set("agent", "007-oa-drawio-v2-generator")
    mxfile.set("etag", "deterministic")
    mxfile.set("type", "device")
    mxfile.set("version", "24.7.0")

    def add_page(root: ET.Element, page_id: str, name: str, width: str, height: str) -> None:
        diag = ET.SubElement(mxfile, "diagram")
        diag.set("id", page_id)
        diag.set("name", name)
        model = ET.SubElement(diag, "mxGraphModel")
        model.set("dx", "1422")
        model.set("dy", "762")
        model.set("grid", "1")
        model.set("gridSize", "10")
        model.set("guides", "1")
        model.set("tooltips", "1")
        model.set("connect", "1")
        model.set("arrows", "1")
        model.set("fold", "1")
        model.set("page", "1")
        model.set("pageScale", "1")
        model.set("pageWidth", width)
        model.set("pageHeight", height)
        model.set("math", "0")
        model.set("shadow", "0")
        model.append(root)

    index_root = _build_v2_index_page(graph)
    add_page(index_root, "index", "00 — World Index", "850", "1100")

    for chapter_id in graph["chapters"].keys():
        layout = layouts["chapters"][chapter_id]
        chapter_root = _build_v2_chapter_page(graph, chapter_id, layout)
        add_page(chapter_root, chapter_id, graph["chapters"][chapter_id]["title"],
                 str(layout["width"]), str(layout["height"]))

    return mxfile


def write_v2_drawio(graph: dict[str, Any], layouts: dict[str, Any], path: Path) -> None:
    """Write the V2 draw.io XML file."""
    mxfile = generate_v2_drawio(graph, layouts)
    ET.register_namespace("", "")
    tree = ET.ElementTree(mxfile)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    rough = path.read_text(encoding="utf-8")
    pretty = _pretty_drawio(rough)
    path.write_text(pretty, encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    with open(root / "output" / "open_adventure_graph.json", encoding="utf-8") as f:
        graph = json.load(f)
    layouts = layout_all_chapters(graph)
    out_path = root / "output" / "Open_Adventure_World_V2.drawio"
    write_v2_drawio(graph, layouts, out_path)
    print(f"Wrote {out_path}")
