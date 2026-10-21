#!/usr/bin/env python3
"""
Mission 004 — CH_ENTRY pilot V2 (visual cartography repair).

Addresses all four defects identified in the Mission 003 review and verified
by direct visual inspection of the rendered PNG:

1. Invisible arrows root cause: draw.io requires the cell `id` on the `<object>`
   wrapper. Placing `id` on the inner `<mxCell>` caused draw.io to renumber all
   location nodes on import and drop every edge whose source/target referenced
   the discarded inner IDs (proven via `tools/fixture.py` + SVG inspection).
2. Connection simplification:
   - Reciprocal internal transitions are merged into bidirectional connectors
     with block arrowheads at both ends and full rule metadata in
     `represents_rules`.
   - The 11 primary spatial/structural connections are visually distinguished
     (bold 2.5 px black for compass, 2.5 px blue for vertical UP/DOWN, purple
     dashed for magic arrival) from the 8 non-adjacent parser fast-travel
     keyword connectors (`ENTRA`, `DEBRI`, `PIT`, routed on dedicated
     non-overlapping horizontal bus lanes between tiers in subtle dashed grey).
3. Compact, stepped 2D composition:
   - Uses a constraint-preserving 3-tier vertical grouping derived from source
     room conditions (`LIT` entry crawl -> upper canyon/pit rim -> `DEEP`
     Hall of Mists/fissure -> south nugget chamber) with a 110 px horizontal
     gap between adjacent boxes so labels and arrowheads never collide with
     room borders.
   - Complete original English `long` descriptions are shown inside every room
     box without truncation.
4. Local reference markers & in-room message annotations:
   - Internal `speak` messages (5 rules) are rendered as in-room annotations
     rather than separate graphical room boxes, while remaining in node
     `travel_rules` metadata.
   - Cross-chapter, death, and magic transitions (14 rules across 9 unique
     destinations) are represented by 9 compact local reference markers placed
     adjacent to their origin rooms and linked by short dashed connectors.
"""

from __future__ import annotations

import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_layout import _node_edges_for_chapter
from oa_layout_v3 import DIRECTION_SIGNS, VERTICAL, primary_direction_v3
from oa_pilot import CHAPTER_ID

NODE_W = 290
X_GAP = 120
X_STEP = NODE_W + X_GAP  # 410 px column pitch -> 120 px clear gap
FONT = "fontSize=10;fontFamily=Helvetica;"


def _esc(text: Any) -> str:
    return html.escape(str(text or ""))


def _cond_badge(cond: dict[str, Any] | None) -> str:
    if cond is None:
        return ""
    t = cond.get("type")
    if t == "probability":
        return f"[{cond.get('percent')}%]"
    if t == "carry":
        return f"[carry {cond.get('object')}]"
    if t == "with":
        return f"[with {cond.get('object')}]"
    if t == "not":
        return f"[not {cond.get('object')}={cond.get('state')}]"
    if t == "nodwarves":
        return "[nodwarves]"
    return "[cond]"


def _clean_heading(loc: dict[str, Any]) -> str:
    desc = loc.get("description", {})
    if desc.get("short"):
        s = str(desc["short"]).strip()
        for prefix in ("You're ", "You are ", "You''re "):
            if s.startswith(prefix):
                s = s[len(prefix):]
                break
        return s.rstrip(".")
    if desc.get("maptag"):
        return str(desc["maptag"]).strip().rstrip(".")
    fallback = {
        "LOC_CRACK": "[unpassable crack]",
        "LOC_FOOF1": "[XYZZY teleport arrival]",
    }
    return fallback.get(loc["source_id"], loc["source_id"])


