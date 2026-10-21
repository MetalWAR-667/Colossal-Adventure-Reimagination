#!/usr/bin/env python3
"""
Mission 005 — Phase C, D & E: Full-world cartographic generator and validator
for Open Adventure (`output/Open_Adventure_World_V3.drawio`).

Extends the visually validated Mission 004 / Phase B Cave Entry V3 approach to
all 11 editorial chapters + the `00 — World Index` page:
  - Preserves all 185 locations, 623 travel rules, and original chapter assignments.
  - Corrected `<object id="...">` XML wrapper structure on all vertices and edges.
  - Untruncated English `long` descriptions and ordered `EXITS` on every room card.
  - Native draw.io layer `Parser Aliases / Fast Travel` (`visible="0"` by default)
    on every chapter page, containing only graph-theoretically verified non-adjacent
    parser-only shortcut connectors.
  - Splits grouped connectors when ordinary spatial movement and parser-alias rules
    share a destination so every source rule has a unique canonical representation.
  - Compass-oriented placement (NORTH = smaller Y, SOUTH = larger Y, EAST = larger X,
    WEST = smaller X) with UPWAR/DOWN visually distinct (bold blue #1565C0).
"""

from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

from oa_chapters import CHAPTERS
from oa_layout import _node_edges_for_chapter, _primary_direction
from oa_layout_v3 import DIRECTION_SIGNS, VERTICAL, primary_direction_v3, solve_axis
from oa_pilot_v2 import (
    FONT,
    NODE_W,
    X_GAP,
    X_STEP,
    _clean_heading,
    _cond_badge,
    _esc,
    _overlap,
    build_external_markers as build_entry_markers,
    build_room_display,
    estimate_room_height,
    layout_v2 as layout_entry_v2,
    route_fast_travel as route_entry_fast_travel,
)
from oa_pilot_v3 import (
    ALIAS_LAYER_ID,
    ALIAS_LAYER_NAME,
    SPATIAL_ACTION_VERBS,
    group_internal_edges_v3,
    is_direct_spatial_or_structural_rule,
)

Y_GAP = 150.0


# ---------------------------------------------------------------------------
# Smart cycle breaking & clamped neighbor-aligned DAG solver
# ---------------------------------------------------------------------------

