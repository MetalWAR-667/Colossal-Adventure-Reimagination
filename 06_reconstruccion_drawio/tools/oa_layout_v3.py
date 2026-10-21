#!/usr/bin/env python3
"""
Mission 003 — constraint-solver layout (v3) for the CH_ENTRY pilot.

Replaces the V2 greedy BFS + constraint-blind overlap pushing with:

1. Correct direction classification (UPWAR is the source symbol for
   vertical up; V2 checked a non-existent "UP" symbol).
2. Difference constraints (coord[j] >= coord[i] + gap) solved exactly
   with Bellman-Ford longest paths, per axis.
3. Positive-cycle detection -> proven contradictory constraints are
   dropped and reported, never silently violated.
4. Text-aware node heights computed BEFORE layout so vertical gaps
   always clear the actual boxes.
5. Deterministic slot search for nodes with free axes, anchored to
   their first internal neighbour.
6. Constraint-aware overlap resolution as a safety net.

No gameplay semantics are modified; only (x, y) coordinates differ.
"""

from __future__ import annotations

from typing import Any

from oa_layout import _node_edges_for_chapter, _primary_direction

# Corrected travel-verb direction set (source YAML symbols).
# "UPWAR" is the symbol used in travel rules; "UP" never appears.
DIRECTION_SIGNS: dict[str, tuple[int, int]] = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST": (1, 0),
    "WEST": (-1, 0),
    "NE": (1, -1),
    "SE": (1, 1),
    "SW": (-1, 1),
    "NW": (-1, -1),
    "UPWAR": (0, -1),  # vertical up — distinct category, same axis sign
    "DOWN": (0, 1),    # vertical down
}
VERTICAL = {"UPWAR", "DOWN"}

# Box geometry (pixels).
NODE_W = 300
X_GAP = 60
Y_GAP = 60
MIN_H = 110

# Text estimation (conservative → taller boxes, safer than overflow).
CHARS_PER_LINE_BODY = 40
CHARS_PER_LINE_HEAD = 34
CHARS_PER_LINE_EXIT = 44
LINE_H_HEAD = 18
LINE_H_BODY = 15
LINE_H_EXIT = 14


def primary_direction_v3(edge: dict[str, Any]) -> str | None:
    """Corrected primary-direction classifier (UPWAR fixed)."""
    verbs = set(edge.get("verbs", []))
    for d in ("NORTH", "SOUTH", "EAST", "WEST", "NE", "SE", "SW", "NW", "UPWAR", "DOWN"):
        if d in verbs:
            return d
    return None


