#!/usr/bin/env python3
"""
Generate an editable, multipage diagrams.net (.drawio) document from the
Open Adventure graph.

The output is native draw.io XML, deterministic for a given input, and stores
full source metadata on every location node to support future translation.
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_chapters import assign_chapters
from oa_graph import build_graph, parse_open_adventure


NODE_WIDTH = 260
NODE_HEIGHT = 110
GRID_COLS = 6
GRID_X_SPACING = 320
GRID_Y_SPACING = 160
PAGE_MARGIN_X = 40
PAGE_MARGIN_Y = 40


def _escape(text: str | None) -> str:
    if text is None:
        return ""
    return html.escape(str(text))


def _heading(loc: dict[str, Any]) -> str:
    """Return a short heading for a location box."""
    desc = loc.get("description", {})
    if desc.get("maptag"):
        return str(desc["maptag"]).strip()
    if desc.get("short"):
        short = str(desc["short"]).strip()
        # Drop the common "You're " prefix for a cleaner heading.
        for prefix in ("You're ", "You are ", "You''re "):
            if short.startswith(prefix):
                short = short[len(prefix):]
                break
        short = short.rstrip(".")
        if short:
            return short
    long_text = str(desc.get("long") or "").strip()
    if long_text:
        return long_text.replace("\n", " ")[:50].rstrip() + ("..." if len(long_text) > 50 else "")
    return loc["source_id"]


def _body_text(loc: dict[str, Any]) -> str:
    """Return the body text for a location box, abbreviating if necessary."""
    long_text = loc.get("description", {}).get("long") or ""
    if not long_text:
        return "(no long description)"
    long_text = str(long_text).strip()
    if len(long_text) <= 220:
        return long_text
    preview = long_text[:210].rstrip()
    return preview + "\n[... full description stored in node metadata ...]"


def _node_label(loc: dict[str, Any]) -> str:
    heading = _heading(loc)
    body = _body_text(loc)
    return f"<b>{_escape(loc['source_id'])} — {_escape(heading)}</b><br><br>{_escape(body).replace(chr(10), '<br>')}"


def _style_for_edge(edge: dict[str, Any]) -> str:
    """Return a draw.io edge style reflecting the movement rule type."""
    base = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    cond = edge.get("condition")
    action = edge.get("action_type")

    if action == "speak":
        return base + "strokeColor=#999999;dashed=1;dashPattern=1 1;"
    if action == "special":
        return base + "strokeColor=#7B1FA2;dashed=1;dashPattern=1 1;"
    if cond is None:
        return base + "strokeColor=#000000;"

    ct = cond.get("type")
    if ct == "probability":
        return base + "strokeColor=#1976D2;dashed=1;dashPattern=1 2;"
    # carry / with / not / nodwarves
    return base + "strokeColor=#F57C00;dashed=1;dashPattern=1 1;"


def _edge_label(edge: dict[str, Any]) -> str | None:
    """Return a short label for an edge, including condition hints."""
    label = edge.get("label", "")
    cond = edge.get("condition")
    action = edge.get("action_type")
    suffix = ""
    if action == "speak":
        suffix = f" → say {edge.get('message', '')}"
    elif action == "special":
        suffix = f" → special({edge.get('special_case', '')})"
    elif cond:
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
    if not label and not suffix:
        return None
    return (label or "") + suffix


def _create_root() -> tuple[ET.Element, ET.Element]:
    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return root, root


def _add_location_node(parent: ET.Element, loc: dict[str, Any], x: float, y: float, node_id: str,
                       treasure_objects: set[str], immovable_objects: set[str]) -> ET.Element:
    """Add a location node with embedded bilingual metadata."""
    desc = loc.get("description", {})
    long_text = desc.get("long") or ""
    short_text = desc.get("short") or ""
    maptag = desc.get("maptag") or ""

    obj = ET.SubElement(parent, "object")
    obj.set("label", _node_label(loc))
    obj.set("source_id", loc["source_id"])
    obj.set("description_en", str(long_text))
    obj.set("description_es", "")  # placeholder for future translation
    obj.set("short_en", str(short_text))
    obj.set("maptag", str(maptag))
    obj.set("chapter_id", str(loc.get("chapter_id", "")))
    obj.set("source_reference", f"Open_Adventure.yaml locations/{loc['source_id']}")
    obj.set("review_status", loc.get("review_status", "ok"))
    obj.set("role", loc.get("role", ""))
    obj.set("conditions", ", ".join(f"{k}={v}" for k, v in sorted(loc.get("conditions", {}).items())))
    if loc.get("objects_here"):
        obj.set("objects_here", ", ".join(loc["objects_here"]))
    # Treasure / immovable flags are useful for translators and puzzle analysis.
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
    cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#333333;arcSize=6;")
    cell.set("vertex", "1")
    cell.set("parent", "1")

    geom = ET.SubElement(cell, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(NODE_WIDTH))
    geom.set("height", str(NODE_HEIGHT))
    geom.set("as", "geometry")
    return obj


def _add_edge(parent: ET.Element, edge: dict[str, Any], source_id: str, target_id: str,
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
        # Cross-page edges get a small off-page connector note on the target side.
        edge_cell.set("sourcePort", "east")

    geom = ET.SubElement(edge_cell, "mxGeometry")
    geom.set("relative", "1")
    geom.set("as", "geometry")


def _grid_position(index: int) -> tuple[float, float]:
    col = index % GRID_COLS
    row = index // GRID_COLS
    return (
        PAGE_MARGIN_X + col * GRID_X_SPACING,
        PAGE_MARGIN_Y + row * GRID_Y_SPACING,
    )


def _build_index_page(graph: dict[str, Any]) -> ET.Element:
    root, _ = _create_root()
    y = PAGE_MARGIN_Y
    x = PAGE_MARGIN_X

    title = ET.SubElement(root, "mxCell")
    title.set("id", "title")
    title.set("style", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1")
    title.set("vertex", "1")
    title.set("parent", "1")
    title.set("value", "Open Adventure — World Index")
    geom = ET.SubElement(title, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(NODE_WIDTH * 2))
    geom.set("height", "40")
    geom.set("as", "geometry")
    y += 80

    legend = ET.SubElement(root, "mxCell")
    legend.set("id", "legend")
    legend.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11")
    legend.set("vertex", "1")
    legend.set("parent", "1")
    legend_text = (
        "Legend: black=direct; orange=dashed=conditional; blue=dotted=random; "
        "grey=dashed=speak message; purple=dashed=special movement. "
        "Cross-page edges are shown as off-page references."
    )
    legend.set("value", legend_text)
    geom = ET.SubElement(legend, "mxGeometry")
    geom.set("x", str(x))
    geom.set("y", str(y))
    geom.set("width", str(NODE_WIDTH * 3))
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
    geom.set("width", str(NODE_WIDTH * 3))
    geom.set("height", "40")
    geom.set("as", "geometry")
    y += 70

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
        geom.set("height", "80")
        geom.set("as", "geometry")

        x += NODE_WIDTH + 40
        if x > PAGE_MARGIN_X + (NODE_WIDTH + 40) * 2:
            x = PAGE_MARGIN_X
            y += 100

    return root


def _build_chapter_page(graph: dict[str, Any], chapter_id: str) -> ET.Element:
    root, _ = _create_root()
    chapter = graph["chapters"][chapter_id]
    members = sorted(chapter["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}

    # Title
    title = ET.SubElement(root, "mxCell")
    title.set("id", f"title_{chapter_id}")
    title.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1")
    title.set("vertex", "1")
    title.set("parent", "1")
    title.set("value", f"{chapter['title']}")
    geom = ET.SubElement(title, "mxGeometry")
    geom.set("x", str(PAGE_MARGIN_X))
    geom.set("y", str(PAGE_MARGIN_Y - 30))
    geom.set("width", str(NODE_WIDTH * 2))
    geom.set("height", "30")
    geom.set("as", "geometry")

    # Nodes
    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}
    node_ids: dict[str, str] = {}
    for idx, loc_id in enumerate(members):
        loc = loc_index[loc_id]
        x, y = _grid_position(idx)
        node_id = f"{chapter_id}_{loc_id}"
        node_ids[loc_id] = node_id
        _add_location_node(root, loc, x, y, node_id, treasure_objects, immovable_objects)

    # Edges whose source is in this chapter.
    edge_counter = 0
    for edge in graph["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        if src not in node_ids:
            continue
        edge_counter += 1
        if tgt is not None and tgt in node_ids:
            # Internal edge
            _add_edge(root, edge, node_ids[src], node_ids[tgt], edge_counter, is_cross_page=False)
        else:
            # Cross-page edge or speak/special edge: create a small off-page marker.
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
            # Place the marker to the right of the source node.
            src_geom = node_ids[src]
            # We need source coordinates; fetch from the node we created.
            src_node = next((n for n in root.findall("object/mxCell") if n.get("id") == src_geom), None)
            if src_node is not None:
                g = src_node.find("mxGeometry")
                sx = float(g.get("x", 0)) + NODE_WIDTH
                sy = float(g.get("y", 0)) + NODE_HEIGHT / 2
            else:
                sx, sy = PAGE_MARGIN_X, PAGE_MARGIN_Y
            geom.set("x", str(sx + 20))
            geom.set("y", str(sy - 12))
            geom.set("width", "24")
            geom.set("height", "24")
            geom.set("as", "geometry")

            _add_edge(root, edge, node_ids[src], marker_id, edge_counter, is_cross_page=True)

    return root


def generate_drawio(graph: dict[str, Any]) -> ET.Element:
    """Build the complete <mxfile> document."""
    mxfile = ET.Element("mxfile")
    mxfile.set("host", "Open Adventure RPG Archaeology tooling")
    mxfile.set("modified", "2026-10-16T00:00:00.000Z")
    mxfile.set("agent", "007-oa-drawio-generator")
    mxfile.set("etag", "deterministic")
    mxfile.set("type", "device")
    mxfile.set("version", "24.7.0")

    # Index page
    index_root = _build_index_page(graph)
    index_diag = ET.SubElement(mxfile, "diagram")
    index_diag.set("id", "index")
    index_diag.set("name", "00 — World Index")
    index_model = ET.SubElement(index_diag, "mxGraphModel")
    index_model.set("dx", "1422")
    index_model.set("dy", "762")
    index_model.set("grid", "1")
    index_model.set("gridSize", "10")
    index_model.set("guides", "1")
    index_model.set("tooltips", "1")
    index_model.set("connect", "1")
    index_model.set("arrows", "1")
    index_model.set("fold", "1")
    index_model.set("page", "1")
    index_model.set("pageScale", "1")
    index_model.set("pageWidth", "850")
    index_model.set("pageHeight", "1100")
    index_model.set("math", "0")
    index_model.set("shadow", "0")
    index_model.append(index_root)

    # Chapter pages
    for chapter_id in graph["chapters"].keys():
        chapter_root = _build_chapter_page(graph, chapter_id)
        diag = ET.SubElement(mxfile, "diagram")
        diag.set("id", chapter_id)
        diag.set("name", graph["chapters"][chapter_id]["title"])
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
        model.set("pageWidth", "2400")
        model.set("pageHeight", "1600")
        model.set("math", "0")
        model.set("shadow", "0")
        model.append(chapter_root)

    return mxfile


def write_drawio(graph: dict[str, Any], path: Path) -> None:
    """Write the draw.io XML file with a deterministic declaration."""
    mxfile = generate_drawio(graph)
    # Register namespaces so draw.io recognises the file cleanly.
    ET.register_namespace("", "")
    tree = ET.ElementTree(mxfile)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    # Post-process to add a newline and pretty-print for human readability.
    rough = path.read_text(encoding="utf-8")
    pretty = _pretty_drawio(rough)
    path.write_text(pretty, encoding="utf-8")


def _pretty_drawio(xml_text: str) -> str:
    """Minimal pretty-printing that keeps draw.io content intact."""
    import xml.dom.minidom as md
    dom = md.parseString(xml_text.encode("utf-8"))
    pretty = dom.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    # Remove empty text-only lines produced by minidom.
    lines = [line for line in pretty.splitlines() if line.strip()]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    graph = build_graph(ir)
    graph = assign_chapters(graph)
    out_path = root / "output" / "Open_Adventure_World.drawio"
    write_drawio(graph, out_path)
    print(f"Wrote {out_path}")