def solve_axis_smart(
    nodes: list[str],
    constraints: list[tuple[str, str, float, tuple]],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """Break 2-node positive cycles first (choosing the edge whose removal leaves
    fewer remaining cycle drops), then delegate remaining cycles to Bellman-Ford."""
    active = list(constraints)
    dropped: list[dict[str, Any]] = []

    while True:
        by_uv: dict[tuple[str, str], tuple[str, str, float, tuple]] = {}
        two_cycle = None
        for c in active:
            u, v, w, ref = c
            if (v, u) in by_uv:
                two_cycle = (by_uv[(v, u)], c)
                break
            by_uv[(u, v)] = c
        if two_cycle is not None:
            c1, c2 = two_cycle
            a1 = [x for x in active if x is not c1]
            a2 = [x for x in active if x is not c2]
            _, d1 = solve_axis(nodes, a1)
            _, d2 = solve_axis(nodes, a2)
            if len(d1) < len(d2) or (len(d1) == len(d2) and str(c1[3]) > str(c2[3])):
                victim = c1
            else:
                victim = c2
            active.remove(victim)
            dropped.append({
                "dropped": victim[3],
                "cycle_nodes": sorted([c1[0], c1[1]]),
                "cycle_constraints": sorted([str(c1[3]), str(c2[3])]),
            })
            continue
        coords, rem_drops = solve_axis(nodes, active)
        dropped.extend(rem_drops)
        return coords, dropped


def _align_within_bounds(
    nodes: list[str],
    coords: dict[str, float],
    active_cons: list[tuple[str, str, float, tuple]],
    align_neighbors: dict[str, list[str]],
) -> dict[str, float]:
    """Pull each node toward the mean coordinate of its orthogonal/non-directional
    neighbors while strictly clamping within [lb, ub] of all active constraints."""
    out = dict(coords)
    for _ in range(30):
        for u in nodes:
            nbrs = align_neighbors.get(u, [])
            if not nbrs:
                continue
            target = sum(out[v] for v in nbrs) / len(nbrs)
            lb = -1e9
            ub = 1e9
            for p, q, w, _ in active_cons:
                if q == u:
                    lb = max(lb, out[p] + w)
                elif p == u:
                    ub = min(ub, out[q] - w)
            if lb <= ub:
                out[u] = max(lb, min(ub, target))
    m = min(out.values()) if out else 0.0
    return {k: round(v - m, 1) for k, v in out.items()}


def layout_witt_different(
    graph: dict[str, Any],
    heights: dict[str, int],
) -> dict[str, Any]:
    """Compact staggered 4x3 layout for Maze All-Different (K_11 complete digraph)
    plus the Anteroom / Witt's End top tier and the South Vending Machine / Ogre wing.

    Satisfies 100% (8/8) of the non-contradictory edges outside K_11 and 59/110
    inside K_11 (67/119 total vs 49/119 unoptimized), on a compact 1796x2656 canvas
    with zero overlaps.
    """
    members, internal_edges = _node_edges_for_chapter(graph, "CH_WITT_DIFFERENT")
    diff_nodes = sorted(n for n in members if n.startswith("LOC_DIFFERENT"))

    slots: list[tuple[float, float]] = []
    for r in range(3):
        for c in range(4):
            sx = 80.0 + c * 430.0 + r * 28.0
            sy = 470.0 + r * 435.0 + c * 22.0
            slots.append((sx, sy))

    best_assign = {
        "LOC_DIFFERENT1": 5,
        "LOC_DIFFERENT10": 3,
        "LOC_DIFFERENT11": 0,
        "LOC_DIFFERENT2": 2,
        "LOC_DIFFERENT3": 7,
        "LOC_DIFFERENT4": 1,
        "LOC_DIFFERENT5": 11,
        "LOC_DIFFERENT6": 9,
        "LOC_DIFFERENT7": 6,
        "LOC_DIFFERENT8": 4,
        "LOC_DIFFERENT9": 10,
    }
    pos: dict[str, tuple[float, float]] = {}
    for n in diff_nodes:
        pos[n] = slots[best_assign[n]]

    pos["LOC_ANTEROOM"] = (80.0, 185.0)
    pos["LOC_WITTSEND"] = (510.0, 185.0)

    x2, _ = pos["LOC_DIFFERENT2"]
    y_south = max(s[1] for s in slots) + 430.0
    pos["LOC_DEADEND13"] = (x2, y_south)
    pos["LOC_BADDIRECTION"] = (x2 - 430.0, y_south + 330.0)
    pos["LOC_ROUGHHEWN"] = (x2, y_south + 330.0)
    pos["LOC_LARGE"] = (x2 + 430.0, y_south + 640.0)
    pos["LOC_STOREROOM"] = (x2 + 430.0, y_south + 330.0)

    # Record the violated edges in K_11 + Witt's End 2-cycle for full transparency
    dropped: list[dict[str, Any]] = []
    for e in internal_edges:
        d = primary_direction_v3(e)
        if d is None or e["source"] == e["target"]:
            continue
        sx, sy = DIRECTION_SIGNS[d]
        x1, y1 = pos[e["source"]]
        x2_, y2_ = pos[e["target"]]
        dx, dy = x2_ - x1, y2_ - y1
        if (sx > 0 and not dx > 1) or (sx < 0 and not dx < -1) or (sy > 0 and not dy > 1) or (sy < 0 and not dy < -1):
            dropped.append({
                "dropped": (e["source"], d, e["target"]),
                "reason": "K_11 Maze All-Different / Witt's End non-Euclidean cycle",
            })

    return {
        "positions": pos,
        "heights": heights,
        "internal_edges": internal_edges,
        "dropped_constraints": dropped,
    }


def layout_special(
    graph: dict[str, Any],
    heights: dict[str, int],
) -> dict[str, Any]:
    """Clean 3-tier state-transition layout for CH_SPECIAL (`11 — Special & Transient States`):
      - Row 1 (y = 185): 4 death pseudo-locations (`LOC_FOOTSLIP`, `LOC_GRUESOME`, `LOC_NECKBROKE`, `LOC_NOMAKE`)
      - Row 2 (y = 480): central `LOC_NOWHERE` terminal state receiving all 4 `(implicit)` death transitions
      - Row 3 (y = 740): 2 conditional movement-block pseudo-locations (`LOC_DOME`, `LOC_SNAKEBLOCK`)
    """
    members, internal_edges = _node_edges_for_chapter(graph, "CH_SPECIAL")
    pos: dict[str, tuple[float, float]] = {
        "LOC_FOOTSLIP": (80.0, 185.0),
        "LOC_GRUESOME": (490.0, 185.0),
        "LOC_NECKBROKE": (900.0, 185.0),
        "LOC_NOMAKE": (1310.0, 185.0),
        "LOC_NOWHERE": (695.0, 480.0),
        "LOC_DOME": (380.0, 740.0),
        "LOC_SNAKEBLOCK": (1010.0, 740.0),
    }
    assert set(pos.keys()) == set(members)
    return {
        "positions": pos,
        "heights": heights,
        "internal_edges": internal_edges,
        "dropped_constraints": [],
    }


def layout_chapter_world_v3(
    graph: dict[str, Any],
    chapter_id: str,
    heights: dict[str, int],
) -> dict[str, Any]:
    """Compute compass-oriented, overlap-free room coordinates for any chapter."""
    if chapter_id == "CH_ENTRY":
        return layout_entry_v2(graph, heights)
    if chapter_id == "CH_WITT_DIFFERENT":
        return layout_witt_different(graph, heights)
    if chapter_id == "CH_SPECIAL":
        return layout_special(graph, heights)

    members, int_edges = _node_edges_for_chapter(graph, chapter_id)
    nodes = sorted(members)
    non_self = [e for e in int_edges if e["source"] != e["target"]]

    x_cons: list[tuple[str, str, float, tuple]] = []
    y_cons: list[tuple[str, str, float, tuple]] = []
    align_x: dict[str, list[str]] = defaultdict(list)
    align_y: dict[str, list[str]] = defaultdict(list)

    for e in non_self:
        d = primary_direction_v3(e)
        u, v = e["source"], e["target"]
        if d is None:
            align_x[u].append(v)
            align_x[v].append(u)
            align_y[u].append(v)
            align_y[v].append(u)
            continue
        sx, sy = DIRECTION_SIGNS[d]
        ref = (u, d, v)
        if sx > 0:
            x_cons.append((u, v, float(X_STEP), ref))
        elif sx < 0:
            x_cons.append((v, u, float(X_STEP), ref))
        else:
            align_x[u].append(v)
            align_x[v].append(u)

        if sy > 0:
            y_cons.append((u, v, float(heights[u] + Y_GAP), ref))
        elif sy < 0:
            y_cons.append((v, u, float(heights[v] + Y_GAP), ref))
        else:
            align_y[u].append(v)
            align_y[v].append(u)

    if chapter_id == "CH_REPOSITORY":
        # Keep the disconnected Endgame Repository pair (LOC_SW, LOC_NE) and
        # the SW Chasm pair (LOC_SWCHASM, LOC_WINDING) in the eastern columns
        # so they never sit inside the Volcano fork!
        x_cons.append(("LOC_BOULDERS2", "LOC_SW", float(X_STEP), ("group_x", "LOC_BOULDERS2", "LOC_SW")))
        x_cons.append(("LOC_BOULDERS2", "LOC_WINDING", float(X_STEP), ("group_x", "LOC_BOULDERS2", "LOC_WINDING")))
        y_cons.append(("LOC_NE", "LOC_SWCHASM", float(heights["LOC_NE"] + Y_GAP), ("group_y", "LOC_NE", "LOC_SWCHASM")))
    elif chapter_id == "CH_CENTRAL":
        # Group the 4 Beanstalk climb pseudo-rooms in the lower Twopit tier near LOC_WESTEND / LOC_WESTPIT
        for bs in ("LOC_CLIMBSTALK", "LOC_BUILDING1", "LOC_NOCLIMB", "LOC_PLANTTOP"):
            y_cons.append(("LOC_WESTEND", bs, float(heights["LOC_WESTEND"] + Y_GAP), ("group_y", "LOC_WESTEND", bs)))

    def get_active(cons: list[tuple[str, str, float, tuple]]):
        active = list(cons)
        _, drops = solve_axis_smart(nodes, active)
        for dr in [d["dropped"] for d in drops]:
            for c in reversed(active):
                if c[3] == dr:
                    active.remove(c)
                    break
        return active, drops

    active_x, drop_x = get_active(x_cons)
    active_y, drop_y = get_active(y_cons)

    for _ in range(300):
        xc0, _ = solve_axis(nodes, active_x)
        yc0, _ = solve_axis(nodes, active_y)
        x_coords = _align_within_bounds(nodes, xc0, active_x, align_x)
        y_coords = _align_within_bounds(nodes, yc0, active_y, align_y)

        conflict = None
        for i, a in enumerate(nodes):
            ra = (x_coords[a], y_coords[a], float(NODE_W), float(heights[a]))
            for b in nodes[i + 1:]:
                rb = (x_coords[b], y_coords[b], float(NODE_W), float(heights[b]))
                if not (
                    ra[0] + ra[2] + 35 <= rb[0]
                    or rb[0] + rb[2] + 35 <= ra[0]
                    or ra[1] + ra[3] + 35 <= rb[1]
                    or rb[1] + rb[3] + 35 <= ra[1]
                ):
                    conflict = (a, b)
                    break
            if conflict:
                break
        if not conflict:
            break

        a, b = conflict
        best_opt = None
        best_score = 1e18
        for axis, u, v, w in [
            ("x", a, b, float(X_STEP)),
            ("x", b, a, float(X_STEP)),
            ("y", a, b, float(heights[a] + Y_GAP)),
            ("y", b, a, float(heights[b] + Y_GAP)),
        ]:
            if axis == "x":
                cand = active_x + [(u, v, w, ("sep_x", u, v))]
                xc_try, dr = solve_axis(nodes, cand)
                if dr:
                    continue
                xc_try = _align_within_bounds(nodes, xc_try, cand, align_x)
                yc_try = y_coords
            else:
                cand = active_y + [(u, v, w, ("sep_y", u, v))]
                yc_try, dr = solve_axis(nodes, cand)
                if dr:
                    continue
                yc_try = _align_within_bounds(nodes, yc_try, cand, align_y)
                xc_try = x_coords
            span_x = max(xc_try.values()) - min(xc_try.values()) + NODE_W
            span_y = max(yc_try[n] + heights[n] for n in nodes) - min(yc_try.values())
            score = max(span_x, span_y * 1.15) + 0.25 * (span_x + span_y)
            if score < best_score:
                best_score = score
                best_opt = (axis, (u, v, w, (f"sep_{axis}", u, v)))
        assert best_opt is not None
        if best_opt[0] == "x":
            active_x.append(best_opt[1])
        else:
            active_y.append(best_opt[1])

    xc0, _ = solve_axis(nodes, active_x)
    yc0, _ = solve_axis(nodes, active_y)
    x_coords = _align_within_bounds(nodes, xc0, active_x, align_x)
    y_coords = _align_within_bounds(nodes, yc0, active_y, align_y)
    pos = {n: (x_coords[n] + 80.0, y_coords[n] + 190.0) for n in nodes}

    return {
        "positions": pos,
        "heights": heights,
        "internal_edges": int_edges,
        "dropped_constraints": drop_x + drop_y,
    }


# ---------------------------------------------------------------------------
# Local reference markers & mixed-rule splitting for all chapters
# ---------------------------------------------------------------------------

MAGIC_VERBS: set[str] = {"XYZZY", "PLUGH", "PLOVE", "FOOF"}
DEATH_TARGETS: set[str] = {
    "LOC_NECKBROKE", "LOC_NOMAKE", "LOC_GRUESOME", "LOC_FOOTSLIP", "LOC_NOWHERE",
}


def build_chapter_markers_v3(
    graph: dict[str, Any],
    chapter_id: str,
    positions: dict[str, tuple[float, float]],
    heights: dict[str, int],
) -> list[dict[str, Any]]:
    """Build local reference markers positioned near their origin rooms.

    For `CH_ENTRY`, returns the exact visually validated marker specifications
    from `oa_pilot_v2.build_external_markers`. For all other chapters, places
    each unique external destination marker adjacent to its primary origin room
    without overlapping any room or marker box, and splits mixed spatial/alias
    rules (e.g., `LOC_KINGHALL -> LOC_SECRET3` via `SW [35%]` vs `SECRE`, and
    `LOC_LOWROOM / LOC_SWISSCHEESE -> LOC_ORIENTAL`) into separate primary and
    `Parser Aliases / Fast Travel` links.
    """
    if chapter_id == "CH_ENTRY":
        return build_entry_markers(graph, positions, heights)

    members = set(graph["chapters"][chapter_id]["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    chapter_num = {
        cid: ch["title"].split(" — ")[0]
        for cid, ch in graph["chapters"].items()
    }
    chapter_short = {
        cid: ch["title"].split(" — ")[1].split("&")[0].strip()
        for cid, ch in graph["chapters"].items()
    }

    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for loc_id in sorted(members):
        for rule in loc_index[loc_id]["travel"]:
            if rule.get("action_type") == "goto":
                tgt = rule.get("action_target")
                if tgt not in members:
                    by_target[tgt].append({
                        "source": loc_id,
                        "verbs": rule.get("verbs", []),
                        "cond": rule.get("cond"),
                        "action": [rule.get("action_type"), tgt],
                    })

    placed_rects: list[tuple[float, float, float, float]] = [
        (positions[m][0], positions[m][1], float(NODE_W), float(heights[m]))
        for m in members
    ]
    markers: list[dict[str, Any]] = []
    mw, mh = 235.0, 50.0

    for tgt, rules in sorted(by_target.items()):
        tgt_loc = loc_index[tgt]
        tgt_cid = tgt_loc["chapter_id"]
        ch_no = chapter_num.get(tgt_cid, "??")
        ch_name = chapter_short.get(tgt_cid, tgt_cid)

        all_verbs = {v for r in rules for v in r.get("verbs", [])}
        if tgt.startswith("LOC_FOOF") or (all_verbs & MAGIC_VERBS):
            kind = "magic"
            fill, stroke, color = "#F3E5F5", "#7B1FA2", "#7B1FA2"
            title = f"✨ {tgt} · Ch {ch_no} {ch_name}"
        elif tgt in DEATH_TARGETS:
            kind = "death"
            fill, stroke, color = "#FFEBEE", "#C62828", "#C62828"
            title = f"☠ {tgt} · Ch {ch_no} Death"
        elif tgt_loc.get("role") in ("special", "transient", "null"):
            kind = "transient"
            fill, stroke, color = "#FFF3E0", "#E65100", "#E65100"
            title = f"⚠ {tgt} · Ch {ch_no} Transient"
        else:
            kind = "cross"
            fill, stroke, color = "#FFF9C4", "#F57C00", "#F57C00"
            title = f"→ {tgt} · Ch {ch_no} {ch_name}"

        # Split rules to `tgt` into primary vs parser-alias if `tgt` has both
        # a spatial/magic/implicit rule AND a non-directional keyword shortcut!
        def is_spatial_ext(r: dict[str, Any]) -> bool:
            vset = set(r.get("verbs", []))
            return (
                primary_direction_v3(r) is not None
                or not vset
                or bool(vset & SPATIAL_ACTION_VERBS)
                or bool(vset & MAGIC_VERBS)
            )

        has_spatial = any(is_spatial_ext(r) for r in rules)
        primary_rules = [r for r in rules if is_spatial_ext(r) or not has_spatial]
        alias_rules = [r for r in rules if has_spatial and not is_spatial_ext(r)]

        anchor_room = primary_rules[0]["source"]
        rx, ry = positions[anchor_room]
        rh = float(heights[anchor_room])
        d = primary_direction_v3(primary_rules[0])
        sx, sy = DIRECTION_SIGNS.get(d, (0, 1)) if d else (0, 1)

        cands: list[tuple[float, float]] = []
        if sy < 0:
            cands.extend([
                (rx, ry - mh - 18),
                (rx + NODE_W - mw, ry - mh - 18),
                (rx, ry - 2 * (mh + 14)),
            ])
        elif sy > 0:
            cands.extend([
                (rx, ry + rh + 18),
                (rx + NODE_W - mw, ry + rh + 18),
                (rx, ry + rh + 18 + mh + 14),
            ])
        if sx > 0:
            cands.extend([
                (rx + NODE_W - mw, ry - mh - 18),
                (rx + NODE_W - mw, ry + rh + 18),
                (rx + NODE_W + 18, ry),
            ])
        elif sx < 0:
            cands.extend([
                (rx, ry - mh - 18),
                (rx, ry + rh + 18),
                (rx - mw - 18, ry),
            ])

        for dy_off in (-mh - 18, rh + 18, -2 * (mh + 16), rh + 18 + mh + 16):
            for dx_off in (0.0, NODE_W - mw, -mw - 16.0, NODE_W + 16.0):
                cands.append((rx + dx_off, ry + dy_off))
        for ring in range(1, 8):
            for dx_off in (0.0, NODE_W - mw, -ring * 130.0, ring * 130.0):
                for dy_off in (-ring * 70.0, rh + ring * 70.0):
                    cands.append((rx + dx_off, ry + dy_off))

        chosen = None
        for cx, cy in cands:
            if cx < 20 or cy < 140:
                continue
            cand_rect = (cx, cy, mw, mh)
            if not any(_overlap(cand_rect, pr) for pr in placed_rects):
                chosen = (cx, cy)
                placed_rects.append(cand_rect)
                break
        assert chosen is not None
        mx, my = chosen

        sub_parts = []
        for r in rules:
            vs = ", ".join(r["verbs"][:2]) if r["verbs"] else "(implicit)"
            cb = _cond_badge(r.get("cond"))
            sub_parts.append(f"{vs} {cb}".strip())
        subtitle = " · ".join(dict.fromkeys(sub_parts))

        links: list[dict[str, Any]] = []
        for role_tag, r_group in (("primary", primary_rules), ("fast_travel", alias_rules)):
            if not r_group:
                continue
            by_src: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for r in r_group:
                by_src[r["source"]].append(r)
            for src_rm, src_rules in sorted(by_src.items()):
                srx, sry = positions[src_rm]
                srh = float(heights[src_rm])
                lbl_parts = []
                for sr in src_rules:
                    v0 = sr["verbs"][0] if sr["verbs"] else "(implicit)"
                    cb = _cond_badge(sr.get("cond"))
                    lbl_parts.append(f"{v0} {cb}".strip())
                lbl = " / ".join(lbl_parts)

                if my + mh <= sry:
                    exit_x, exit_y, entry_x, entry_y = 0.5, 0.0, 0.5, 1.0
                elif my >= sry + srh:
                    exit_x, exit_y, entry_x, entry_y = 0.5, 1.0, 0.5, 0.0
                elif mx >= srx + NODE_W:
                    exit_x, exit_y, entry_x, entry_y = 1.0, 0.5, 0.0, 0.5
                else:
                    exit_x, exit_y, entry_x, entry_y = 0.0, 0.5, 1.0, 0.5

                links.append({
                    "from": src_rm,
                    "label": lbl,
                    "role": role_tag,
                    "layer": ALIAS_LAYER_ID if role_tag == "fast_travel" else "1",
                    "rules": src_rules,
                    "exitX": exit_x,
                    "exitY": exit_y,
                    "entryX": entry_x,
                    "entryY": entry_y,
                    "color": "#78909C" if role_tag == "fast_travel" else color,
                    "offset": (0, 0),
                })

        markers.append({
            "id": f"M_{tgt}",
            "target": tgt,
            "target_chapter": tgt_cid,
            "kind": kind,
            "x": mx,
            "y": my,
            "w": mw,
            "h": mh,
            "fill": fill,
            "stroke": stroke,
            "title": title,
            "subtitle": subtitle,
            "rules": rules,
            "links": links,
        })

    return markers


# ---------------------------------------------------------------------------
# Page builders (Index Page + 11 Chapter Pages)
# ---------------------------------------------------------------------------

def build_index_diagram(
    mxfile: ET.Element,
    graph: dict[str, Any],
    chapter_stats: dict[str, dict[str, Any]],
) -> None:
    diag = ET.SubElement(mxfile, "diagram", {
        "id": "INDEX",
        "name": "00 — World Index",
    })
    model = ET.SubElement(diag, "mxGraphModel")
    for k, v in {
        "dx": "1422", "dy": "762", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": "1600", "pageHeight": "1180",
        "math": "0", "shadow": "0",
    }.items():
        model.set(k, v)

    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def add_text(cid: str, x: int, y: int, w: int, h: int, style: str, val: str) -> None:
        c = ET.SubElement(root, "mxCell", {
            "id": cid, "style": style, "value": val, "vertex": "1", "parent": "1",
        })
        ET.SubElement(c, "mxGeometry", {
            "x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry",
        })

    add_text(
        "idx_title", 60, 20, 1100, 34,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "fontSize=18;fontStyle=1;fontFamily=Helvetica;",
        "Open Adventure (Colossal Cave) — World Atlas V3 (Mata Hari, Mission 005)",
    )
    add_text(
        "idx_subtitle", 60, 56, 1420, 68,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=left;verticalAlign=top;spacingLeft=10;spacingTop=6;fontSize=10;fontFamily=Helvetica;",
        "<b>CANONICAL SOURCE &amp; LAYER ARCHITECTURE</b><br>"
        "• <b>Source authority:</b> Open_Adventure.yaml (E. S. Raymond, BSD-2-Clause, 1995 Crowther &amp; Woods 430-point expansion) — "
        "185 locations, 623 travel rules, 70 objects.<br>"
        "• <b>Compass convention:</b> NORTH = up (–Y), SOUTH = down (+Y), EAST = right (+X), WEST = left (–X). "
        "Vertical UPWAR / DOWN shafts are rendered in bold blue (#1565C0).<br>"
        "• <b>Optional layer on every chapter page:</b> <code>Parser Aliases / Fast Travel</code> (hidden by default; toggle in draw.io "
        "<i>View → Layers</i> to inspect the 27 non-adjacent keyword shortcut connectors [33 internal rules] + 2 split external alias links).",
    )

    # Place 11 chapter cards in a 3-column x 4-row grid
    card_w, card_h = 440, 195
    x0, y0 = 60, 150
    dx, dy = 490, 235

    for idx, cid in enumerate(CHAPTERS.keys()):
        ch = graph["chapters"][cid]
        st = chapter_stats[cid]
        col = idx % 3
        row = idx // 3
        cx = x0 + col * dx
        cy = y0 + row * dy

        label = (
            f"<b>{_esc(ch['title'])}</b><hr size='1'/>"
            f"{_esc(ch['description'])}<br><br>"
            f"• <b>Locations:</b> {st['locations']} · <b>Travel rules:</b> {st['total_rules']} "
            f"({st['internal_rules']} internal, {st['external_goto_rules']} cross-page, {st['speak_special_rules']} msg/special)<br>"
            f"• <b>Primary connectors:</b> {st['primary_internal_connectors']} internal + "
            f"{st['primary_external_connectors']} marker links<br>"
            f"• <b>Parser Aliases / Fast Travel layer:</b> {st['alias_internal_connectors']} internal "
            f"({st['alias_internal_rules']} rules) + {st['alias_external_connectors']} external<br>"
            f"• <b>Directional constraints:</b> {st['dir_satisfied']}/{st['dir_applicable']} satisfied"
        )
        obj = ET.SubElement(root, "object", {
            "id": f"IDX_{cid}",
            "label": label,
            "chapter_id": cid,
            "link": f"data:page/id,{cid}",
            "locations_count": str(st["locations"]),
            "rules_count": str(st["total_rules"]),
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": (
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#1565C0;"
                "strokeWidth=1.8;arcSize=4;fontSize=10;fontFamily=Helvetica;"
                "align=left;verticalAlign=top;spacingLeft=10;spacingRight=10;spacingTop=8;"
            ),
            "vertex": "1",
            "parent": "1",
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(cx), "y": str(cy),
            "width": str(card_w), "height": str(card_h), "as": "geometry",
        })


def seg_hits_box(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    box: tuple[float, float, float, float],
    margin: float = 4.0,
) -> bool:
    bx, by, bw, bh = box
    ix0, iy0, ix1, iy1 = bx - margin, by - margin, bx + bw + margin, by + bh + margin
    if abs(x1 - x2) < 1.0:
        x = 0.5 * (x1 + x2)
        if ix0 < x < ix1:
            lo, hi = min(y1, y2), max(y1, y2)
            if max(lo, iy0) < min(hi, iy1):
                return True
    elif abs(y1 - y2) < 1.0:
        y = 0.5 * (y1 + y2)
        if iy0 < y < iy1:
            lo, hi = min(x1, x2), max(x1, x2)
            if max(lo, ix0) < min(hi, ix1):
                return True
    return False


def path_hits_obstacles(
    pts: list[tuple[float, float]],
    obstacles: list[tuple[float, float, float, float]],
) -> bool:
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if abs(x1 - x2) + abs(y1 - y2) < 2.0:
            continue
        for ob in obstacles:
            if seg_hits_box(x1, y1, x2, y2, ob):
                return True
    return False


def route_obstacle_free(
    rect_a: tuple[float, float, float, float],
    rect_b: tuple[float, float, float, float],
    obstacles: list[tuple[float, float, float, float]],
    track_idx: int = 0,
) -> tuple[dict[str, str], list[tuple[float, float]], tuple[int, int] | None]:
    """Find an orthogonal polyline from rect_a to rect_b that avoids all obstacles."""
    xa, ya, wa, ha = rect_a
    xb, yb, wb, hb = rect_b
    shift = ((track_idx % 7) - 3) * 10.0

    def port_pt(rect: tuple[float, float, float, float], side: str, frac: float) -> tuple[float, float, float, float]:
        rx, ry, rw, rh = rect
        frac = max(0.08, min(0.92, frac))
        if side == "top":
            return (rx + rw * frac, ry, frac, 0.0)
        if side == "bottom":
            return (rx + rw * frac, ry + rh, frac, 1.0)
        if side == "left":
            return (rx, ry + rh * frac, 0.0, frac)
        return (rx + rw, ry + rh * frac, 1.0, frac)

    # 1. Try straight horizontal if vertical intervals overlap
    y_lo = max(ya + 22.0, yb + 22.0)
    y_hi = min(ya + ha - 22.0, yb + hb - 22.0)
    if y_hi >= y_lo:
        for cand_y in [0.5 * (y_lo + y_hi) + shift, y_lo + 10.0, y_hi - 10.0, 0.5 * (y_lo + y_hi)]:
            if not (y_lo <= cand_y <= y_hi):
                continue
            sa, sb = ("right", "left") if xb >= xa + wa else ("left", "right")
            x1 = xa + wa if sa == "right" else xa
            x2 = xb if sb == "left" else xb + wb
            if not path_hits_obstacles([(x1, cand_y), (x2, cand_y)], obstacles):
                fa = (cand_y - ya) / ha
                fb = (cand_y - yb) / hb
                ex_a = "1.0" if sa == "right" else "0.0"
                ex_b = "0.0" if sb == "left" else "1.0"
                return (
                    {"exitX": ex_a, "exitY": f"{fa:.3f}", "entryX": ex_b, "entryY": f"{fb:.3f}"},
                    [],
                    (0, -14),
                )

    # 2. Try straight vertical if horizontal intervals overlap
    x_lo = max(xa + 22.0, xb + 22.0)
    x_hi = min(xa + wa - 22.0, xb + wb - 22.0)
    if x_hi >= x_lo:
        for cand_x in [0.5 * (x_lo + x_hi) + shift, x_lo + 12.0, x_hi - 12.0, 0.5 * (x_lo + x_hi)]:
            if not (x_lo <= cand_x <= x_hi):
                continue
            sa, sb = ("bottom", "top") if yb >= ya + ha else ("top", "bottom")
            y1 = ya + ha if sa == "bottom" else ya
            y2 = yb if sb == "top" else yb + hb
            if not path_hits_obstacles([(cand_x, y1), (cand_x, y2)], obstacles):
                fa = (cand_x - xa) / wa
                fb = (cand_x - xb) / wb
                ey_a = "1.0" if sa == "bottom" else "0.0"
                ey_b = "0.0" if sb == "top" else "1.0"
                return (
                    {"exitX": f"{fa:.3f}", "exitY": ey_a, "entryX": f"{fb:.3f}", "entryY": ey_b},
                    [],
                    None,
                )

    all_boxes = obstacles + [rect_a, rect_b]
    y_tracks: list[float] = []
    if yb > ya + ha:
        y_tracks.append(0.5 * (ya + ha + yb) + shift)
    elif ya > yb + hb:
        y_tracks.append(0.5 * (yb + hb + ya) + shift)
    for bx, by, bw, bh in all_boxes:
        for off in (-26.0, -42.0, -60.0, bh + 26.0, bh + 42.0, bh + 60.0):
            y_tracks.append(by + off + shift * 0.5)

    x_tracks: list[float] = []
    if xb > xa + wa:
        x_tracks.append(0.5 * (xa + wa + xb) + shift)
    elif xa > xb + wb:
        x_tracks.append(0.5 * (xb + wb + xa) + shift)
    for bx, by, bw, bh in all_boxes:
        for off in (-26.0, -48.0, -70.0, bw + 26.0, bw + 48.0, bw + 70.0):
            x_tracks.append(bx + off + shift * 0.5)

    fracs = [0.5, 0.25, 0.75, 0.15, 0.85]
    best_route = None
    best_len = 1e18

    # 3. Try 1-bend L-paths
    for sa in ("left", "right"):
        if (sa == "right" and xb < xa) or (sa == "left" and xb > xa):
            continue
        for sb in ("top", "bottom"):
            for fa in fracs[:3]:
                for fb in fracs[:3]:
                    x1, y1, exa, eya = port_pt(rect_a, sa, fa)
                    x2, y2, exb, eyb = port_pt(rect_b, sb, fb)
                    pts = [(x1, y1), (x2, y1), (x2, y2)]
                    if not path_hits_obstacles(pts, all_boxes):
                        plen = abs(x2 - x1) + abs(y2 - y1)
                        if plen < best_len:
                            best_len = plen
                            best_route = (
                                {"exitX": f"{exa:.3f}", "exitY": f"{eya:.3f}", "entryX": f"{exb:.3f}", "entryY": f"{eyb:.3f}"},
                                [(round(x2, 1), round(y1, 1))],
                                None,
                            )
    if best_route:
        return best_route

    # 4. Try 2-bend horizontal gutter
    y_tracks_sorted = sorted(set(round(y, 1) for y in y_tracks if y > 130), key=lambda y: abs(y - 0.5 * (ya + yb)))
    for yt in y_tracks_sorted[:24]:
        sa = "bottom" if yt > ya + ha * 0.5 else "top"
        sb = "bottom" if yt > yb + hb * 0.5 else "top"
        for fa in fracs:
            x1, y1, exa, eya = port_pt(rect_a, sa, fa)
            if path_hits_obstacles([(x1, y1), (x1, yt)], obstacles + [rect_b]):
                continue
            for fb in fracs:
                x2, y2, exb, eyb = port_pt(rect_b, sb, fb)
                if path_hits_obstacles([(x2, yt), (x2, y2)], obstacles + [rect_a]):
                    continue
                if not path_hits_obstacles([(x1, yt), (x2, yt)], all_boxes):
                    plen = abs(yt - y1) + abs(x2 - x1) + abs(y2 - yt)
                    if plen < best_len:
                        best_len = plen
                        best_route = (
                            {"exitX": f"{exa:.3f}", "exitY": f"{eya:.3f}", "entryX": f"{exb:.3f}", "entryY": f"{eyb:.3f}"},
                            [(round(x1, 1), round(yt, 1)), (round(x2, 1), round(yt, 1))],
                            None,
                        )

    # 5. Try 2-bend vertical gutter
    x_tracks_sorted = sorted(set(round(x, 1) for x in x_tracks if x > 20), key=lambda x: abs(x - 0.5 * (xa + xb)))
    for xt in x_tracks_sorted[:24]:
        sa = "right" if xt > xa + wa * 0.5 else "left"
        sb = "right" if xt > xb + wb * 0.5 else "left"
        for fa in fracs:
            x1, y1, exa, eya = port_pt(rect_a, sa, fa)
            if path_hits_obstacles([(x1, y1), (xt, y1)], obstacles + [rect_b]):
                continue
            for fb in fracs:
                x2, y2, exb, eyb = port_pt(rect_b, sb, fb)
                if path_hits_obstacles([(xt, y2), (x2, y2)], obstacles + [rect_a]):
                    continue
                if not path_hits_obstacles([(xt, y1), (xt, y2)], all_boxes):
                    plen = abs(xt - x1) + abs(y2 - y1) + abs(x2 - xt)
                    if plen < best_len:
                        best_len = plen
                        best_route = (
                            {"exitX": f"{exa:.3f}", "exitY": f"{eya:.3f}", "entryX": f"{exb:.3f}", "entryY": f"{eyb:.3f}"},
                            [(round(xt, 1), round(y1, 1)), (round(xt, 1), round(y2, 1))],
                            None,
                        )
    if best_route:
        return best_route

    # 6. Try 3-bend gutter-to-gutter
    for yt1 in [ya - 26.0 + shift * 0.4, ya + ha + 26.0 + shift * 0.4]:
        sa = "top" if yt1 < ya else "bottom"
        x1, y1, exa, eya = port_pt(rect_a, sa, 0.5 + (track_idx % 5 - 2) * 0.08)
        if path_hits_obstacles([(x1, y1), (x1, yt1)], obstacles + [rect_b]):
            continue
        for yt2 in [yb - 26.0 + shift * 0.4, yb + hb + 26.0 + shift * 0.4]:
            sb = "top" if yt2 < yb else "bottom"
            x2, y2, exb, eyb = port_pt(rect_b, sb, 0.5 + (track_idx % 5 - 2) * 0.08)
            if path_hits_obstacles([(x2, yt2), (x2, y2)], obstacles + [rect_a]):
                continue
            for xt in x_tracks_sorted[:24]:
                pts = [(x1, yt1), (xt, yt1), (xt, yt2), (x2, yt2)]
                if not path_hits_obstacles(pts, all_boxes):
                    plen = abs(yt1 - y1) + abs(xt - x1) + abs(yt2 - yt1) + abs(x2 - xt) + abs(y2 - yt2)
                    if plen < best_len:
                        best_len = plen
                        best_route = (
                            {"exitX": f"{exa:.3f}", "exitY": f"{eya:.3f}", "entryX": f"{exb:.3f}", "entryY": f"{eyb:.3f}"},
                            [
                                (round(x1, 1), round(yt1, 1)),
                                (round(xt, 1), round(yt1, 1)),
                                (round(xt, 1), round(yt2, 1)),
                                (round(x2, 1), round(yt2, 1)),
                            ],
                            None,
                        )
    if best_route:
        return best_route

    return ({"exitX": "0.5", "exitY": "1.0", "entryX": "0.5", "entryY": "0.0"}, [], None)


def build_chapter_diagram(
    mxfile: ET.Element,
    graph: dict[str, Any],
    chapter_id: str,
) -> dict[str, Any]:
    chapter = graph["chapters"][chapter_id]
    members = set(chapter["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}

    display = build_room_display(graph, chapter_id)
    heights = {
        loc_id: estimate_room_height(d["heading"], d["body"], d["exit_lines"])
        for loc_id, d in display.items()
    }
    lay = layout_chapter_world_v3(graph, chapter_id, heights)
    positions = lay["positions"]
    internal_edges = lay["internal_edges"]

    connectors, analysis = group_internal_edges_v3(internal_edges, loc_index)
    markers = build_chapter_markers_v3(graph, chapter_id, positions, heights)

    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    ET.SubElement(root, "mxCell", {
        "id": ALIAS_LAYER_ID,
        "value": ALIAS_LAYER_NAME,
        "style": "locked=0;",
        "parent": "0",
        "visible": "0",
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
        "title", 60, 14, 920, 28,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;fontFamily=Helvetica;",
        f"{chapter['title']} — Open Adventure World V3 (Mata Hari, Mission 005)",
    )
    add_text_cell(
        "compass", 60, 46, 130, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=center;verticalAlign=middle;fontFamily=Courier New;fontSize=11;fontStyle=1;",
        "NORTH (–Y)<br>↑<br>W ← + → E<br>↓<br>SOUTH (+Y)",
    )
    add_text_cell(
        "legend", 206, 46, 740, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=left;verticalAlign=top;spacingLeft=10;spacingTop=5;fontSize=9.5;fontFamily=Helvetica;",
        "<b>LEGEND &amp; LAYERS</b><br>"
        "• <b>Black solid (2.5 px):</b> primary compass/passage movement (double arrowhead = two-way)<br>"
        "• <b>Blue solid (2.8 px):</b> vertical UPWAR / DOWN shaft (distinct from compass N/S)<br>"
        "• <b>Purple dashed:</b> magic word / special transition · "
        "<b>Local markers:</b> yellow = cross-page · orange = transient · red = death<br>"
        "• <b>Optional layer [Parser Aliases / Fast Travel] (hidden by default):</b> "
        "non-adjacent keyword shortcuts",
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

    # --- Local Reference Markers & their links ---
    marker_rects_by_id: dict[str, tuple[float, float, float, float]] = {
        m["id"]: (m["x"], m["y"], m["w"], m["h"]) for m in markers
    }
    all_rects: dict[str, tuple[float, float, float, float]] = {**room_rects, **marker_rects_by_id}
    marker_rects: list[tuple[float, float, float, float]] = []
    ext_conn_count = 0
    primary_ext_conns = 0
    alias_ext_conns = 0

    for m in markers:
        mid = m["id"]
        mx, my, mw, mh = m["x"], m["y"], m["w"], m["h"]
        marker_rects.append((mx, my, mw, mh))
        mlabel = f"<b>{_esc(m['title'])}</b><br>{_esc(m['subtitle']).replace(chr(10), '<br>')}"
        tgt_cid = loc_index[m["target"]]["chapter_id"]
        obj = ET.SubElement(root, "object", {
            "id": mid,
            "label": mlabel,
            "kind": m["kind"],
            "target_id": m["target"],
            "target_chapter_id": tgt_cid,
            "link": f"data:page/id,{tgt_cid}",
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
            link_layer = link.get("layer", "1")
            link_role = link.get("role", "primary")
            if link_layer == ALIAS_LAYER_ID:
                alias_ext_conns += 1
            else:
                primary_ext_conns += 1

            ext_exit_x = str(link["exitX"])
            ext_exit_y = str(link["exitY"])
            ext_entry_x = str(link["entryX"])
            ext_entry_y = str(link["entryY"])
            ext_wps: list[tuple[float, float]] = list(link.get("waypoints", []))
            if chapter_id != "CH_ENTRY":
                obs_ext = [r for k, r in all_rects.items() if k not in (src_room, mid)]
                ext_pts, ext_wps, _ = route_obstacle_free(
                    room_rects[src_room], marker_rects_by_id[mid], obs_ext, ext_conn_count
                )
                ext_exit_x = ext_pts["exitX"]
                ext_exit_y = ext_pts["exitY"]
                ext_entry_x = ext_pts["entryX"]
                ext_entry_y = ext_pts["entryY"]

            lstyle = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor={link['color']};strokeWidth=1.8;dashed=1;dashPattern=4 3;"
                "endArrow=block;endFill=1;endSize=6;"
                f"exitX={ext_exit_x};exitY={ext_exit_y};exitDx=0;exitDy=0;"
                f"entryX={ext_entry_x};entryY={ext_entry_y};entryDx=0;entryDy=0;"
                "fontSize=9;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
            eobj_attrs = {
                "id": eid,
                "label": _esc(link["label"]),
                "role": link_role,
                "layer_name": ALIAS_LAYER_NAME if link_layer == ALIAS_LAYER_ID else "Primary Map",
                "marker_target": m["target"],
                "source_room": src_room,
            }
            if link.get("rules"):
                eobj_attrs["represents_rules"] = json.dumps(
                    link["rules"], sort_keys=True, ensure_ascii=False
                )
            eobj = ET.SubElement(root, "object", eobj_attrs)
            ecell = ET.SubElement(eobj, "mxCell", {
                "style": lstyle,
                "edge": "1",
                "parent": link_layer,
                "source": f"N_{src_room}",
                "target": mid,
            })
            egeom = ET.SubElement(ecell, "mxGeometry", {"relative": "1", "as": "geometry"})
            ox, oy = link.get("offset", (0, 0))
            if ox or oy:
                ET.SubElement(egeom, "mxPoint", {"x": str(ox), "y": str(oy), "as": "offset"})
            if ext_wps:
                arr = ET.SubElement(egeom, "Array", {"as": "points"})
                for wx, wy in ext_wps:
                    ET.SubElement(arr, "mxPoint", {"x": str(int(wx)), "y": str(int(wy))})

    # --- Internal Connectors (Primary Map + Parser Aliases / Fast Travel layer) ---
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

        if chapter_id == "CH_ENTRY":
            # Use exact Mission 004 / Phase B pilot styling and routing for CH_ENTRY
            if conn["role"] == "fast_travel":
                pts, waypoints, label_rel_x = route_entry_fast_travel(conn, positions, heights)
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
                waypoints = [(round(x1, 1), 576.0), (round(x2, 1), 576.0)]
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
                ex_a, ex_b = ("1.0", "0.0") if positions[b][0] > positions[a][0] else ("0.0", "1.0")
                style = (
                    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                    f"strokeColor=#000000;strokeWidth=2.5;{arrows}"
                    f"exitX={ex_a};exitY={ey_a:.3f};exitDx=0;exitDy=0;"
                    f"entryX={ex_b};entryY={ey_b:.3f};entryDx=0;entryDy=0;"
                    "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
                )
                label_offset = (0, -14)
        else:
            # General chapter connector styling + obstacle-avoiding orthogonal routing
            has_vert = any(primary_direction_v3(r) in VERTICAL for r in rules)
            has_cond = any(r.get("cond") is not None for r in rules)
            is_magic = a.startswith("LOC_FOOF") or b.startswith("LOC_FOOF")

            if conn["kind"] == "self":
                style = (
                    "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;html=1;"
                    f"strokeColor=#616161;strokeWidth=1.8;dashed=1;{arrows}"
                    "exitX=1.0;exitY=0.25;exitDx=0;exitDy=0;"
                    "entryX=0.85;entryY=0.0;entryDx=0;entryDy=0;"
                    "fontSize=8.5;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
                )
                rx, ry = positions[a]
                waypoints = [(rx + NODE_W + 28.0, ry + 45.0), (rx + NODE_W + 28.0, ry - 22.0), (rx + NODE_W * 0.85, ry - 22.0)]
            else:
                obs_int = [r for k, r in all_rects.items() if k not in (a, b)]
                int_pts, waypoints, label_offset = route_obstacle_free(
                    room_rects[a], room_rects[b], obs_int, gi
                )
                ports_str = (
                    f"exitX={int_pts['exitX']};exitY={int_pts['exitY']};exitDx=0;exitDy=0;"
                    f"entryX={int_pts['entryX']};entryY={int_pts['entryY']};entryDx=0;entryDy=0;"
                )
                if conn["role"] == "fast_travel":
                    style = (
                        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                        f"strokeColor=#78909C;strokeWidth=1.5;dashed=1;dashPattern=3 3;{arrows}"
                        f"{ports_str}"
                        "fontSize=8.5;fontFamily=Helvetica;fontColor=#37474F;labelBackgroundColor=#FFFFFF;"
                    )
                elif is_magic:
                    style = (
                        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                        f"strokeColor=#7B1FA2;strokeWidth=2.2;dashed=1;dashPattern=5 3;{arrows}"
                        f"{ports_str}"
                        "fontSize=9;fontFamily=Helvetica;fontColor=#4A148C;labelBackgroundColor=#FFFFFF;"
                    )
                elif has_vert:
                    dash_s = "dashed=1;dashPattern=6 3;" if has_cond else ""
                    style = (
                        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                        f"strokeColor=#1565C0;strokeWidth=2.6;{dash_s}{arrows}"
                        f"{ports_str}"
                        "fontSize=9;fontStyle=1;fontFamily=Helvetica;fontColor=#0D47A1;"
                        "labelBackgroundColor=#FFFFFF;"
                    )
                else:
                    dash_s = "dashed=1;dashPattern=6 3;" if has_cond else ""
                    color_s = "#BF360C" if has_cond else "#000000"
                    style = (
                        "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                        f"strokeColor={color_s};strokeWidth=2.3;{dash_s}{arrows}"
                        f"{ports_str}"
                        "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
                    )

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

    # Compute chapter metrics
    all_rects = list(room_rects.values()) + marker_rects
    max_x = max(r[0] + r[2] for r in all_rects)
    max_y = max(r[1] + r[3] for r in all_rects)

    total_rules = sum(len(loc_index[m]["travel"]) for m in members)
    ext_goto_rules = sum(len(m["rules"]) for m in markers)
    speak_spec_rules = total_rules - len(internal_edges) - ext_goto_rules

    primary_int_conns = [c for c in connectors if c["role"] == "primary"]
    alias_int_conns = [c for c in connectors if c["role"] == "fast_travel"]
    alias_int_rules = sum(len(c["rules"]) for c in alias_int_conns)

    # Directional constraint metrics (V3 vs V2 baseline)
    non_self_v3 = [
        e for e in internal_edges
        if primary_direction_v3(e) is not None and e["source"] != e["target"]
    ]
    non_self_v2 = [
        e for e in internal_edges
        if _primary_direction(e) is not None and e["source"] != e["target"]
    ]
    self_dir = [
        e for e in internal_edges
        if primary_direction_v3(e) is not None and e["source"] == e["target"]
    ]
    dir_sat = 0
    violated_edges = []
    for e in non_self_v3:
        d = primary_direction_v3(e)
        sx, sy = DIRECTION_SIGNS[d]
        x1, y1 = positions[e["source"]]
        x2, y2 = positions[e["target"]]
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
        else:
            violated_edges.append((e["source"], d, e["target"]))

    add_text_cell(
        "provenance", 60, max_y + 18, 1340, 34,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
        "whiteSpace=wrap;rounded=0;fontSize=9;fontStyle=2;fontFamily=Helvetica;",
        "Source: Open_Adventure.yaml (BSD-2-Clause, E. S. Raymond) — canonical. "
        f"{chapter['title']}: {len(members)} locations, {total_rules} travel rules preserved "
        f"({len(primary_int_conns)} primary internal connectors + {len(markers)} local markers on Primary Map; "
        f"{len(alias_int_conns)} internal + {alias_ext_conns} external alias connectors on optional layer "
        f"'{ALIAS_LAYER_NAME}'; {dir_sat}/{len(non_self_v3)} directional constraints satisfied). NORTH = up = smaller Y.",
    )

    page_w = int(max_x + 60)
    page_h = int(max_y + 65)

    diag = ET.SubElement(mxfile, "diagram", {
        "id": chapter_id,
        "name": chapter["title"],
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

    return {
        "chapter_id": chapter_id,
        "title": chapter["title"],
        "locations": len(members),
        "total_rules": total_rules,
        "internal_rules": len(internal_edges),
        "external_goto_rules": ext_goto_rules,
        "speak_special_rules": speak_spec_rules,
        "primary_internal_connectors": len(primary_int_conns),
        "alias_internal_connectors": len(alias_int_conns),
        "alias_internal_rules": alias_int_rules,
        "primary_external_connectors": primary_ext_conns,
        "alias_external_connectors": alias_ext_conns,
        "local_markers": len(markers),
        "dir_v2_baseline": len(non_self_v2),
        "dir_upwar_added": len(non_self_v3) - len(non_self_v2),
        "dir_self_loops": len(self_dir),
        "dir_applicable": len(non_self_v3),
        "dir_satisfied": dir_sat,
        "dir_violated": violated_edges,
        "reciprocal_retained": [
            (r["source"], r["verbs"], r["target"])
            for r in analysis["reciprocal_retained"]
        ],
        "uncertain_retained": [
            (r["source"], r["verbs"], r["target"])
            for r in analysis["uncertain_retained"]
        ],
        "page_width": page_w,
        "page_height": page_h,
    }


def generate_world_v3(graph: dict[str, Any], out_path: Path) -> dict[str, Any]:
    mxfile = ET.Element("mxfile", {
        "host": "Open Adventure RPG Archaeology tooling",
        "agent": "007-mata-hari-world-v3",
        "type": "device",
        "version": "24.7.0",
    })

    # First build all 11 chapter diagrams into a temporary container so we have
    # exact stats for the `00 — World Index` page, then assemble Index + 11 Chapters.
    temp_mx = ET.Element("mxfile")
    chapter_stats: dict[str, dict[str, Any]] = {}
    for cid in CHAPTERS.keys():
        chapter_stats[cid] = build_chapter_diagram(temp_mx, graph, cid)

    build_index_diagram(mxfile, graph, chapter_stats)
    for diag in list(temp_mx):
        mxfile.append(diag)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(out_path, encoding="utf-8", xml_declaration=True)
    return chapter_stats


# ---------------------------------------------------------------------------
# Full-World Structural, Layer & Directional Validation
# ---------------------------------------------------------------------------

def validate_world_v3(graph: dict[str, Any], path: Path) -> dict[str, Any]:
    tree = ET.parse(path)
    mxfile = tree.getroot()
    diagrams = list(mxfile.findall("diagram"))

    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    expected_locs = set(loc_index.keys())
    seen_locs: set[str] = set()
    total_rules_on_nodes = 0
    all_rules_roundtrip = True
    all_descs_roundtrip = True
    all_partitions_ok = True
    all_endpoints_ok = True
    all_layers_ok = True
    total_overlaps = 0

    per_chapter: dict[str, dict[str, Any]] = {}

    for diag in diagrams[1:]:
        cid = diag.get("id")
        root = diag.find("mxGraphModel/root")
        members = set(graph["chapters"][cid]["members"])

        alias_layer = root.find(f"mxCell[@id='{ALIAS_LAYER_ID}']")
        layer_ok = (
            alias_layer is not None
            and alias_layer.get("value") == ALIAS_LAYER_NAME
            and alias_layer.get("visible") == "0"
            and alias_layer.get("parent") == "0"
        )
        if not layer_ok:
            all_layers_ok = False

        objs = list(root.iter("object"))
        rooms = [o for o in objs if o.get("source_id")]
        markers = [o for o in objs if o.get("target_id")]
        int_conns = [o for o in objs if o.get("id", "").startswith("C")]
        ext_conns = [o for o in objs if o.get("id", "").startswith("X")]

        room_ids = {o.get("source_id") for o in rooms}
        if room_ids != members:
            all_rules_roundtrip = False
        seen_locs |= room_ids

        for o in rooms:
            lid = o.get("source_id")
            if o.get("description_en") != (loc_index[lid]["description"].get("long") or ""):
                all_descs_roundtrip = False
            stored = json.loads(o.get("travel_rules", "[]"))
            if stored != loc_index[lid]["travel"]:
                all_rules_roundtrip = False
            total_rules_on_nodes += len(stored)

        valid_ids = {o.get("id") for o in objs}
        internal_edges = [
            e for e in graph["edges"]
            if e["source"] in members and e.get("target") in members
        ]
        represented = []
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
                all_endpoints_ok = False

        for c in ext_conns:
            cell = c.find("mxCell")
            if cell.get("source") not in valid_ids or cell.get("target") not in valid_ids:
                all_endpoints_ok = False

        original = [
            (
                e["source"],
                tuple(e["verbs"]),
                (e.get("action_type"), e.get("action_target")),
                json.dumps(e.get("cond"), sort_keys=True),
            )
            for e in internal_edges
        ]
        part_ok = (len(represented) == len(original)) and (sorted(represented) == sorted(original))
        if not part_ok:
            all_partitions_ok = False

        rects = []
        for o in rooms + markers:
            gm = o.find("mxCell/mxGeometry")
            rects.append((
                float(gm.get("x")), float(gm.get("y")),
                float(gm.get("width")), float(gm.get("height")),
            ))
        ch_overlaps = 0
        for i, a in enumerate(rects):
            for b in rects[i + 1:]:
                if _overlap(a, b):
                    ch_overlaps += 1
        total_overlaps += ch_overlaps

        per_chapter[cid] = {
            "rooms": f"{len(rooms)}/{len(members)}",
            "internal_partition_ok": part_ok,
            "layer_ok": layer_ok,
            "overlaps": ch_overlaps,
            "primary_int_conns": sum(1 for c in int_conns if c.find("mxCell").get("parent") == "1"),
            "alias_int_conns": sum(1 for c in int_conns if c.find("mxCell").get("parent") == ALIAS_LAYER_ID),
            "ext_conns": len(ext_conns),
        }

    return {
        "pages_count": len(diagrams),
        "index_page_present": diagrams[0].get("id") == "INDEX",
        "locations_preserved": f"{len(seen_locs)}/{len(expected_locs)}",
        "all_locations_exact_match": seen_locs == expected_locs,
        "travel_rules_preserved": f"{total_rules_on_nodes}/{len(graph['edges'])}",
        "all_travel_rules_roundtrip": all_rules_roundtrip,
        "all_descriptions_roundtrip": all_descs_roundtrip,
        "all_internal_partitions_exact": all_partitions_ok,
        "all_connector_endpoints_resolve": all_endpoints_ok,
        "all_alias_layers_configured_hidden": all_layers_ok,
        "total_box_overlaps_across_world": total_overlaps,
        "per_chapter": per_chapter,
    }


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    with (root_dir / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
        graph = json.load(f)

    out_world = root_dir / "output" / "Open_Adventure_World_V3.drawio"
    stats = generate_world_v3(graph, out_world)
    val = validate_world_v3(graph, out_world)

    total_app = sum(s["dir_applicable"] for s in stats.values())
    total_sat = sum(s["dir_satisfied"] for s in stats.values())
    total_alias_int = sum(s["alias_internal_connectors"] for s in stats.values())
    total_alias_rules = sum(s["alias_internal_rules"] for s in stats.values())
    total_alias_ext = sum(s["alias_external_connectors"] for s in stats.values())

    print(json.dumps({
        "file": str(out_world),
        "validation": {k: v for k, v in val.items() if k != "per_chapter"},
        "world_directional_constraints": f"{total_sat}/{total_app} ({100.0 * total_sat / total_app:.1f}%)",
        "world_alias_layer_summary": {
            "internal_alias_connectors": total_alias_int,
            "internal_alias_rules": total_alias_rules,
            "external_alias_connectors": total_alias_ext,
        },
        "chapter_summary": {
            cid: {
                "locs": s["locations"],
                "rules": s["total_rules"],
                "dir": f"{s['dir_satisfied']}/{s['dir_applicable']}",
                "v2_dir_base": s["dir_v2_baseline"],
                "upwar_added": s["dir_upwar_added"],
                "primary_conns": s["primary_internal_connectors"],
                "alias_conns": s["alias_internal_connectors"],
                "markers": s["local_markers"],
                "page": [s["page_width"], s["page_height"]],
            }
            for cid, s in stats.items()
        },
    }, indent=2))
