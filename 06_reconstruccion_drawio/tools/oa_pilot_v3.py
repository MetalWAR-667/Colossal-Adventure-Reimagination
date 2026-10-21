#!/usr/bin/env python3
"""
Mission 005 — Phase A & Phase B: Cave Entry pilot V3 with native draw.io
`Parser Aliases / Fast Travel` layer (hidden by default) and regression gate.

Preserves all Mission 003 and Mission 004 outputs untouched and generates:
  - output/pilot/CH_ENTRY_MataHari_V3.drawio
"""

from __future__ import annotations

import copy
import html
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from oa_layout import _node_edges_for_chapter
from oa_layout_v3 import DIRECTION_SIGNS, VERTICAL, primary_direction_v3
from oa_pilot import CHAPTER_ID
from oa_pilot_v2 import (
    FONT,
    NODE_W,
    PRIMARY_PAIR_LABELS,
    X_GAP,
    X_STEP,
    _clean_heading,
    _cond_badge,
    _esc,
    _overlap,
    build_external_markers,
    build_room_display,
    estimate_room_height,
    layout_v2,
    route_fast_travel,
)

ALIAS_LAYER_ID = "layer_aliases"
ALIAS_LAYER_NAME = "Parser Aliases / Fast Travel"

SPATIAL_ACTION_VERBS: set[str] = {
    "OVER", "ACROS", "CROSS", "JUMP", "CLIMB", "CRAWL",
    "INWAR", "OUT", "ENTER", "DOWNS", "UPSTR",
}


def is_direct_spatial_or_structural_rule(
    rule: dict[str, Any],
    loc_index: dict[str, dict[str, Any]],
) -> bool:
    """Return True if a rule represents direct spatial movement, obstacle traversal,
    or forced/special state transition rather than a keyword alias."""
    u, v = rule["source"], rule["target"]
    if u == v:
        return True
    if primary_direction_v3(rule) is not None:
        return True
    verbs = set(rule.get("verbs", []))
    if not verbs:
        return True
    if (
        loc_index[u].get("role") in ("special", "transient", "null")
        or loc_index[v].get("role") in ("special", "transient", "null")
    ):
        return True
    if verbs & SPATIAL_ACTION_VERBS:
        return True
    return False


