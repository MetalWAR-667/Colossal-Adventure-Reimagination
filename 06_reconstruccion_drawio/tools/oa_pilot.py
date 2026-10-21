#!/usr/bin/env python3
"""
Mission 003 — CH_ENTRY pilot generator (Mata Hari).

Generates output/pilot/CH_ENTRY_MataHari.drawio using the v3
constraint-solver layout, with:

- text-aware node heights,
- exit summaries in original rule-precedence order,
- directional connection points (N/S/E/W/NE/SE/SW/NW + UP/DOWN channels),
- distinct styles for conditional / random / speak / special / vertical,
- precise cross-page markers (destination ID + chapter),
- full source metadata on every node (bilingual-ready).

Also computes validation evidence and a baseline-vs-pilot comparison
using identical measurement definitions.
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_drawio import _body_text, _escape, _heading
from oa_layout import _node_edges_for_chapter, layout_chapter
from oa_layout_v3 import (
    DIRECTION_SIGNS,
    MIN_H,
    NODE_W,
    VERTICAL,
    estimate_height,
    layout_chapter_v3,
    primary_direction_v3,
)

CHAPTER_ID = "CH_ENTRY"
PILOT_NODE_W = NODE_W  # 300
FONT = "fontSize=11;fontFamily=Helvetica;"

# Editorial placement hint (documented in the audit report): the source
# descriptions place EASTBANK on the "east bank of a fissure" and WESTBANK
# on the "west side of the fissure", so WESTBANK is laid out west of
# EASTBANK. This affects placement only, never compass metrics.
HINTS: dict[str, str] = {"LOC_WESTBANK": "west_of:LOC_EASTBANK"}


# ---------------------------------------------------------------------------
# Content building
# ---------------------------------------------------------------------------

def _cond_str(cond: dict[str, Any] | None) -> str:
    if cond is None:
        return ""
    t = cond.get("type")
    if t == "probability":
        return f" [{cond.get('percent')}%]"
    if t == "carry":
        return f" [carry {cond.get('object')}]"
    if t == "with":
        return f" [with {cond.get('object')}]"
    if t == "not":
        return f" [not {cond.get('object')}={cond.get('state')}]"
    if t == "nodwarves":
        return " [nodwarves]"
    return " [?]"


def _verb_display(verb: str, motion_map: dict[str, str]) -> str:
    return motion_map.get(verb, verb)


def build_content(graph: dict[str, Any], chapter_id: str) -> dict[str, dict[str, Any]]:
    """Build per-location display content in original rule order."""
    members = set(graph["chapters"][chapter_id]["members"])
    motion_map = graph["motion_map"]
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    chapter_titles = {cid: ch["title"] for cid, ch in graph["chapters"].items()}

    content: dict[str, dict[str, Any]] = {}
    for loc_id in sorted(members):
        loc = loc_index[loc_id]
        heading = _heading(loc)
        body = _body_text(loc)  # full text; CH_ENTRY never needs truncation

        exit_lines: list[str] = []
        internal_rules: list[dict[str, Any]] = []
        external_rules: list[dict[str, Any]] = []

        for rule in loc["travel"]:  # original source order = precedence
            verbs = rule.get("verbs", [])
            kw = _verb_display(verbs[0], motion_map) if verbs else "(implicit)"
            cond = _cond_str(rule.get("cond"))
            at = rule.get("action_type")
            tgt = rule.get("action_target")
            if at == "goto" and tgt in members:
                exit_lines.append(f"{kw} → {tgt}{cond}")
                internal_rules.append(rule)
            elif at == "goto":
                tgt_ch = next((cid for cid, ch in graph["chapters"].items()
                               if tgt in ch["members"]), None)
                page = chapter_titles.get(tgt_ch, "?")
                exit_lines.append(f"{kw} → {tgt} · {page}{cond}")
                external_rules.append({**rule, "marker_kind": "cross"})
            elif at == "speak":
                exit_lines.append(f"{kw} → say {tgt}{cond}")
                external_rules.append({**rule, "marker_kind": "speak"})
            elif at == "special":
                exit_lines.append(f"{kw} → special({tgt}){cond}")
                external_rules.append({**rule, "marker_kind": "special"})
            else:
                exit_lines.append(f"{kw}{cond}")

        content[loc_id] = {
            "heading": heading,
            "body": body,
            "exit_lines": exit_lines,
            "internal_rules": internal_rules,
            "external_rules": external_rules,
        }
    return content


def compute_heights(content: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {
        loc_id: estimate_height(c["heading"], c["body"], c["exit_lines"])
        for loc_id, c in content.items()
    }


# ---------------------------------------------------------------------------
# draw.io generation
# ---------------------------------------------------------------------------

def _edge_style(edge_like: dict[str, Any], cross: bool) -> str:
    base = ("edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
            "jettySize=auto;html=1;endArrow=block;endFill=1;strokeWidth=1.5;")
    cond = edge_like.get("cond")
    at = edge_like.get("action_type")
    d = primary_direction_v3(edge_like)
    if at == "speak":
        return base + "strokeColor=#9E9E9E;dashed=1;"
    if at == "special":
        return base + "strokeColor=#7B1FA2;dashed=1;"
    if cross:
        col = "#000000" if cond is None else ("#1976D2" if (cond or {}).get("type") == "probability" else "#E65100")
        return base + f"strokeColor={col};dashed=1;strokeWidth=1;"
    if d in VERTICAL:
        return base + "strokeColor=#1565C0;"
    if cond is None:
        return base + "strokeColor=#000000;"
    if cond.get("type") == "probability":
        return base + "strokeColor=#1976D2;dashed=1;dashPattern=1 3;"
    return base + "strokeColor=#E65100;dashed=1;"


def _connection_points(d: str | None, lane: float) -> dict[str, str]:
    """Fixed exit/entry perimeter points per direction."""
    if d is None:
        return {}
    if d == "NORTH":
        ex, ey, nx, ny = 0.5, 0, 0.5, 1
    elif d == "SOUTH":
        ex, ey, nx, ny = 0.5, 1, 0.5, 0
    elif d == "EAST":
        ex, ey, nx, ny = 1, lane, 0, lane
    elif d == "WEST":
        ex, ey, nx, ny = 0, lane, 1, lane
    elif d == "NE":
        ex, ey, nx, ny = 1, 0.25, 0, 0.75
    elif d == "SE":
        ex, ey, nx, ny = 1, 0.75, 0, 0.25
    elif d == "SW":
        ex, ey, nx, ny = 0, 0.75, 1, 0.25
    elif d == "NW":
        ex, ey, nx, ny = 0, 0.25, 1, 0.75
    elif d == "UPWAR":
        ex, ey, nx, ny = 0.72, 0, 0.72, 1
    elif d == "DOWN":
        ex, ey, nx, ny = 0.72, 1, 0.72, 0
    else:
        return {}
    return {
        "exitX": str(ex), "exitY": str(ey), "exitDx": "0", "exitDy": "0",
        "entryX": str(nx), "entryY": str(ny), "entryDx": "0", "entryDy": "0",
    }


def _pair_lanes(internal_edges: list[dict[str, Any]]) -> dict[int, float]:
    """Assign parallel lanes when several edges share a channel between
    the same node pair (e.g. A→B east and B→A west)."""
    groups: dict[tuple, list[int]] = {}
    for i, e in enumerate(internal_edges):
        d = primary_direction_v3(e)
        if d in ("EAST", "WEST"):
            key = ("h", frozenset((e["source"], e["target"])))
        elif d in ("NORTH", "SOUTH"):
            key = ("v", frozenset((e["source"], e["target"])))
        else:
            continue
        groups.setdefault(key, []).append(i)
    lanes: dict[int, float] = {}
    for key, idxs in groups.items():
        if len(idxs) == 1:
            lanes[idxs[0]] = 0.5
        else:
            ordered = sorted(idxs, key=lambda i: (
                internal_edges[i]["source"],
                internal_edges[i]["target"],
                tuple(internal_edges[i]["verbs"])))
            table = [0.62, 0.38, 0.72, 0.28, 0.80, 0.20]
            for rank, i in enumerate(ordered):
                lanes[i] = table[min(rank, len(table) - 1)]
    return lanes


def generate_pilot(graph: dict[str, Any], out_path: Path) -> dict[str, Any]:
    """Generate the pilot drawio file; returns metrics for reporting."""
    content = build_content(graph, CHAPTER_ID)
    heights = compute_heights(content)

    hints = {}
    for node, spec in HINTS.items():
        direction, anchor = spec.split(":")
        hints[node] = direction

    layout = layout_chapter_v3(graph, CHAPTER_ID, heights, hints=hints)
    positions = layout["positions"]

    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    chapter = graph["chapters"][CHAPTER_ID]
    chapter_titles = {cid: ch["title"] for cid, ch in graph["chapters"].items()}

    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}

    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # --- page furniture ---
    title = ET.SubElement(root, "mxCell")
    title.set("id", "title")
    title.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1")
    title.set("vertex", "1"); title.set("parent", "1")
    title.set("value", f"{chapter['title']} — Pilot (Mata Hari, Mission 003)")
    g = ET.SubElement(title, "mxGeometry")
    g.set("x", "80"); g.set("y", "20"); g.set("width", "700"); g.set("height", "30"); g.set("as", "geometry")

    compass = ET.SubElement(root, "mxCell")
    compass.set("id", "compass")
    compass.set("style", "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Courier New;fontSize=12")
    compass.set("vertex", "1"); compass.set("parent", "1")
    compass.set("value", _escape("   N\n   ↑\nW ← + → E\n   ↓\n   S"))
    g = ET.SubElement(compass, "mxGeometry")
    g.set("x", "80"); g.set("y", "60"); g.set("width", "120"); g.set("height", "90"); g.set("as", "geometry")

    legend = ET.SubElement(root, "mxCell")
    legend.set("id", "legend")
    legend.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=10")
    legend.set("vertex", "1"); legend.set("parent", "1")
    legend.set("value", _escape(
        "black solid = direct compass travel\n"
        "blue solid = vertical UP/DOWN (not compass N/S)\n"
        "orange dashed = conditional · blue dotted = random %\n"
        "grey dashed = message · purple dashed = special movement\n"
        "dashed to gutter = leaves this page (marker shows exact destination)"))
    g = ET.SubElement(legend, "mxGeometry")
    g.set("x", "220"); g.set("y", "60"); g.set("width", "360"); g.set("height", "95"); g.set("as", "geometry")

    # --- location nodes ---
    node_ids: dict[str, str] = {}
    for loc_id in chapter["members"]:
        loc = loc_index[loc_id]
        c = content[loc_id]
        x, y = positions[loc_id]
        h = heights[loc_id]
        node_id = f"{CHAPTER_ID}_{loc_id}"
        node_ids[loc_id] = node_id

        label = (f"<b>{_escape(loc_id)} — {_escape(c['heading'])}</b><br><br>"
                 f"{_escape(c['body']).replace(chr(10), '<br>')}")
        if c["exit_lines"]:
            label += "<br><br><b>EXITS (source order)</b><br>" + "<br>".join(_escape(l) for l in c["exit_lines"])

        obj = ET.SubElement(root, "object")
        obj.set("label", label)
        obj.set("source_id", loc_id)
        obj.set("description_en", str(loc["description"].get("long") or ""))
        obj.set("description_es", "")
        obj.set("short_en", str(loc["description"].get("short") or ""))
        obj.set("maptag", str(loc["description"].get("maptag") or ""))
        obj.set("chapter_id", loc.get("chapter_id", ""))
        obj.set("source_reference", f"Open_Adventure.yaml locations/{loc_id}")
        obj.set("review_status", loc.get("review_status", "ok"))
        obj.set("role", loc.get("role", ""))
        obj.set("conditions", ", ".join(f"{k}={v}" for k, v in sorted(loc.get("conditions", {}).items())))
        if loc.get("objects_here"):
            obj.set("objects_here", ", ".join(loc["objects_here"]))
            tr = [o for o in loc["objects_here"] if o in treasure_objects]
            im = [o for o in loc["objects_here"] if o in immovable_objects]
            if tr: obj.set("treasures_here", ", ".join(tr))
            if im: obj.set("immovable_objects_here", ", ".join(im))
        if loc.get("sound"): obj.set("sound", str(loc["sound"]))
        if loc.get("loud"): obj.set("loud", "true")

        fill = "#F5F5F5" if loc.get("role") in ("special", "transient", "null") else "#FFFFFF"
        cell = ET.SubElement(obj, "mxCell")
        cell.set("id", node_id)
        cell.set("style", f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor=#333333;arcSize=6;{FONT}verticalAlign=top;spacingTop=2;")
        cell.set("vertex", "1"); cell.set("parent", "1")
        g = ET.SubElement(cell, "mxGeometry")
        g.set("x", str(int(x))); g.set("y", str(int(y)))
        g.set("width", str(PILOT_NODE_W)); g.set("height", str(h)); g.set("as", "geometry")

    # --- internal edges (with directional connection points) ---
    internal_edges = layout["internal_edges"]
    lanes = _pair_lanes(internal_edges)
    motion_map = graph["motion_map"]
    for i, e in enumerate(internal_edges):
        d = primary_direction_v3(e)
        lane = lanes.get(i, 0.5)
        style = _edge_style(e, cross=False)
        pts = _connection_points(d, lane)
        if pts:
            style += "".join(f"{k}={v};" for k, v in pts.items())
        style += "exitPerimeter=0;entryPerimeter=0;"

        cell = ET.SubElement(root, "mxCell")
        cell.set("id", f"ie{i}")
        cell.set("style", style)
        cell.set("edge", "1"); cell.set("parent", "1")
        cell.set("source", node_ids[e["source"]])
        cell.set("target", node_ids[e["target"]])
        verbs = e.get("verbs", [])
        lbl = ", ".join(_verb_display(v, motion_map) for v in verbs) if verbs else "(implicit)"
        lbl += _cond_str(e.get("condition"))
        cell.set("value", _escape(lbl))
        g = ET.SubElement(cell, "mxGeometry")
        g.set("relative", "1"); g.set("as", "geometry")

    # --- gutter markers for cross-page / speak / special rules ---
    gutter_x = int(max(b[0] + b[2] for b in layout["boxes"].values())) + 80
    gy = 170
    marker_count = 0
    edge_count = 0
    for loc_id in chapter["members"]:
        for rule in content[loc_id]["external_rules"]:
            marker_count += 1
            kind = rule["marker_kind"]
            cond = _cond_str(rule.get("cond"))
            verbs = rule.get("verbs", [])
            kw = _verb_display(verbs[0], motion_map) if verbs else "(implicit)"
            if kind == "cross":
                tgt = rule["action_target"]
                tgt_ch = next((cid for cid, ch in graph["chapters"].items()
                               if tgt in ch["members"]), None)
                page = chapter_titles.get(tgt_ch, "?")
                mlabel = f"<b>→ {_escape(tgt)}</b><br><i>{_escape(page)}</i>{_escape(cond)}"
                mstyle = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F57C00;arcSize=6;" + FONT
                mw, mh = 250, 60
            elif kind == "speak":
                mlabel = f"<b>MESSAGE</b><br>say {_escape(str(rule['action_target']))}{_escape(cond)}"
                mstyle = "rounded=1;whiteSpace=wrap;html=1;fillColor=#EEEEEE;strokeColor=#9E9E9E;arcSize=6;" + FONT
                mw, mh = 250, 60
            else:
                mlabel = f"<b>SPECIAL CASE</b><br>special({_escape(str(rule['action_target']))}){_escape(cond)}"
                mstyle = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#7B1FA2;arcSize=6;" + FONT
                mw, mh = 250, 60

            mid = f"xp_{loc_id}_{marker_count}"
            m = ET.SubElement(root, "mxCell")
            m.set("id", mid)
            m.set("style", mstyle)
            m.set("vertex", "1"); m.set("parent", "1")
            m.set("value", mlabel)
            g = ET.SubElement(m, "mxGeometry")
            g.set("x", str(gutter_x)); g.set("y", str(gy))
            g.set("width", str(mw)); g.set("height", str(mh)); g.set("as", "geometry")
            gy += mh + 30

            cell = ET.SubElement(root, "mxCell")
            cell.set("id", f"xe{edge_count}")
            cell.set("style", _edge_style(rule, cross=True))
            cell.set("edge", "1"); cell.set("parent", "1")
            cell.set("source", node_ids[loc_id])
            cell.set("target", mid)
            cell.set("value", _escape(kw + cond))
            g = ET.SubElement(cell, "mxGeometry")
            g.set("relative", "1"); g.set("as", "geometry")
            edge_count += 1

    # --- provenance ---
    total_rules = sum(len(loc_index[m]["travel"]) for m in chapter["members"])
    prov = ET.SubElement(root, "mxCell")
    prov.set("id", "provenance")
    prov.set("style", "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=9;fontStyle=2")
    prov.set("vertex", "1"); prov.set("parent", "1")
    prov.set("value", _escape(
        "Source: Open_Adventure.yaml (BSD-2-Clause, E. S. Raymond / Open Adventure) — canonical. "
        f"Pilot: {len(chapter['members'])} locations, {total_rules} travel rules preserved in source order. "
        "Editorial hint: WESTBANK placed west of EASTBANK per fissure descriptions. "
        "Generated by Mata Hari (Mission 003). North = up = smaller Y."))
    g = ET.SubElement(prov, "mxGeometry")
    g.set("x", "80"); g.set("y", str(gy + 10)); g.set("width", "700"); g.set("height", "60"); g.set("as", "geometry")

    page_w = max(layout["width"], gutter_x + 250 + 80)
    page_h = max(layout["height"], gy + 90)

    mxfile = ET.Element("mxfile")
    mxfile.set("host", "Open Adventure RPG Archaeology tooling")
    mxfile.set("agent", "007-mata-hari-pilot")
    mxfile.set("type", "device")
    mxfile.set("version", "24.7.0")
    diag = ET.SubElement(mxfile, "diagram")
    diag.set("id", CHAPTER_ID)
    diag.set("name", chapter["title"] + " — Pilot")
    model = ET.SubElement(diag, "mxGraphModel")
    for k, v in {"dx": "1422", "dy": "762", "grid": "1", "gridSize": "10", "guides": "1",
                 "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
                 "pageScale": "1", "pageWidth": str(page_w), "pageHeight": str(page_h),
                 "math": "0", "shadow": "0"}.items():
        model.set(k, v)
    model.append(root)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(out_path, encoding="utf-8", xml_declaration=True)

    return {
        "layout": layout,
        "content": content,
        "heights": heights,
        "page_width": page_w,
        "page_height": page_h,
        "internal_edges": len(internal_edges),
        "markers": marker_count,
        "total_rules": total_rules,
    }


# ---------------------------------------------------------------------------
# Validation + comparison
# ---------------------------------------------------------------------------

def evaluate_constraints_v3(internal_edges: list[dict[str, Any]],
                            positions: dict[str, tuple[float, float]]) -> dict[str, Any]:
    """Corrected constraint evaluation (UPWAR recognised)."""
    satisfied = 0
    violated = 0
    violations = []
    for e in internal_edges:
        d = primary_direction_v3(e)
        if d is None:
            continue
        sx, sy = positions[e["source"]]
        tx, ty = positions[e["target"]]
        dx, dy = tx - sx, ty - sy
        vx, vy = DIRECTION_SIGNS[d]
        ok = (dx > 1 if vx > 0 else dx < -1 if vx < 0 else True) and \
             (dy > 1 if vy > 0 else dy < -1 if vy < 0 else True)
        if ok:
            satisfied += 1
        else:
            violated += 1
            violations.append({
                "source": e["source"], "target": e["target"], "direction": d,
                "delta": (round(dx, 1), round(dy, 1)),
            })
    return {"satisfied": satisfied, "violated": violated, "violations": violations}


def _seg_hits_box(p1, p2, box, skip_boxes) -> bool:
    """Segment vs axis-aligned rect intersection (Liang-Barsky style)."""
    (x1, y1), (x2, y2) = p1, p2
    bx, by, bw, bh = box
    if box in skip_boxes:
        return False
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx), (dx, bx + bw - x1), (-dy, y1 - by), (dy, by + bh - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1: return False
                if r > t0: t0 = r
            else:
                if r < t0: return False
                if r < t1: t1 = r
    return True


def _l_paths(edges, positions, heights, lanes_map=None) -> list[list[tuple]]:
    """Approximate orthogonal routes: exit point -> entry point, best L-shape."""
    boxes = {n: (positions[n][0], positions[n][1], float(NODE_W), float(heights.get(n, MIN_H)))
             for n in positions}
    paths = []
    for i, e in enumerate(edges):
        d = primary_direction_v3(e)
        lane = (lanes_map or {}).get(i, 0.5)
        s, t = e["source"], e["target"]
        sb, tb = boxes[s], boxes[t]
        if d == "NORTH":
            p1 = (sb[0] + sb[2] * 0.5, sb[1]); p2 = (tb[0] + tb[2] * 0.5, tb[1] + tb[3])
        elif d == "SOUTH":
            p1 = (sb[0] + sb[2] * 0.5, sb[1] + sb[3]); p2 = (tb[0] + tb[2] * 0.5, tb[1])
        elif d == "EAST":
            p1 = (sb[0] + sb[2], sb[1] + sb[3] * lane); p2 = (tb[0], tb[1] + tb[3] * lane)
        elif d == "WEST":
            p1 = (sb[0], sb[1] + sb[3] * lane); p2 = (tb[0] + tb[2], tb[1] + tb[3] * lane)
        elif d == "UPWAR":
            p1 = (sb[0] + sb[2] * 0.72, sb[1]); p2 = (tb[0] + tb[2] * 0.72, tb[1] + tb[3])
        elif d == "DOWN":
            p1 = (sb[0] + sb[2] * 0.72, sb[1] + sb[3]); p2 = (tb[0] + tb[2] * 0.72, tb[1])
        else:
            p1 = (sb[0] + sb[2] / 2, sb[1] + sb[3] / 2)
            p2 = (tb[0] + tb[2] / 2, tb[1] + tb[3] / 2)
        cand = [
            [(p1, (p2[0], p1[1])), ((p2[0], p1[1]), p2)],
            [(p1, (p1[0], p2[1])), ((p1[0], p2[1]), p2)],
        ]
        def hits(segs):
            n = 0
            for seg in segs:
                for bn, bb in boxes.items():
                    if bn in (s, t):
                        continue
                    if _seg_hits_box(seg[0], seg[1], bb, skip_boxes=()):
                        n += 1
            return n
        best = min(cand, key=hits)
        paths.append(best)
    return paths


def _seg_intersect(p1, p2, p3, p4) -> bool:
    def orient(a, b, c):
        v = (b[1] - a[1]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[1] - a[1])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    o1, o2 = orient(p1, p2, p3), orient(p1, p2, p4)
    o3, o4 = orient(p3, p4, p1), orient(p3, p4, p2)
    return o1 * o2 < 0 and o3 * o4 < 0


def measure_layout(internal_edges, positions, heights, width, height) -> dict[str, Any]:
    """Same measurement definitions for baseline and pilot."""
    ev = evaluate_constraints_v3(internal_edges, positions)
    boxes = {n: (positions[n][0], positions[n][1], float(NODE_W), float(heights.get(n, MIN_H)))
             for n in positions}
    overlaps = 0
    names = sorted(boxes)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ba, bb = boxes[a], boxes[b]
            if not (ba[0] + ba[2] <= bb[0] or bb[0] + bb[2] <= ba[0] or
                    ba[1] + ba[3] <= bb[1] or bb[1] + bb[3] <= ba[1]):
                overlaps += 1

    lanes = _pair_lanes(internal_edges)
    paths = _l_paths(internal_edges, positions, heights, lanes)
    box_hits = 0
    for pi, path in enumerate(paths):
        s, t = internal_edges[pi]["source"], internal_edges[pi]["target"]
        for seg in path:
            for bn, bb in boxes.items():
                if bn in (s, t):
                    continue
                if _seg_hits_box(seg[0], seg[1], bb, skip_boxes=()):
                    box_hits += 1
                    break  # count once per segment
    crossings = 0
    flat = []
    for i, path in enumerate(paths):
        for seg in path:
            flat.append((i, seg))
    for i in range(len(flat)):
        for j in range(i):
            (ei, s1), (ej, s2) = flat[i], flat[j]
            if ei == ej:
                continue
            # Skip edge pairs that share an endpoint node: near-endpoint
            # crossings are artifacts of the crude L-path model.
            if {internal_edges[ei]["source"], internal_edges[ei]["target"]} & \
               {internal_edges[ej]["source"], internal_edges[ej]["target"]}:
                continue
            if _seg_intersect(s1[0], s1[1], s2[0], s2[1]):
                crossings += 1

    return {
        "applicable_constraints": ev["satisfied"] + ev["violated"],
        "satisfied": ev["satisfied"],
        "violated": ev["violated"],
        "violations": ev["violations"],
        "box_overlaps": overlaps,
        "edge_box_intersections": box_hits,
        "edge_crossings": crossings,
        "width": width,
        "height": height,
    }


def compare(graph: dict[str, Any], pilot: dict[str, Any]) -> dict[str, Any]:
    """Baseline V2 vs pilot, identical measurement definitions."""
    members, internal_edges = _node_edges_for_chapter(graph, CHAPTER_ID)

    baseline = layout_chapter(graph, CHAPTER_ID)  # V2 algorithm, untouched
    baseline_heights = {m: 150 for m in members}  # V2 fixed box height
    baseline_metrics = measure_layout(
        internal_edges, baseline["positions"], baseline_heights,
        baseline["width"], baseline["height"])

    pilot_metrics = measure_layout(
        internal_edges, pilot["layout"]["positions"], pilot["heights"],
        pilot["page_width"], pilot["page_height"])

    # Text overflow: same content, different box heights.
    content = pilot["content"]
    needed = compute_heights(content)
    baseline_overflow = {m: needed[m] - 150 for m in members if needed[m] > 150}
    pilot_overflow = {m: needed[m] - pilot["heights"][m] for m in members
                      if needed[m] > pilot["heights"][m]}

    return {
        "baseline_v2": baseline_metrics,
        "baseline_v2_text_overflow_nodes": len(baseline_overflow),
        "baseline_v2_text_overflow_detail": baseline_overflow,
        "pilot": pilot_metrics,
        "pilot_text_overflow_nodes": len(pilot_overflow),
        "proven_contradictions": pilot["layout"]["constraints"]["dropped"],
        "unresolved_overlaps": pilot["layout"]["unresolved_overlaps"],
    }


def validate_pilot(graph: dict[str, Any], path: Path) -> dict[str, Any]:
    """Structural validation of the pilot drawio file."""
    tree = ET.parse(path)
    mxfile = tree.getroot()
    root = mxfile.find("diagram/mxGraphModel/root")

    locs = [o for o in root.iter("object") if o.get("source_id")]
    ids = [o.get("source_id") for o in locs]
    edges = [c for c in root.iter("mxCell") if c.get("edge") == "1"]
    vertices = [c for c in root.iter("mxCell") if c.get("vertex") == "1"]

    members = set(graph["chapters"][CHAPTER_ID]["members"])
    source_long = {loc["source_id"]: (loc["description"].get("long") or "")
                   for loc in graph["locations"]}

    desc_ok = all(o.get("description_en") == source_long[o.get("source_id")]
                  for o in locs)

    # Box overlap among location nodes.
    boxes = []
    for o in locs:
        cell = o.find("mxCell")
        gm = cell.find("mxGeometry")
        boxes.append((o.get("source_id"),
                      float(gm.get("x")), float(gm.get("y")),
                      float(gm.get("width")), float(gm.get("height"))))
    overlaps = 0
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if not (a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1] or
                    a[2] + a[4] <= b[2] or b[2] + b[4] <= a[2]):
                overlaps += 1

    total_rules = sum(len(l["travel"]) for l in graph["locations"]
                      if l["source_id"] in members)

    return {
        "locations_present": len(locs),
        "expected_locations": len(members),
        "location_ids_match": set(ids) == members,
        "duplicate_node_ids": len(ids) != len(set(ids)),
        "edges_total": len(edges),
        "internal_edges_expected": 32,
        "markers_expected": total_rules - 32,
        "total_rules_expected": total_rules,
        "descriptions_roundtrip": desc_ok,
        "location_box_overlaps": overlaps,
        "xml_valid": True,
    }


if __name__ == "__main__":
    import json
    root_dir = Path(__file__).resolve().parent.parent
    with (root_dir / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
        graph = json.load(f)
    out = root_dir / "output" / "pilot" / "CH_ENTRY_MataHari.drawio"
    pilot = generate_pilot(graph, out)
    validation = validate_pilot(graph, out)
    comparison = compare(graph, pilot)
    print(json.dumps({
        "file": str(out),
        "validation": validation,
        "comparison": comparison,
    }, indent=2))