def estimate_height(heading: str, body: str, exit_lines: list[str]) -> int:
    """Deterministic text-aware box height estimate."""
    def wrap(text: str, cpl: int) -> int:
        lines = 0
        for para in text.split("\n"):
            n = max(1, -(-len(para) // cpl))
            lines += n
        return lines

    h = 10  # top padding
    h += wrap(heading, CHARS_PER_LINE_HEAD) * LINE_H_HEAD
    h += 6
    h += wrap(body or "(no long description)", CHARS_PER_LINE_BODY) * LINE_H_BODY
    if exit_lines:
        h += 8 + LINE_H_HEAD  # "EXITS" header
        for line in exit_lines:
            h += max(1, -(-len(line) // CHARS_PER_LINE_EXIT)) * LINE_H_EXIT
    h += 10  # bottom padding
    h = max(MIN_H, h)
    return -(-h // 10) * 10  # round up to multiple of 10


def build_constraints(internal_edges: list[dict[str, Any]],
                      heights: dict[str, int]) -> tuple[list, list]:
    """Convert directional edges into per-axis difference constraints.

    A constraint is (u, v, w, ref) meaning coord[v] >= coord[u] + w.
    """
    x_cons: list[tuple[str, str, float, tuple]] = []
    y_cons: list[tuple[str, str, float, tuple]] = []

    def ygap(a: str, b: str) -> float:
        return float(max(heights.get(a, MIN_H), heights.get(b, MIN_H)) + Y_GAP)

    xstep = float(NODE_W + X_GAP)

    for e in internal_edges:
        d = primary_direction_v3(e)
        if d is None:
            continue
        sx, sy = DIRECTION_SIGNS[d]
        src, tgt = e["source"], e["target"]
        ref = (src, d, tgt)
        if sx > 0:  # target east of source
            x_cons.append((src, tgt, xstep, ref))
        elif sx < 0:  # target west of source
            x_cons.append((tgt, src, xstep, ref))
        if sy > 0:  # target south of source
            y_cons.append((src, tgt, ygap(src, tgt), ref))
        elif sy < 0:  # target north of source
            y_cons.append((tgt, src, ygap(src, tgt), ref))
    return x_cons, y_cons


def solve_axis(nodes: list[str], constraints: list[tuple[str, str, float, tuple]]):
    """Bellman-Ford longest path from a virtual source (all dist 0).

    Returns (coords, dropped) where dropped lists constraints removed
    because they participated in a positive (unsatisfiable) cycle.
    """
    active = list(constraints)
    dropped: list[dict[str, Any]] = []
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    while True:
        dist = [0.0] * n
        parent = [-1] * n
        parent_cons: list = [None] * n
        last_updated = -1
        for _ in range(n):
            changed = False
            for c in active:
                u, v, w, ref = c
                if dist[idx[v]] < dist[idx[u]] + w:
                    dist[idx[v]] = dist[idx[u]] + w
                    parent[idx[v]] = idx[u]
                    parent_cons[idx[v]] = c
                    changed = True
                    last_updated = idx[v]
            if not changed:
                break
        else:
            pass
        # Positive cycle iff an update occurred in the n-th relaxation round.
        # Detect: run one extra round; any update proves a positive cycle.
        extra = False
        for c in active:
            u, v, w, ref = c
            if dist[idx[v]] < dist[idx[u]] + w:
                extra = True
                break
        if not extra:
            return {nodes[i]: dist[i] for i in range(n)}, dropped

        # Find the cycle: walk parents n times from last_updated.
        node = last_updated
        for _ in range(n):
            node = parent[node]
        cycle = []
        cur = node
        while True:
            cycle.append(cur)
            cur = parent[cur]
            if cur == node:
                break
        cycle_set = set(cycle)
        # Constraints on the cycle: those used as parent edges between cycle nodes.
        cyc_cons = []
        seen = set()
        for cn in cycle:
            c = parent_cons[cn]
            if c is not None and id(c) not in seen:
                seen.add(id(c))
                cyc_cons.append(c)
        # Deterministic drop: alphabetically last ref in the cycle.
        cyc_cons.sort(key=lambda c: str(c[3]))
        victim = cyc_cons[-1]
        active.remove(victim)
        dropped.append({
            "dropped": victim[3],
            "cycle_nodes": sorted(nodes[i] for i in cycle_set),
            "cycle_constraints": [str(c[3]) for c in cyc_cons],
        })


def _box(x: float, y: float, h: int) -> tuple[float, float, float, float]:
    return (x, y, float(NODE_W), float(h))


def _overlaps(a: tuple[float, float, float, float], b: tuple[float, float, float, float],
              margin: float = 0.0) -> bool:
    return not (a[0] + a[2] + margin <= b[0] or b[0] + b[2] + margin <= a[0] or
                a[1] + a[3] + margin <= b[1] or b[1] + b[3] + margin <= a[1])


def _anchor_map(nodes: list[str], internal_edges: list[dict[str, Any]]) -> dict[str, str]:
    """First internal neighbour (in source edge order) for each node."""
    anchor: dict[str, str] = {}
    for e in internal_edges:
        s, t = e["source"], e["target"]
        if s not in anchor:
            anchor[s] = t
        if t not in anchor:
            anchor[t] = s
    return anchor


def layout_chapter_v3(graph: dict[str, Any], chapter_id: str,
                      heights: dict[str, int],
                      hints: dict[str, str] | None = None) -> dict[str, Any]:
    """Compute constraint-solved positions for one chapter.

    hints: optional editorial placement hints {node: "west_of"/"east_of"/
    "north_of"/"south_of": anchor} — documented, reviewable, and never
    affecting compass-constraint metrics.
    """
    members, internal_edges = _node_edges_for_chapter(graph, chapter_id)
    nodes = sorted(members)
    hints = hints or {}

    x_cons, y_cons = build_constraints(internal_edges, heights)

    constrained_x = {n for c in x_cons for n in (c[0], c[1])}
    constrained_y = {n for c in y_cons for n in (c[0], c[1])}

    x0, dropped_x = solve_axis(nodes, x_cons)
    y0, dropped_y = solve_axis(nodes, y_cons)
    dropped = dropped_x + dropped_y

    pos: dict[str, tuple[float, float]] = {}
    boxes: dict[str, tuple[float, float, float, float]] = {}

    def step_y(a: str, b: str) -> float:
        return float(max(heights.get(a, MIN_H), heights.get(b, MIN_H)) + Y_GAP)

    step_x = float(NODE_W + X_GAP)

    def try_place(n: str, x: float, y: float) -> bool:
        """Place n at (x, y) if no overlap with placed boxes and no
        directional constraint is violated."""
        bx = _box(x, y, heights.get(n, MIN_H))
        for other, ob in boxes.items():
            if _overlaps(bx, ob, margin=20):
                return False
        # Constraint check over all directional edges.
        for e in internal_edges:
            d = primary_direction_v3(e)
            if d is None:
                continue
            s, t = e["source"], e["target"]
            if s != n and t != n:
                continue
            sx_, sy_ = pos.get(s, (x0.get(s, 0.0), y0.get(s, 0.0)))
            tx_, ty_ = pos.get(t, (x0.get(t, 0.0), y0.get(t, 0.0)))
            if s == n:
                sx_, sy_ = x, y
            if t == n:
                tx_, ty_ = x, y
            dx = tx_ - sx_
            dy = ty_ - sy_
            vx, vy = DIRECTION_SIGNS[d]
            if vx > 0 and not dx > 1: return False
            if vx < 0 and not dx < -1: return False
            if vy > 0 and not dy > 1: return False
            if vy < 0 and not dy < -1: return False
        return True

    anchors = _anchor_map(nodes, internal_edges)

    # Candidate orders. Free-axis nodes inherit their anchor's coordinate,
    # then search outward. Fully-free nodes search around their anchor.
    for n in nodes:
        h = heights.get(n, MIN_H)
        anchor = anchors.get(n, n)
        ax = x0.get(n) if n in constrained_x else None
        ay = y0.get(n) if n in constrained_y else None

        # Build candidate (x, y) list.
        cands: list[tuple[float, float]] = []
        if ax is not None and ay is not None:
            cands = [(ax, ay)]
        elif ax is not None:
            base_y = pos.get(anchor, (x0.get(anchor, 0.0), y0.get(anchor, 0.0)))[1]
            for dy in (0, -1, 1, -2, 2):
                cands.append((ax, base_y + dy * step_y(n, anchor)))
        elif ay is not None:
            base_x = pos.get(anchor, (x0.get(anchor, 0.0), y0.get(anchor, 0.0)))[0]
            for dx in (0, -1, 1, -2, 2):
                cands.append((base_x + dx * step_x, ay))
        else:
            base = pos.get(anchor, (x0.get(anchor, 0.0), y0.get(anchor, 0.0)))
            hint = hints.get(n)
            orders = {
                "west_of": [(-1, 0), (0, -1), (0, 1), (1, 0), (-2, 0), (0, -2), (0, 2), (2, 0)],
                "east_of": [(1, 0), (0, -1), (0, 1), (-1, 0), (2, 0), (0, -2), (0, 2), (-2, 0)],
                "north_of": [(0, -1), (-1, 0), (1, 0), (0, 1), (0, -2), (-2, 0), (2, 0), (0, 2)],
                "south_of": [(0, 1), (-1, 0), (1, 0), (0, -1), (0, 2), (-2, 0), (2, 0), (0, -2)],
            }
            offsets = orders.get(hint, [(0, -1), (0, 1), (-1, 0), (1, 0), (0, -2), (0, 2), (-2, 0), (2, 0)])
            cands.append(base)
            for dx, dy in offsets:
                cands.append((base[0] + dx * step_x, base[1] + dy * step_y(n, anchor)))

        placed = False
        for (cx, cy) in cands:
            if try_place(n, cx, cy):
                pos[n] = (cx, cy)
                boxes[n] = _box(cx, cy, h)
                placed = True
                break
        if not placed:
            # Fallback: keep solver coordinate even if overlapping; the
            # safety-net pass below will attempt to resolve.
            cx = ax if ax is not None else x0.get(n, 0.0)
            cy = ay if ay is not None else y0.get(n, 0.0)
            pos[n] = (cx, cy)
            boxes[n] = _box(cx, cy, h)

    # Safety net: constraint-aware overlap resolution.
    unresolved: list[tuple[str, str]] = []
    for _ in range(200):
        overlapped = False
        pairs = [(a, b) for a in nodes for b in nodes if a < b]
        for a, b in pairs:
            if a not in boxes or b not in boxes:
                continue
            if not _overlaps(boxes[a], boxes[b], margin=20):
                continue
            overlapped = True
            resolved = False
            for mover, other in ((a, b), (b, a)):
                if mover in constrained_y:
                    continue
                bx, by, bw, bh = boxes[other]
                h_m = heights.get(mover, MIN_H)
                up_y = by - h_m - Y_GAP
                down_y = by + bh + Y_GAP
                cur = pos[mover][1]
                target_y = up_y if abs(up_y - cur) <= abs(down_y - cur) else down_y
                if mover < other and abs(up_y - cur) == abs(down_y - cur):
                    target_y = up_y
                if try_place(mover, pos[mover][0], target_y):
                    pos[mover] = (pos[mover][0], target_y)
                    boxes[mover] = _box(pos[mover][0], target_y, h_m)
                    resolved = True
                    break
            if resolved:
                continue
            for mover, other in ((a, b), (b, a)):
                if mover in constrained_x:
                    continue
                bx, by, bw, bh = boxes[other]
                h_m = heights.get(mover, MIN_H)
                left_x = bx - NODE_W - X_GAP
                right_x = bx + bw + X_GAP
                cur = pos[mover][0]
                target_x = left_x if abs(left_x - cur) <= abs(right_x - cur) else right_x
                if mover < other and abs(left_x - cur) == abs(right_x - cur):
                    target_x = left_x
                if try_place(mover, target_x, pos[mover][1]):
                    pos[mover] = (target_x, pos[mover][1])
                    boxes[mover] = _box(target_x, pos[mover][1], h_m)
                    resolved = True
                    break
            if not resolved:
                unresolved.append((a, b))
        if not overlapped:
            break

    # Normalise to positive canvas with margins.
    min_x = min(p[0] for p in pos.values())
    min_y = min(p[1] for p in pos.values())
    pos = {n: (x - min_x + 80, y - min_y + 170) for n, (x, y) in pos.items()}
    boxes = {n: (b[0] - min_x + 80, b[1] - min_y + 170, b[2], b[3]) for n, b in boxes.items()}

    max_x = max(b[0] + b[2] for b in boxes.values())
    max_y = max(b[1] + b[3] for b in boxes.values())

    return {
        "positions": pos,
        "boxes": boxes,
        "heights": dict(heights),
        "width": int(max_x + 80),
        "height": int(max_y + 80),
        "internal_edges": internal_edges,
        "constraints": {
            "x": len(x_cons),
            "y": len(y_cons),
            "dropped": dropped,
        },
        "unresolved_overlaps": unresolved,
    }