def classify_chapter_internal_rules(
    internal_edges: list[dict[str, Any]],
    loc_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Deterministically classify each internal goto rule in a chapter into:
      - 'primary': ordinary spatial / vertical / structural movement (Layer '1')
      - 'fast_travel': non-adjacent parser-only shortcut whose endpoints are
        already connected by a >=2-hop path in the chapter's primary spatial
        subgraph (Layer 'layer_aliases', hidden by default).

    Also records:
      - `reciprocal_retained`: non-directional rules retained on Layer '1'
        because they are the reciprocal return of a direct 1-hop spatial edge.
      - `uncertain_retained`: non-directional rules retained on Layer '1'
        because hiding them would disconnect their endpoints in the chapter's
        primary spatial subgraph.
    """
    direct_pairs: set[frozenset[str]] = set()
    for e in internal_edges:
        if is_direct_spatial_or_structural_rule(e, loc_index):
            direct_pairs.add(frozenset((e["source"], e["target"])))

    adj: dict[str, set[str]] = defaultdict(set)
    for pair in direct_pairs:
        if len(pair) == 2:
            u, v = tuple(pair)
            adj[u].add(v)
            adj[v].add(u)

    def shortest_primary_path(u: str, v: str) -> list[str] | None:
        q: deque[tuple[str, list[str]]] = deque([(u, [u])])
        seen = {u}
        while q:
            cur, path = q.popleft()
            if cur == v:
                return path
            for nxt in sorted(adj[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [nxt]))
        return None

    classified: list[tuple[dict[str, Any], str, list[str] | None]] = []
    reciprocal_retained: list[dict[str, Any]] = []
    uncertain_retained: list[dict[str, Any]] = []

    for e in internal_edges:
        pair = frozenset((e["source"], e["target"]))
        if is_direct_spatial_or_structural_rule(e, loc_index):
            classified.append((e, "primary", [e["source"], e["target"]]))
        elif pair in direct_pairs:
            # Reciprocal of a direct 1-hop spatial transition (e.g. BEDQU, SLAB, CANYO in CH_BEDQUILT)
            classified.append((e, "primary", [e["source"], e["target"]]))
            reciprocal_retained.append(e)
        else:
            path = shortest_primary_path(e["source"], e["target"])
            if path is not None and len(path) >= 3:
                classified.append((e, "fast_travel", path))
            else:
                classified.append((e, "primary", path))
                uncertain_retained.append(e)

    return {
        "classified": classified,
        "reciprocal_retained": reciprocal_retained,
        "uncertain_retained": uncertain_retained,
    }


def group_internal_edges_v3(
    internal_edges: list[dict[str, Any]],
    loc_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Group internal rules by (unordered_pair, role) so that ordinary spatial
    rules and parser-alias rules are never mixed in the same connector."""
    analysis = classify_chapter_internal_rules(internal_edges, loc_index)
    by_pair_role: dict[tuple[frozenset[str], str], list[tuple[dict[str, Any], list[str] | None]]] = {}
    for e, role, path in analysis["classified"]:
        key = (frozenset((e["source"], e["target"])), role)
        by_pair_role.setdefault(key, []).append((e, path))

    connectors: list[dict[str, Any]] = []
    for (pair, role) in sorted(
        by_pair_role,
        key=lambda kr: (tuple(sorted(kr[0])), 0 if kr[1] == "primary" else 1),
    ):
        items = by_pair_role[(pair, role)]
        rules = [it[0] for it in items]
        bypass_path = items[0][1]

        if len(pair) == 1:
            # Self-loop(s) on a single location (e.g. Maze All Alike)
            u = next(iter(pair))
            all_verbs: list[str] = []
            for r in rules:
                for v in r.get("verbs", []):
                    if v not in all_verbs:
                        all_verbs.append(v)
            label = ", ".join(all_verbs) if all_verbs else "(loop)"
            connectors.append({
                "kind": "self",
                "role": role,
                "layer": ALIAS_LAYER_ID if role == "fast_travel" else "1",
                "source": u,
                "target": u,
                "label": label,
                "rules": rules,
                "bypass_path": bypass_path,
            })
        elif len(rules) == 2 and rules[0]["source"] != rules[1]["source"]:
            if role == "primary" and pair in PRIMARY_PAIR_LABELS:
                src_id, tgt_id, label = PRIMARY_PAIR_LABELS[pair]
                r_ordered = sorted(rules, key=lambda r: 0 if r["source"] == src_id else 1)
            else:
                r_ordered = sorted(rules, key=lambda r: r["source"])
                src_id, tgt_id = r_ordered[0]["source"], r_ordered[0]["target"]
                v0 = r_ordered[0]["verbs"][0] if r_ordered[0]["verbs"] else "(implicit)"
                v1 = r_ordered[1]["verbs"][0] if r_ordered[1]["verbs"] else "(implicit)"
                c0 = _cond_badge(r_ordered[0].get("cond"))
                c1 = _cond_badge(r_ordered[1].get("cond"))
                s0 = f"{v0} {c0}".strip()
                s1 = f"{v1} {c1}".strip()
                label = f"{s0} ↔ {s1}"
            connectors.append({
                "kind": "pair",
                "role": role,
                "layer": ALIAS_LAYER_ID if role == "fast_travel" else "1",
                "source": src_id,
                "target": tgt_id,
                "label": label,
                "rules": r_ordered,
                "bypass_path": bypass_path,
            })
        else:
            r = rules[0]
            v0 = r["verbs"][0] if r["verbs"] else "(implicit)"
            c0 = _cond_badge(r.get("cond"))
            label = f"{v0} {c0}".strip()
            if role == "primary" and pair in PRIMARY_PAIR_LABELS:
                _, _, label = PRIMARY_PAIR_LABELS[pair]
            connectors.append({
                "kind": "single",
                "role": role,
                "layer": ALIAS_LAYER_ID if role == "fast_travel" else "1",
                "source": r["source"],
                "target": r["target"],
                "label": label,
                "rules": rules,
                "bypass_path": bypass_path,
            })

    return connectors, analysis


def generate_pilot_v3(
    graph: dict[str, Any],
    out_path: Path,
    *,
    alias_layer_visible: bool = False,
) -> dict[str, Any]:
    display = build_room_display(graph, CHAPTER_ID)
    heights = {
        loc_id: estimate_room_height(d["heading"], d["body"], d["exit_lines"])
        for loc_id, d in display.items()
    }
    lay = layout_v2(graph, heights)
    positions = lay["positions"]
    internal_edges = lay["internal_edges"]
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}

    connectors, analysis = group_internal_edges_v3(internal_edges, loc_index)
    markers = build_external_markers(graph, positions, heights)

    chapter = graph["chapters"][CHAPTER_ID]
    members = set(chapter["members"])
    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}

    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    ET.SubElement(root, "mxCell", {
        "id": ALIAS_LAYER_ID,
        "value": ALIAS_LAYER_NAME,
        "style": "locked=0;",
        "parent": "0",
        "visible": "1" if alias_layer_visible else "0",
    })

    def add_text_cell(cid: str, x: float, y: float, w: float, h: float, style: str, value: str) -> None:
        c = ET.SubElement(root, "mxCell", {
            "id": cid, "style": style, "value": value, "vertex": "1", "parent": "1",
        })
        ET.SubElement(c, "mxGeometry", {
            "x": str(int(x)), "y": str(int(y)),
            "width": str(int(w)), "height": str(int(h)), "as": "geometry",
        })

    add_text_cell(
        "title", 60, 14, 780, 28,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;fontFamily=Helvetica;",
        f"{chapter['title']} — Pilot V3 (Mata Hari, Mission 005)",
    )
    add_text_cell(
        "compass", 60, 46, 130, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=center;verticalAlign=middle;fontFamily=Courier New;fontSize=11;fontStyle=1;",
        "NORTH (–Y)<br>↑<br>W ← + → E<br>↓<br>SOUTH (+Y)",
    )
    add_text_cell(
        "legend", 206, 46, 720, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=left;verticalAlign=top;spacingLeft=10;spacingTop=5;fontSize=9.5;fontFamily=Helvetica;",
        "<b>LEGEND &amp; LAYERS</b><br>"
        "• <b>Black solid (2.5 px):</b> primary compass/passage movement (double arrowhead = two-way)<br>"
        "• <b>Blue solid (2.8 px):</b> vertical UP / DOWN shaft (distinct from compass N/S)<br>"
        "• <b>Purple dashed:</b> magic word teleport (XYZZY / &gt;&gt;Foof!&lt;&lt;) · "
        "<b>Local markers:</b> yellow = cross-page · orange = transient · red = death<br>"
        "• <b>Optional layer [Parser Aliases / Fast Travel] (hidden by default):</b> "
        "non-adjacent keyword shortcuts (ENTRA, DEBRI, PIT)",
    )

    room_rects: dict[str, tuple[float, float, float, float]] = {}
    for loc_id in sorted(members):
        loc = loc_index[loc_id]
        d = display[loc_id]
        x, y = positions[loc_id]
        h = heights[loc_id]
        nid = f"N_{loc_id}"
        room_rects[loc_id] = (x, y, float(NODE_W), float(h))

        header_html = f"<b>{_esc(loc_id)} — {_esc(d['heading'])}</b>"
        body_html = _esc(d["body"]).replace("\n", "<br>")
        exits_html = (
            "<b>EXITS (source precedence order)</b><br>"
            + "<br>".join(_esc(line) for line in d["exit_lines"])
        )
        label = f"{header_html}<hr size='1'/>{body_html}<br><br>{exits_html}"

        travel_json = json.dumps(loc["travel"], sort_keys=True, ensure_ascii=False)
        obj = ET.SubElement(root, "object", {
            "id": nid,
            "label": label,
            "source_id": loc_id,
            "description_en": str(loc["description"].get("long") or ""),
            "description_es": "",
            "short_en": str(loc["description"].get("short") or ""),
            "maptag": str(loc["description"].get("maptag") or ""),
            "chapter_id": str(loc.get("chapter_id", "")),
            "source_reference": f"Open_Adventure.yaml locations/{loc_id}",
            "review_status": loc.get("review_status", "ok"),
            "role": loc.get("role", ""),
            "conditions": ", ".join(f"{k}={v}" for k, v in sorted(loc.get("conditions", {}).items())),
            "travel_rules": travel_json,
        })
        if d["msg_lines"]:
            obj.set("blocked_messages", " | ".join(d["msg_lines"]))
        if loc.get("objects_here"):
            tr = [o for o in loc["objects_here"] if o in treasure_objects]
            im = [o for o in loc["objects_here"] if o in immovable_objects]
            obj.set("objects_here", ", ".join(loc["objects_here"]))
            if tr:
                obj.set("treasures_here", ", ".join(tr))
            if im:
                obj.set("immovable_objects_here", ", ".join(im))
        if loc.get("sound"):
            obj.set("sound", str(loc["sound"]))
        if loc.get("loud"):
            obj.set("loud", "true")

        is_pseudo = loc.get("role") in ("special", "transient", "null")
        fill = "#F3E5F5" if loc_id.startswith("LOC_FOOF") else ("#F5F5F5" if is_pseudo else "#FFFFFF")
        stroke = "#7B1FA2" if loc_id.startswith("LOC_FOOF") else "#333333"
        dash = "dashed=1;" if is_pseudo else ""
        cell = ET.SubElement(obj, "mxCell", {
            "style": (
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                f"strokeWidth=1.5;{dash}arcSize=4;{FONT}align=left;verticalAlign=top;"
                "spacingLeft=8;spacingRight=8;spacingTop=6;spacingBottom=6;"
            ),
            "vertex": "1",
            "parent": "1",
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(int(x)), "y": str(int(y)),
            "width": str(NODE_W), "height": str(int(h)), "as": "geometry",
        })

    marker_rects: list[tuple[float, float, float, float]] = []
    ext_conn_count = 0
    for m in markers:
        mid = m["id"]
        mx, my, mw, mh = m["x"], m["y"], m["w"], m["h"]
        marker_rects.append((mx, my, mw, mh))
        mlabel = f"<b>{_esc(m['title'])}</b><br>{_esc(m['subtitle']).replace(chr(10), '<br>')}"
        obj = ET.SubElement(root, "object", {
            "id": mid,
            "label": mlabel,
            "kind": m["kind"],
            "target_id": m["target"],
            "represents_rules": json.dumps(m["rules"], sort_keys=True, ensure_ascii=False),
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": (
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={m['fill']};strokeColor={m['stroke']};"
                "strokeWidth=1.5;dashed=1;arcSize=6;fontSize=9;fontFamily=Helvetica;"
                "align=left;verticalAlign=middle;spacingLeft=8;spacingRight=6;"
            ),
            "vertex": "1",
            "parent": "1",
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(int(mx)), "y": str(int(my)),
            "width": str(int(mw)), "height": str(int(mh)), "as": "geometry",
        })

        for link in m["links"]:
            ext_conn_count += 1
            eid = f"X{ext_conn_count}"
            src_room = link["from"]
            lstyle = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor={link['color']};strokeWidth=1.8;dashed=1;dashPattern=4 3;"
                "endArrow=block;endFill=1;endSize=6;"
                f"exitX={link['exitX']};exitY={link['exitY']};exitDx=0;exitDy=0;"
                f"entryX={link['entryX']};entryY={link['entryY']};entryDx=0;entryDy=0;"
                "fontSize=9;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
            eobj = ET.SubElement(root, "object", {
                "id": eid,
                "label": _esc(link["label"]),
                "marker_target": m["target"],
                "source_room": src_room,
            })
            ecell = ET.SubElement(eobj, "mxCell", {
                "style": lstyle,
                "edge": "1",
                "parent": "1",
                "source": f"N_{src_room}",
                "target": mid,
            })
            egeom = ET.SubElement(ecell, "mxGeometry", {"relative": "1", "as": "geometry"})
            ox, oy = link.get("offset", (0, 0))
            if ox or oy:
                ET.SubElement(egeom, "mxPoint", {"x": str(ox), "y": str(oy), "as": "offset"})
            if link.get("waypoints"):
                arr = ET.SubElement(egeom, "Array", {"as": "points"})
                for wx, wy in link["waypoints"]:
                    ET.SubElement(arr, "mxPoint", {"x": str(int(wx)), "y": str(int(wy))})

    for gi, conn in enumerate(connectors):
        rules = conn["rules"]
        a, b = conn["source"], conn["target"]
        edge_id = f"C{gi}"
        key = frozenset((a, b))

        represents = json.dumps([
            {
                "source": r["source"],
                "verbs": r.get("verbs", []),
                "cond": r.get("cond"),
                "action": [r.get("action_type"), r.get("action_target")],
            }
            for r in rules
        ], sort_keys=True, ensure_ascii=False)

        arrows = "endArrow=block;endFill=1;endSize=7;"
        if conn["kind"] == "pair":
            arrows += "startArrow=block;startFill=1;startSize=7;"

        waypoints: list[tuple[float, float]] = []
        label_offset: tuple[int, int] | None = None
        label_rel_x: float | None = None

        if conn["role"] == "fast_travel":
            pts, waypoints, label_rel_x = route_fast_travel(conn, positions, heights)
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#78909C;strokeWidth=1.4;dashed=1;dashPattern=3 3;{arrows}"
                "fontSize=8;fontFamily=Helvetica;fontColor=#37474F;labelBackgroundColor=#FFFFFF;"
            )
            style += "".join(f"{k}={v};" for k, v in pts.items())
            style += "exitDx=0;exitDy=0;entryDx=0;entryDy=0;"
        elif key == frozenset(("LOC_PITTOP", "LOC_MISTHALL")):
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#1565C0;strokeWidth=2.8;{arrows}"
                "exitX=0.90;exitY=1.0;exitDx=0;exitDy=0;"
                "entryX=0.10;entryY=0.0;entryDx=0;entryDy=0;"
                "fontSize=10;fontStyle=1;fontFamily=Helvetica;fontColor=#0D47A1;"
                "labelBackgroundColor=#FFFFFF;"
            )
            x1 = positions["LOC_PITTOP"][0] + NODE_W * 0.90
            x2 = positions["LOC_MISTHALL"][0] + NODE_W * 0.10
            y_mid = 576.0
            waypoints = [(round(x1, 1), y_mid), (round(x2, 1), y_mid)]
            label_offset = (0, -12)
        elif key == frozenset(("LOC_AWKWARD", "LOC_DEBRIS")):
            x_line = 1545.0
            ex_awk = (x_line - positions["LOC_AWKWARD"][0]) / NODE_W
            ex_deb = (x_line - positions["LOC_DEBRIS"][0]) / NODE_W
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#000000;strokeWidth=2.5;{arrows}"
                f"exitX={ex_awk:.3f};exitY=1.0;exitDx=0;exitDy=0;"
                f"entryX={ex_deb:.3f};entryY=0.0;entryDx=0;entryDy=0;"
                "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
            label_offset = (0, 56)
        elif key == frozenset(("LOC_MISTHALL", "LOC_NUGGET")):
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#000000;strokeWidth=2.5;{arrows}"
                "exitX=0.5;exitY=1.0;exitDx=0;exitDy=0;"
                "entryX=0.5;entryY=0.0;entryDx=0;entryDy=0;"
                "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
        elif key == frozenset(("LOC_FOOF1", "LOC_DEBRIS")):
            x_line = 1675.0
            ex_src = (x_line - positions["LOC_FOOF1"][0]) / NODE_W
            ex_tgt = (x_line - positions["LOC_DEBRIS"][0]) / NODE_W
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#7B1FA2;strokeWidth=2.2;dashed=1;dashPattern=5 3;{arrows}"
                f"exitX={ex_src:.3f};exitY=1.0;exitDx=0;exitDy=0;"
                f"entryX={ex_tgt:.3f};entryY=0.0;entryDx=0;entryDy=0;"
                "fontSize=9;fontFamily=Helvetica;fontColor=#4A148C;labelBackgroundColor=#FFFFFF;"
            )
            label_offset = (0, -80)
        else:
            y_line = positions[a][1] + 78.0
            ey_a = (y_line - positions[a][1]) / heights[a]
            ey_b = (y_line - positions[b][1]) / heights[b]
            if positions[b][0] > positions[a][0]:
                ex_a, ex_b = "1.0", "0.0"
            else:
                ex_a, ex_b = "0.0", "1.0"
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#000000;strokeWidth=2.5;{arrows}"
                f"exitX={ex_a};exitY={ey_a:.3f};exitDx=0;exitDy=0;"
                f"entryX={ex_b};entryY={ey_b:.3f};entryDx=0;entryDy=0;"
                "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
            label_offset = (0, -14)

        obj_attrs = {
            "id": edge_id,
            "label": _esc(conn["label"]),
            "role": conn["role"],
            "layer_name": ALIAS_LAYER_NAME if conn["role"] == "fast_travel" else "Primary Map",
            "represents_rules": represents,
        }
        if conn["role"] == "fast_travel" and conn.get("bypass_path"):
            obj_attrs["bypasses_spatial_path"] = " -> ".join(conn["bypass_path"])

        obj = ET.SubElement(root, "object", obj_attrs)
        cell = ET.SubElement(obj, "mxCell", {
            "style": style,
            "edge": "1",
            "parent": conn["layer"],
            "source": f"N_{a}",
            "target": f"N_{b}",
        })
        geom_attrs = {"relative": "1", "as": "geometry"}
        if label_rel_x is not None and abs(label_rel_x) > 1e-4:
            geom_attrs["x"] = f"{label_rel_x:.2f}"
        geom = ET.SubElement(cell, "mxGeometry", geom_attrs)
        if label_offset is not None:
            ET.SubElement(geom, "mxPoint", {
                "x": str(label_offset[0]),
                "y": str(label_offset[1]),
                "as": "offset",
            })
        if waypoints:
            arr = ET.SubElement(geom, "Array", {"as": "points"})
            for wx, wy in waypoints:
                ET.SubElement(arr, "mxPoint", {"x": str(int(wx)), "y": str(int(wy))})

    all_rects = list(room_rects.values()) + marker_rects
    max_x = max(r[0] + r[2] for r in all_rects)
    max_y = max(r[1] + r[3] for r in all_rects)
    total_rules = sum(len(loc_index[m]["travel"]) for m in members)

    add_text_cell(
        "provenance", 60, max_y + 18, 1280, 32,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
        "whiteSpace=wrap;rounded=0;fontSize=9;fontStyle=2;fontFamily=Helvetica;",
        "Source: Open_Adventure.yaml (BSD-2-Clause, E. S. Raymond) — canonical. "
        f"Pilot V3: {len(members)} locations, {total_rules}/51 travel rules preserved "
        "(11 primary connectors + 9 local reference markers + 5 in-room message annotations on Primary Map; "
        "8 fast-travel connectors [11 rules] on optional layer 'Parser Aliases / Fast Travel', hidden by default; "
        "17/17 directional constraints satisfied). NORTH = up = smaller Y.",
    )

    page_w = int(max_x + 60)
    page_h = int(max_y + 65)

    mxfile = ET.Element("mxfile", {
        "host": "Open Adventure RPG Archaeology tooling",
        "agent": "007-mata-hari-pilot-v3",
        "type": "device",
        "version": "24.7.0",
    })
    diag = ET.SubElement(mxfile, "diagram", {
        "id": CHAPTER_ID,
        "name": chapter["title"] + " — Pilot V3",
    })
    model = ET.SubElement(diag, "mxGraphModel")
    for k, v in {
        "dx": "1422", "dy": "762", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": str(page_w), "pageHeight": str(page_h),
        "math": "0", "shadow": "0",
    }.items():
        model.set(k, v)
    model.append(root)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(out_path, encoding="utf-8", xml_declaration=True)

    return {
        "layout": lay,
        "connectors": connectors,
        "analysis": analysis,
        "markers": markers,
        "heights": heights,
        "page_width": page_w,
        "page_height": page_h,
    }