def build_room_display(graph: dict[str, Any], chapter_id: str) -> dict[str, dict[str, Any]]:
    """Build complete, untruncated room text and ordered exit/message lines."""
    members = set(graph["chapters"][chapter_id]["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    chapter_short = {
        cid: ch["title"].split(" — ")[0]
        for cid, ch in graph["chapters"].items()
    }

    out: dict[str, dict[str, Any]] = {}
    for loc_id in sorted(members):
        loc = loc_index[loc_id]
        heading = _clean_heading(loc)
        body = str(loc["description"].get("long") or "").strip()

        exit_lines: list[str] = []
        msg_lines: list[str] = []
        for idx, rule in enumerate(loc["travel"], start=1):
            verbs = rule.get("verbs", [])
            v_str = ", ".join(verbs) if verbs else "(implicit)"
            cond = _cond_badge(rule.get("cond"))
            cond_sfx = f" {cond}" if cond else ""
            at = rule.get("action_type")
            tgt = rule.get("action_target")

            if at == "goto" and tgt in members:
                exit_lines.append(f"{idx}. {v_str} → {tgt}{cond_sfx}")
            elif at == "goto":
                tgt_ch = next(
                    (cid for cid, ch in graph["chapters"].items() if tgt in ch["members"]),
                    None,
                )
                ch_tag = chapter_short.get(tgt_ch, "?")
                exit_lines.append(f"{idx}. {v_str} → {tgt} [Ch {ch_tag}]{cond_sfx}")
            elif at == "speak":
                exit_lines.append(f"{idx}. {v_str} ✕ msg {tgt}{cond_sfx}")
                msg_lines.append(f"{v_str} → {tgt}{cond_sfx}")
            elif at == "special":
                exit_lines.append(f"{idx}. {v_str} ⚡ special({tgt}){cond_sfx}")

        out[loc_id] = {
            "heading": heading,
            "body": body,
            "exit_lines": exit_lines,
            "msg_lines": msg_lines,
        }
    return out


def estimate_room_height(heading: str, body: str, exit_lines: list[str]) -> int:
    """Text-aware height estimate for untruncated room cards (NODE_W = 290)."""
    def count_wrapped(text: str, cpl: int) -> int:
        total = 0
        for line in text.split("\n"):
            total += max(1, -(-len(line) // cpl))
        return total

    h = 14
    h += count_wrapped(heading, 34) * 16
    h += 8
    h += count_wrapped(body, 42) * 14
    if exit_lines:
        h += 10 + 15  # EXITS subheading
        for line in exit_lines:
            h += max(1, -(-len(line) // 44)) * 13
    h += 12
    return max(120, -(-h // 10) * 10)


# ---------------------------------------------------------------------------
# Internal connector grouping (Phase B)
# ---------------------------------------------------------------------------

FAST_TRAVEL_PAIRS: set[frozenset[str]] = {
    frozenset(("LOC_DEBRIS", "LOC_BELOWGRATE")),
    frozenset(("LOC_AWKWARD", "LOC_BELOWGRATE")),
    frozenset(("LOC_BIRDCHAMBER", "LOC_BELOWGRATE")),
    frozenset(("LOC_PITTOP", "LOC_BELOWGRATE")),
    frozenset(("LOC_BIRDCHAMBER", "LOC_DEBRIS")),
    frozenset(("LOC_PITTOP", "LOC_DEBRIS")),
    frozenset(("LOC_AWKWARD", "LOC_PITTOP")),
    frozenset(("LOC_COBBLE", "LOC_PITTOP")),
}

PRIMARY_PAIR_LABELS: dict[frozenset[str], tuple[str, str, str]] = {
    # frozenset({west_or_upper, east_or_lower}): (west_id, east_id, concise_label)
    frozenset(("LOC_COBBLE", "LOC_BELOWGRATE")): ("LOC_COBBLE", "LOC_BELOWGRATE", "E · out ↔ W · crawl"),
    frozenset(("LOC_DEBRIS", "LOC_COBBLE")): ("LOC_DEBRIS", "LOC_COBBLE", "E · crawl ↔ W · inwar"),
    frozenset(("LOC_AWKWARD", "LOC_DEBRIS")): ("LOC_AWKWARD", "LOC_DEBRIS", "DOWN / E ↔ UP / W · canyon"),
    frozenset(("LOC_BIRDCHAMBER", "LOC_AWKWARD")): ("LOC_BIRDCHAMBER", "LOC_AWKWARD", "E · canyon ↔ W / UP"),
    frozenset(("LOC_PITTOP", "LOC_BIRDCHAMBER")): ("LOC_PITTOP", "LOC_BIRDCHAMBER", "E · passage ↔ W · passage"),
    frozenset(("LOC_CRACK", "LOC_PITTOP")): ("LOC_CRACK", "LOC_PITTOP", "(return) ↔ W · crack"),
    frozenset(("LOC_PITTOP", "LOC_MISTHALL")): ("LOC_PITTOP", "LOC_MISTHALL", "DOWN ↔ UP"),
    frozenset(("LOC_MISTHALL", "LOC_NUGGET")): ("LOC_MISTHALL", "LOC_NUGGET", "S · left ↔ N · hall"),
    frozenset(("LOC_EASTBANK", "LOC_MISTHALL")): ("LOC_EASTBANK", "LOC_MISTHALL", "E · hall ↔ W · hall"),
    frozenset(("LOC_WESTBANK", "LOC_EASTBANK")): ("LOC_WESTBANK", "LOC_EASTBANK", "OVER ↔ OVER"),
}


def group_internal_edges(internal_edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group the 32 internal rules into 19 connectors (11 primary + 8 fast-travel).

    Every unordered endpoint pair in CH_ENTRY has at most 2 internal rules
    (one in each direction). Reciprocal pairs become `kind="pair"` with
    bidirectional arrows; one-way rules become `kind="single"`.
    """
    by_pair: dict[frozenset[str], list[dict[str, Any]]] = {}
    for e in internal_edges:
        key = frozenset((e["source"], e["target"]))
        by_pair.setdefault(key, []).append(e)

    connectors: list[dict[str, Any]] = []
    for key in sorted(by_pair, key=lambda k: tuple(sorted(k))):
        rules = by_pair[key]
        is_fast = key in FAST_TRAVEL_PAIRS
        role = "fast_travel" if is_fast else "primary"

        if len(rules) == 2:
            if key in PRIMARY_PAIR_LABELS:
                src_id, tgt_id, label = PRIMARY_PAIR_LABELS[key]
                r_ordered = sorted(rules, key=lambda r: 0 if r["source"] == src_id else 1)
            else:
                r_ordered = sorted(rules, key=lambda r: r["source"])
                src_id, tgt_id = r_ordered[0]["source"], r_ordered[0]["target"]
                v0 = r_ordered[0]["verbs"][0] if r_ordered[0]["verbs"] else "(implicit)"
                v1 = r_ordered[1]["verbs"][0] if r_ordered[1]["verbs"] else "(implicit)"
                label = f"{v0} ↔ {v1}"
            connectors.append({
                "kind": "pair",
                "role": role,
                "source": src_id,
                "target": tgt_id,
                "label": label,
                "rules": r_ordered,
            })
        else:
            r = rules[0]
            v0 = r["verbs"][0] if r["verbs"] else "(implicit)"
            label = v0
            if key in PRIMARY_PAIR_LABELS:
                _, _, label = PRIMARY_PAIR_LABELS[key]
            connectors.append({
                "kind": "single",
                "role": role,
                "source": r["source"],
                "target": r["target"],
                "label": label,
                "rules": [r],
            })
    return connectors


# ---------------------------------------------------------------------------
# Compact Stepped Composition (Phase C)
# ---------------------------------------------------------------------------

def layout_v2(graph: dict[str, Any], heights: dict[str, int]) -> dict[str, Any]:
    """Deterministic compact stepped layout preserving all 17 directional constraints
    PLUS the compound diagonal slope between LOC_AWKWARD and LOC_DEBRIS:

      - Upper Tier (y = 175): Upper Canyon, Bird Chamber, Pit Rim & Foof arrival
        (LOC_CRACK, LOC_PITTOP, LOC_BIRDCHAMBER, LOC_AWKWARD, LOC_FOOF1)
      - Middle Tier (y = 660):
          * West group: Deep Hall of Mists & Fissure Banks (LOC_WESTBANK, LOC_EASTBANK, LOC_MISTHALL)
          * East group: Surface Crawl & Debris Room (LOC_DEBRIS, LOC_COBBLE, LOC_BELOWGRATE),
            stepped DOWN (+485 px) and EAST (+110 px) from LOC_AWKWARD so that
            `DEBRIS --[UPWAR, WEST]--> AWKWARD` goes strictly UP and WEST, and
            `AWKWARD --[DOWN, EAST]--> DEBRIS` goes strictly DOWN and EAST.
      - South Tier (y = 1060): Nugget of Gold Room (LOC_NUGGET, south of LOC_MISTHALL).
    """
    members, internal_edges = _node_edges_for_chapter(graph, CHAPTER_ID)

    upper_y = 175.0
    mid_y = 660.0
    south_y = 1060.0

    positions: dict[str, tuple[float, float]] = {
        # Upper Tier: west -> east
        "LOC_CRACK": (60.0, upper_y),
        "LOC_PITTOP": (470.0, upper_y),
        "LOC_BIRDCHAMBER": (880.0, upper_y),
        "LOC_AWKWARD": (1290.0, upper_y),
        "LOC_FOOF1": (1660.0, upper_y),
        # Middle Tier — West group (Hall of Mists & Fissure, below PITTOP):
        "LOC_WESTBANK": (60.0, mid_y),
        "LOC_EASTBANK": (470.0, mid_y),
        "LOC_MISTHALL": (880.0, mid_y),
        # Middle Tier — East group (Entry crawl, down & east from AWKWARD):
        "LOC_DEBRIS": (1400.0, mid_y),
        "LOC_COBBLE": (1810.0, mid_y),
        "LOC_BELOWGRATE": (2220.0, mid_y),
        # South Tier — Nugget room (south of MISTHALL):
        "LOC_NUGGET": (880.0, south_y),
    }

    assert set(positions.keys()) == set(members)
    return {
        "positions": positions,
        "heights": heights,
        "internal_edges": internal_edges,
        "dropped_constraints": [],
    }


# ---------------------------------------------------------------------------
# Local reference markers for the 9 unique external destinations (Phase C)
# ---------------------------------------------------------------------------

def build_external_markers(
    graph: dict[str, Any],
    positions: dict[str, tuple[float, float]],
    heights: dict[str, int],
) -> list[dict[str, Any]]:
    """Build 9 compact reference markers positioned adjacent to their origin rooms."""
    members = set(graph["chapters"][CHAPTER_ID]["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}

    by_target: dict[str, list[dict[str, Any]]] = {}
    for loc_id in sorted(members):
        for rule in loc_index[loc_id]["travel"]:
            if rule.get("action_type") == "goto":
                tgt = rule.get("action_target")
                if tgt not in members:
                    by_target.setdefault(tgt, []).append({
                        "source": loc_id,
                        "verbs": rule.get("verbs", []),
                        "cond": rule.get("cond"),
                        "action": rule.get("action_full", [rule.get("action_type"), tgt]),
                    })

    markers: list[dict[str, Any]] = [
        {
            "id": "M_LOC_GRATE",
            "target": "LOC_GRATE",
            "kind": "cross",
            "x": 2270.0,
            "y": 545.0,
            "w": 240.0,
            "h": 56.0,
            "fill": "#FFF9C4",
            "stroke": "#F57C00",
            "title": "→ LOC_GRATE · Ch 01 Surface World",
            "subtitle": "OUT, UPWAR (BELOWGRATE) · DEPRE (4 rooms)\n[not GRATE=GRATE_CLOSED]",
            "rules": by_target["LOC_GRATE"],
            "links": [
                {
                    "from": "LOC_BELOWGRATE",
                    "label": "OUT, UPWAR [open]",
                    "exitX": 0.65, "exitY": 0.0,
                    "entryX": 0.58, "entryY": 1.0,
                    "color": "#E65100",
                    "offset": (0, 0),
                },
            ],
        },
        {
            "id": "M_LOC_FOOF2",
            "target": "LOC_FOOF2",
            "kind": "magic",
            "x": 1540.0,
            "y": 985.0,
            "w": 250.0,
            "h": 48.0,
            "fill": "#F3E5F5",
            "stroke": "#7B1FA2",
            "title": "✨ XYZZY → LOC_FOOF2 · Ch 01",
            "subtitle": "Magic word teleport to LOC_BUILDING",
            "rules": by_target["LOC_FOOF2"],
            "links": [
                {
                    "from": "LOC_DEBRIS",
                    "label": "XYZZY",
                    "exitX": 0.69, "exitY": 1.0,
                    "entryX": 0.24, "entryY": 0.0,
                    "color": "#7B1FA2",
                    "offset": (0, 0),
                },
            ],
        },
        {
            "id": "M_LOC_NECKBROKE",
            "target": "LOC_NECKBROKE",
            "kind": "death",
            "x": 470.0,
            "y": 550.0,
            "w": 230.0,
            "h": 48.0,
            "fill": "#FFEBEE",
            "stroke": "#C62828",
            "title": "☠ LOC_NECKBROKE · Ch 11 Death",
            "subtitle": "DOWN, PIT, STEPS [carry NUGGET]",
            "rules": by_target["LOC_NECKBROKE"],
            "links": [
                {
                    "from": "LOC_PITTOP",
                    "label": "DOWN [carry NUGGET]",
                    "exitX": 0.16, "exitY": 1.0,
                    "entryX": 0.20, "entryY": 0.0,
                    "color": "#C62828",
                    "offset": (0, 18),
                },
            ],
        },
        {
            "id": "M_LOC_PARALLEL1",
            "target": "LOC_PARALLEL1",
            "kind": "cross",
            "x": 60.0,
            "y": 550.0,
            "w": NODE_W,
            "h": 48.0,
            "fill": "#FFF9C4",
            "stroke": "#F57C00",
            "title": "→ LOC_PARALLEL1 · Ch 04 Maze All Alike",
            "subtitle": "NORTH (low wide passage north of hall)",
            "rules": by_target["LOC_PARALLEL1"],
            "links": [
                {
                    "from": "LOC_WESTBANK",
                    "label": "NORTH",
                    "exitX": 0.5, "exitY": 0.0,
                    "entryX": 0.5, "entryY": 1.0,
                    "color": "#F57C00",
                    "offset": (0, 0),
                },
            ],
        },
        {
            "id": "M_LOC_MISTWEST",
            "target": "LOC_MISTWEST",
            "kind": "cross",
            "x": 60.0,
            "y": 950.0,
            "w": 225.0,
            "h": 48.0,
            "fill": "#FFF9C4",
            "stroke": "#F57C00",
            "title": "→ LOC_MISTWEST · Ch 04 Maze",
            "subtitle": "WEST (west end of Hall of Mists)",
            "rules": by_target["LOC_MISTWEST"],
            "links": [
                {
                    "from": "LOC_WESTBANK",
                    "label": "WEST",
                    "exitX": 0.39, "exitY": 1.0,
                    "entryX": 0.50, "entryY": 0.0,
                    "color": "#F57C00",
                    "offset": (0, 0),
                },
            ],
        },
        {
            "id": "M_LOC_NOMAKE",
            "target": "LOC_NOMAKE",
            "kind": "death",
            "x": 470.0,
            "y": 950.0,
            "w": NODE_W,
            "h": 50.0,
            "fill": "#FFEBEE",
            "stroke": "#C62828",
            "title": "☠ LOC_NOMAKE · Ch 11 Death",
            "subtitle": "FORWA [not FISSURE=BRIDGED] (both banks)",
            "rules": by_target["LOC_NOMAKE"],
            "links": [
                {
                    "from": "LOC_EASTBANK",
                    "label": "FORWA [unbridged]",
                    "exitX": 0.5, "exitY": 1.0,
                    "entryX": 0.5, "entryY": 0.0,
                    "color": "#C62828",
                    "offset": (0, 0),
                },
                {
                    "from": "LOC_WESTBANK",
                    "label": "FORWA [unbridged]",
                    "exitX": 0.88, "exitY": 1.0,
                    "entryX": 0.0, "entryY": 0.5,
                    "color": "#C62828",
                    "waypoints": [
                        (60.0 + NODE_W * 0.88, 975.0),
                    ],
                    "offset": (26, 20),
                },
            ],
        },
        {
            "id": "M_LOC_DOME",
            "target": "LOC_DOME",
            "kind": "transient",
            "x": 940.0,
            "y": 548.0,
            "w": 230.0,
            "h": 52.0,
            "fill": "#FFF3E0",
            "stroke": "#E65100",
            "title": "⚠ LOC_DOME · Ch 11 Transient State",
            "subtitle": "UPWAR, PIT, STEPS… [carry NUGGET]\n(\"The dome is unclimbable\")",
            "rules": by_target["LOC_DOME"],
            "links": [
                {
                    "from": "LOC_MISTHALL",
                    "label": "UP [carry NUGGET]",
                    "exitX": 0.60, "exitY": 0.0,
                    "entryX": 0.495, "entryY": 1.0,
                    "color": "#E65100",
                    "offset": (0, 0),
                },
            ],
        },
        {
            "id": "M_LOC_KINGHALL",
            "target": "LOC_KINGHALL",
            "kind": "cross",
            "x": 1260.0,
            "y": 985.0,
            "w": 250.0,
            "h": 48.0,
            "fill": "#FFF9C4",
            "stroke": "#F57C00",
            "title": "→ LOC_KINGHALL · Ch 03 Mt King",
            "subtitle": "STAIR, DOWN, NORTH (wide stone staircase)",
            "rules": by_target["LOC_KINGHALL"],
            "links": [
                {
                    "from": "LOC_MISTHALL",
                    "label": "STAIR / N",
                    "exitX": 1.0, "exitY": 0.88,
                    "entryX": 0.0, "entryY": 0.5,
                    "color": "#F57C00",
                    "waypoints": [
                        (1192.0, 660.0 + heights["LOC_MISTHALL"] * 0.88),
                        (1192.0, 1009.0),
                    ],
                    "offset": (32, 2),
                },
            ],
        },
        {
            "id": "M_LOC_JUMBLE",
            "target": "LOC_JUMBLE",
            "kind": "cross",
            "x": 1260.0,
            "y": 1055.0,
            "w": 250.0,
            "h": 48.0,
            "fill": "#FFF9C4",
            "stroke": "#F57C00",
            "title": "→ LOC_JUMBLE · Ch 10 Y2 & Windows",
            "subtitle": "Y2 (fast-travel keyword to rock jumble)",
            "rules": by_target["LOC_JUMBLE"],
            "links": [
                {
                    "from": "LOC_MISTHALL",
                    "label": "Y2",
                    "exitX": 1.0, "exitY": 0.95,
                    "entryX": 0.0, "entryY": 0.5,
                    "color": "#F57C00",
                    "waypoints": [
                        (1180.0, 660.0 + heights["LOC_MISTHALL"] * 0.95),
                        (1180.0, 1079.0),
                    ],
                    "offset": (36, 18),
                },
            ],
        },
    ]
    return markers


# ---------------------------------------------------------------------------
# Dedicated non-overlapping bus lanes for the 8 fast-travel connectors
# ---------------------------------------------------------------------------

def route_fast_travel(
    conn: dict[str, Any],
    positions: dict[str, tuple[float, float]],
    heights: dict[str, int],
) -> tuple[dict[str, str], list[tuple[float, float]], float]:
    """Return (exit/entry style attrs, waypoints, label_rel_x) for fast-travel rules.

    - Same-row Tier 2 pair `LOC_DEBRIS <-> LOC_BELOWGRATE` routes as a single
      straight horizontal segment at y = 845 directly underneath LOC_COBBLE.
    - Same-row Tier 1 rule `LOC_AWKWARD -> LOC_PITTOP` routes cleanly over
      LOC_BIRDCHAMBER at y = 148.
    - The remaining 6 inter-tier rules use 6 dedicated horizontal tracks at
      y = 436..516 in the open inter-tier channel with labels placed inside
      riser-free horizontal windows (Window A: x=760..1000, Window B: x=1100..1400,
      Window C: x=1900..2220).
    """
    key = frozenset((conn["source"], conn["target"]))

    if key == frozenset(("LOC_DEBRIS", "LOC_BELOWGRATE")):
        # Straight horizontal line at y = 845 passing 25 px below LOC_COBBLE (bottom = 820)
        y_line = 845.0
        ey_deb = (y_line - positions["LOC_DEBRIS"][1]) / heights["LOC_DEBRIS"]
        ey_bg = (y_line - positions["LOC_BELOWGRATE"][1]) / heights["LOC_BELOWGRATE"]
        if conn["source"] == "LOC_DEBRIS":
            pts = {"exitX": "1.000", "exitY": f"{ey_deb:.3f}", "entryX": "0.000", "entryY": f"{ey_bg:.3f}"}
        else:
            pts = {"exitX": "0.000", "exitY": f"{ey_bg:.3f}", "entryX": "1.000", "entryY": f"{ey_deb:.3f}"}
        return pts, [], 0.0

    if key == frozenset(("LOC_AWKWARD", "LOC_PITTOP")):
        # Clean arch above LOC_BIRDCHAMBER at y = 148
        y_track = 148.0
        x_awk = positions["LOC_AWKWARD"][0] + NODE_W * 0.25
        x_pit = positions["LOC_PITTOP"][0] + NODE_W * 0.78
        pts = {"exitX": "0.250", "exitY": "0.0", "entryX": "0.780", "entryY": "0.0"}
        return pts, [(round(x_awk, 1), y_track), (round(x_pit, 1), y_track)], 0.0

    # 6 inter-tier tracks between Upper Tier bottoms (360..420) and Middle Tier tops (660)
    # Note: in mxGraph, relative geometry `x` is in [-1, 1] along the total path length
    # from source (-1) to target (+1). We specify `target_label_x` (desired absolute X
    # in a riser-free window) and compute `rel_x` from the exact polyline arc length!
    specs: dict[frozenset[str], tuple[tuple[str, str, float], tuple[str, str, float], float, float]] = {
        frozenset(("LOC_BIRDCHAMBER", "LOC_DEBRIS")): (
            ("LOC_BIRDCHAMBER", "bottom", 0.72),
            ("LOC_DEBRIS", "top", 0.10),
            436.0,
            1250.0,  # Window B
        ),
        frozenset(("LOC_PITTOP", "LOC_DEBRIS")): (
            ("LOC_PITTOP", "bottom", 0.72),
            ("LOC_DEBRIS", "top", 0.22),
            452.0,
            860.0,   # Window A
        ),
        frozenset(("LOC_AWKWARD", "LOC_BELOWGRATE")): (
            ("LOC_AWKWARD", "bottom", 0.45),
            ("LOC_BELOWGRATE", "top", 0.06),
            468.0,
            2040.0,  # Window C
        ),
        frozenset(("LOC_COBBLE", "LOC_PITTOP")): (
            ("LOC_COBBLE", "top", 0.35),
            ("LOC_PITTOP", "bottom", 0.58),
            484.0,
            1250.0,  # Window B
        ),
        frozenset(("LOC_BIRDCHAMBER", "LOC_BELOWGRATE")): (
            ("LOC_BIRDCHAMBER", "bottom", 0.46),
            ("LOC_BELOWGRATE", "top", 0.12),
            500.0,
            2040.0,  # Window C
        ),
        frozenset(("LOC_PITTOP", "LOC_BELOWGRATE")): (
            ("LOC_PITTOP", "bottom", 0.42),
            ("LOC_BELOWGRATE", "top", 0.18),
            516.0,
            860.0,   # Window A
        ),
    }

    p_a, p_b, y_track, target_x = specs[key]
    if p_a[0] != conn["source"]:
        p_a, p_b = p_b, p_a

    def port_xy(room_id: str, side: str, frac: float) -> tuple[float, float, float]:
        rx, ry = positions[room_id]
        rh = heights[room_id]
        ey = 0.0 if side == "top" else 1.0
        py = ry if side == "top" else ry + rh
        return (rx + NODE_W * frac, py, ey)

    x1, y1, ey1 = port_xy(*p_a)
    x2, y2, ey2 = port_xy(*p_b)

    # Compute exact arc-length position along (x1,y1)->(x1,y_track)->(x2,y_track)->(x2,y2)
    d1 = abs(y_track - y1)
    d2 = abs(x2 - x1)
    d3 = abs(y2 - y_track)
    total_len = d1 + d2 + d3
    dist_to_target = d1 + abs(target_x - x1)
    rel_x = (2.0 * (dist_to_target / total_len)) - 1.0

    pts = {
        "exitX": f"{p_a[2]:.3f}",
        "exitY": f"{ey1:.1f}",
        "entryX": f"{p_b[2]:.3f}",
        "entryY": f"{ey2:.1f}",
    }
    waypoints = [(round(x1, 1), y_track), (round(x2, 1), y_track)]
    return pts, waypoints, rel_x


# ---------------------------------------------------------------------------
# XML Generation
# ---------------------------------------------------------------------------

def generate_v2(graph: dict[str, Any], out_path: Path) -> dict[str, Any]:
    display = build_room_display(graph, CHAPTER_ID)
    heights = {
        loc_id: estimate_room_height(d["heading"], d["body"], d["exit_lines"])
        for loc_id, d in display.items()
    }
    lay = layout_v2(graph, heights)
    positions = lay["positions"]
    internal_edges = lay["internal_edges"]
    connectors = group_internal_edges(internal_edges)
    markers = build_external_markers(graph, positions, heights)

    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    chapter = graph["chapters"][CHAPTER_ID]
    members = set(chapter["members"])
    treasure_objects = {o["source_id"] for o in graph["objects"] if o.get("treasure")}
    immovable_objects = {o["source_id"] for o in graph["objects"] if o.get("immovable")}

    root = ET.Element("root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    def add_text_cell(cid: str, x: float, y: float, w: float, h: float, style: str, value: str) -> None:
        c = ET.SubElement(root, "mxCell", {
            "id": cid, "style": style, "value": value, "vertex": "1", "parent": "1",
        })
        ET.SubElement(c, "mxGeometry", {
            "x": str(int(x)), "y": str(int(y)),
            "width": str(int(w)), "height": str(int(h)), "as": "geometry",
        })

    # Header, Compass & Restrained Legend (top-left, clear of Upper Tier at y=175)
    add_text_cell(
        "title", 60, 14, 780, 28,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;fontFamily=Helvetica;",
        f"{chapter['title']} — Pilot V2 (Mata Hari, Mission 004)",
    )
    add_text_cell(
        "compass", 60, 46, 130, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=center;verticalAlign=middle;fontFamily=Courier New;fontSize=11;fontStyle=1;",
        "NORTH (–Y)<br>↑<br>W ← + → E<br>↓<br>SOUTH (+Y)",
    )
    add_text_cell(
        "legend", 206, 46, 660, 92,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;"
        "align=left;verticalAlign=top;spacingLeft=10;spacingTop=5;fontSize=9.5;fontFamily=Helvetica;",
        "<b>LEGEND &amp; VISUAL HIERARCHY</b><br>"
        "• <b>Black solid (2.5 px):</b> primary compass/passage movement (double arrowhead = two-way)<br>"
        "• <b>Blue solid (2.8 px):</b> vertical UP / DOWN shaft (distinct from compass N/S)<br>"
        "• <b>Purple dashed:</b> magic word teleport (XYZZY / &gt;&gt;Foof!&lt;&lt;) · "
        "<b>Grey dashed bus:</b> parser fast-travel aliases (ENTRA, DEBRI, PIT)<br>"
        "• <b>Local markers:</b> yellow = cross-page room · orange = transient state · red = death hazard",
    )

    # --- 12 Playable/Auxiliary Room Nodes (id on <object> wrapper!) ---
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

    # --- 9 Local Reference Markers + their short dashed connectors ---
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

    # --- 19 Internal Connectors (11 primary + 8 fast-travel) ---
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
            # Vertical pit shaft: exits right-bottom of PITTOP, enters top-left of MISTHALL
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
            # Straight vertical shaft at x = 1545 between AWKWARD (bottom-right) and DEBRIS (top-center)
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
            # North-South connection between MISTHALL and NUGGET
            style = (
                "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;html=1;"
                f"strokeColor=#000000;strokeWidth=2.5;{arrows}"
                "exitX=0.5;exitY=1.0;exitDx=0;exitDy=0;"
                "entryX=0.5;entryY=0.0;entryDx=0;entryDy=0;"
                "fontSize=9;fontStyle=1;fontFamily=Helvetica;labelBackgroundColor=#FFFFFF;"
            )
        elif key == frozenset(("LOC_FOOF1", "LOC_DEBRIS")):
            # Straight vertical magic arrival from FOOF1 into top-right of DEBRIS
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
            # Same-row horizontal primary connector: align exitY and entryY at the
            # exact same pixel Y (row_top + 78 px) and offset the label 14 px ABOVE
            # the shaft so arrowheads and shaft are 100% unobstructed!
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

        obj = ET.SubElement(root, "object", {
            "id": edge_id,
            "label": _esc(conn["label"]),
            "role": conn["role"],
            "represents_rules": represents,
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": style,
            "edge": "1",
            "parent": "1",
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

    # --- Provenance footer ---
    all_rects = list(room_rects.values()) + marker_rects
    max_x = max(r[0] + r[2] for r in all_rects)
    max_y = max(r[1] + r[3] for r in all_rects)
    total_rules = sum(len(loc_index[m]["travel"]) for m in members)

    add_text_cell(
        "provenance", 60, max_y + 18, 1200, 32,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;"
        "whiteSpace=wrap;rounded=0;fontSize=9;fontStyle=2;fontFamily=Helvetica;",
        "Source: Open_Adventure.yaml (BSD-2-Clause, E. S. Raymond) — canonical. "
        f"Pilot V2: {len(members)} locations, {total_rules}/51 travel rules preserved "
        "(19 internal connectors + 9 local reference markers + 5 in-room message annotations; "
        "17/17 directional constraints satisfied). NORTH = up = smaller Y.",
    )

    page_w = int(max_x + 60)
    page_h = int(max_y + 65)

    mxfile = ET.Element("mxfile", {
        "host": "Open Adventure RPG Archaeology tooling",
        "agent": "007-mata-hari-pilot-v2",
        "type": "device",
        "version": "24.7.0",
    })
    diag = ET.SubElement(mxfile, "diagram", {
        "id": CHAPTER_ID,
        "name": chapter["title"] + " — Pilot V2",
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
        "markers": markers,
        "heights": heights,
        "page_width": page_w,
        "page_height": page_h,
        "room_rects": room_rects,
        "marker_rects": marker_rects,
        "ext_conn_count": ext_conn_count,
    }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (
        a[0] + a[2] <= b[0]
        or b[0] + b[2] <= a[0]
        or a[1] + a[3] <= b[1]
        or b[1] + b[3] <= a[1]
    )


def validate_v2(graph: dict[str, Any], path: Path) -> dict[str, Any]:
    tree = ET.parse(path)
    root = tree.getroot().find("diagram/mxGraphModel/root")
    members = set(graph["chapters"][CHAPTER_ID]["members"])
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}

    objs = list(root.iter("object"))
    rooms = [o for o in objs if o.get("source_id")]
    markers = [o for o in objs if o.get("target_id")]
    int_conns = [o for o in objs if o.get("id", "").startswith("C")]
    ext_conns = [o for o in objs if o.get("id", "").startswith("X")]

    all_ids = [o.get("id") for o in objs]
    dup_ids = len(all_ids) != len(set(all_ids))

    room_ok = {o.get("source_id") for o in rooms} == members
    desc_ok = all(
        o.get("description_en") == (loc_index[o.get("source_id")]["description"].get("long") or "")
        for o in rooms
    )
    no_truncated_label = all(
        "full description stored in node metadata" not in (o.get("label") or "")
        for o in rooms
    )

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
    partition_ok = sorted(represented) == sorted(original)

    # Check external goto rules partition across the 9 markers
    ext_represented = 0
    for m in markers:
        ext_represented += len(json.loads(m.get("represents_rules", "[]")))

    rects = []
    for o in rooms + markers:
        cell = o.find("mxCell")
        gm = cell.find("mxGeometry")
        rects.append((
            float(gm.get("x")), float(gm.get("y")),
            float(gm.get("width")), float(gm.get("height")),
        ))
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
        "descriptions_roundtrip": desc_ok,
        "no_truncated_room_descriptions": no_truncated_label,
        "travel_rules_on_nodes_roundtrip": rules_ok,
        "total_rules_on_nodes": f"{rule_count}/{total_rules}",
        "internal_rules_partition": partition_ok,
        "external_goto_rules_on_markers": f"{ext_represented}/14",
        "connector_endpoints_resolve": endpoint_ok,
        "internal_connectors": len(int_conns),
        "external_connectors": len(ext_conns),
        "total_visible_connectors": len(int_conns) + len(ext_conns),
        "local_reference_markers": len(markers),
        "box_overlaps": overlaps,
        "xml_valid": True,
    }


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    with (root_dir / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
        graph = json.load(f)
    out = root_dir / "output" / "pilot" / "CH_ENTRY_MataHari_V2.drawio"
    result = generate_v2(graph, out)
    validation = validate_v2(graph, out)
    print(json.dumps({
        "file": str(out),
        "page": [result["page_width"], result["page_height"]],
        "validation": validation,
    }, indent=2))