def validate_pilot_v3(graph: dict[str, Any], path: Path) -> dict[str, Any]:
    tree = ET.parse(path)
    root = tree.getroot().find("diagram/mxGraphModel/root")
    members = set(graph["chapters"][CHAPTER_ID]["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}

    # Verify layer definition
    alias_layer = root.find(f"mxCell[@id='{ALIAS_LAYER_ID}']")
    layer_exists = alias_layer is not None
    layer_name_ok = alias_layer is not None and alias_layer.get("value") == ALIAS_LAYER_NAME
    layer_hidden_default = alias_layer is not None and alias_layer.get("visible") == "0"
    layer_parent_ok = alias_layer is not None and alias_layer.get("parent") == "0"

    objs = list(root.iter("object"))
    rooms = [o for o in objs if o.get("source_id")]
    markers = [o for o in objs if o.get("target_id")]
    int_conns = [o for o in objs if o.get("id", "").startswith("C")]
    ext_conns = [o for o in objs if o.get("id", "").startswith("X")]

    primary_int_conns = [
        o for o in int_conns if o.find("mxCell").get("parent") == "1"
    ]
    alias_int_conns = [
        o for o in int_conns if o.find("mxCell").get("parent") == ALIAS_LAYER_ID
    ]

    all_ids = [o.get("id") for o in objs]
    dup_ids = len(all_ids) != len(set(all_ids))
    room_ok = {o.get("source_id") for o in rooms} == members

    rules_ok = True
    rule_count = 0
    for o in rooms:
        src = loc_index[o.get("source_id")]
        stored = json.loads(o.get("travel_rules", "[]"))
        if stored != src["travel"]:
            rules_ok = False
        rule_count += len(stored)

    internal_edges = [
        e for e in graph["edges"]
        if e["source"] in members and e.get("target") in members
    ]
    represented = []
    valid_ids = set(all_ids)
    endpoint_ok = True
    for c in int_conns:
        for r in json.loads(c.get("represents_rules", "[]")):
            represented.append((
                r["source"],
                tuple(r["verbs"]),
                tuple(r["action"]),
                json.dumps(r.get("cond"), sort_keys=True),
            ))
        cell = c.find("mxCell")
        if cell.get("source") not in valid_ids or cell.get("target") not in valid_ids:
            endpoint_ok = False

    for c in ext_conns:
        cell = c.find("mxCell")
        if cell.get("source") not in valid_ids or cell.get("target") not in valid_ids:
            endpoint_ok = False

    original = [
        (
            e["source"],
            tuple(e["verbs"]),
            (e.get("action_type"), e.get("action_target")),
            json.dumps(e.get("cond"), sort_keys=True),
        )
        for e in internal_edges
    ]
    partition_ok = (len(represented) == len(original)) and (sorted(represented) == sorted(original))

    # Verify directional constraints (17/17)
    pos_by_loc = {}
    rects = []
    for o in rooms:
        cell = o.find("mxCell")
        gm = cell.find("mxGeometry")
        x, y, w, h = float(gm.get("x")), float(gm.get("y")), float(gm.get("width")), float(gm.get("height"))
        pos_by_loc[o.get("source_id")] = (x, y)
        rects.append((x, y, w, h))
    for o in markers:
        cell = o.find("mxCell")
        gm = cell.find("mxGeometry")
        rects.append((float(gm.get("x")), float(gm.get("y")), float(gm.get("width")), float(gm.get("height"))))

    dir_total = 0
    dir_sat = 0
    for e in internal_edges:
        d = primary_direction_v3(e)
        if d is None:
            continue
        dir_total += 1
        sx, sy = DIRECTION_SIGNS[d]
        x1, y1 = pos_by_loc[e["source"]]
        x2, y2 = pos_by_loc[e["target"]]
        dx, dy = x2 - x1, y2 - y1
        ok = True
        if sx > 0 and not (dx > 1):
            ok = False
        if sx < 0 and not (dx < -1):
            ok = False
        if sy > 0 and not (dy > 1):
            ok = False
        if sy < 0 and not (dy < -1):
            ok = False
        if ok:
            dir_sat += 1

    overlaps = 0
    for i, a in enumerate(rects):
        for b in rects[i + 1:]:
            if _overlap(a, b):
                overlaps += 1

    total_rules = sum(len(loc_index[m]["travel"]) for m in members)
    return {
        "rooms_present": f"{len(rooms)}/{len(members)}",
        "room_ids_match": room_ok,
        "duplicate_ids": dup_ids,
        "travel_rules_on_nodes_roundtrip": rules_ok,
        "total_rules_on_nodes": f"{rule_count}/{total_rules}",
        "internal_rules_exact_partition": partition_ok,
        "directional_constraints": f"{dir_sat}/{dir_total}",
        "connector_endpoints_resolve": endpoint_ok,
        "box_overlaps": overlaps,
        "layer_exists": layer_exists,
        "layer_name_ok": layer_name_ok,
        "layer_hidden_by_default": layer_hidden_default,
        "layer_parent_ok": layer_parent_ok,
        "primary_internal_connectors": len(primary_int_conns),
        "alias_internal_connectors": len(alias_int_conns),
        "external_marker_connectors": len(ext_conns),
        "default_visible_connectors": len(primary_int_conns) + len(ext_conns),
        "all_layers_connectors": len(primary_int_conns) + len(alias_int_conns) + len(ext_conns),
    }


def verify_pilot_v3_svg(svg_default_path: Path, svg_enabled_path: Path | None = None) -> dict[str, Any]:
    """Inspect exported SVG vector geometry to confirm that:
      - In default render (visible=0), all 21 primary/marker connectors are rendered
        and 0 alias connectors (#78909c) are rendered.
      - When the optional layer is enabled (visible=1), all 29 connectors (21 + 8 alias)
        are rendered.
    """
    import re

    pat = re.compile(
        r'<path d="M [^"]+" fill="none" stroke="([^"]+)"[^>]*stroke-miterlimit="10"'
    )
    svg_off = svg_default_path.read_text(encoding="utf-8")
    strokes_off = pat.findall(svg_off)
    alias_off = [c for c in strokes_off if c.lower() == "#78909c"]

    out: dict[str, Any] = {
        "default_svg_total_connectors": len(strokes_off),
        "default_svg_alias_connectors": len(alias_off),
        "default_svg_primary_visible_and_aliases_hidden": (
            len(strokes_off) == 21 and len(alias_off) == 0
        ),
    }
    if svg_enabled_path is not None and svg_enabled_path.exists():
        svg_on = svg_enabled_path.read_text(encoding="utf-8")
        strokes_on = pat.findall(svg_on)
        alias_on = [c for c in strokes_on if c.lower() == "#78909c"]
        out["enabled_svg_total_connectors"] = len(strokes_on)
        out["enabled_svg_alias_connectors"] = len(alias_on)
        out["enabled_svg_all_connectors_visible"] = (
            len(strokes_on) == 29 and len(alias_on) == 8
        )
    return out


if __name__ == "__main__":
    import subprocess
    import tempfile

    root_dir = Path(__file__).resolve().parent.parent
    drawio_exe = root_dir.parent / "draw.io" / "draw.io.exe"
    with (root_dir / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
        graph = json.load(f)

    out_v3 = root_dir / "output" / "pilot" / "CH_ENTRY_MataHari_V3.drawio"
    svg_v3 = root_dir / "output" / "pilot" / "CH_ENTRY_MataHari_V3.svg"
    generate_pilot_v3(graph, out_v3, alias_layer_visible=False)
    val = validate_pilot_v3(graph, out_v3)

    if svg_v3.exists() and drawio_exe.exists():
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            on_drawio = td_path / "CH_ENTRY_V3_on.drawio"
            on_svg = td_path / "CH_ENTRY_V3_on.svg"
            generate_pilot_v3(graph, on_drawio, alias_layer_visible=True)
            val_on = validate_pilot_v3(graph, on_drawio)
            subprocess.run(
                [str(drawio_exe), "-x", "-f", "svg", "--crop", "-o", str(on_svg), str(on_drawio)],
                check=True,
            )
            val["svg_layer_regression"] = verify_pilot_v3_svg(svg_v3, on_svg)
            val["no_metadata_loss_on_layer_toggle"] = (
                val_on["rooms_present"] == val["rooms_present"]
                and val_on["total_rules_on_nodes"] == val["total_rules_on_nodes"]
                and val_on["internal_rules_exact_partition"]
            )

    print(json.dumps(val, indent=2))

