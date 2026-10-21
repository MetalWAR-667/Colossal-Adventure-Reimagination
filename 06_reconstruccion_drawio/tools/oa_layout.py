#!/usr/bin/env python3
"""
Compass-oriented layout engine for Open Adventure draw.io maps.

Deterministically assigns (x, y) coordinates to chapter locations using
directional hints extracted from the original motion vocabulary. Outputs are
editable; the engine reports how many edges satisfy their compass constraint
and how many violate it.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

# Compass direction vectors. North = up = negative Y.
DIRECTION_VECTORS: dict[str, tuple[int, int]] = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST": (1, 0),
    "WEST": (-1, 0),
    "NE": (1, -1),
    "SE": (1, 1),
    "SW": (-1, 1),
    "NW": (-1, -1),
    "UP": (0, -1),
    "DOWN": (0, 1),
}

COMPASS_ORDER = ["NORTH", "SOUTH", "EAST", "WEST", "NE", "SE", "SW", "NW", "UP", "DOWN"]

# Spacing constants (pixels).
BASE_DX = 320
BASE_DY = 220
DIAGONAL_SCALE = 0.85
NODE_WIDTH = 280
NODE_HEIGHT = 140


def _primary_direction(edge: dict[str, Any]) -> str | None:
    """Return the strongest directional hint for an edge, if any."""
    verbs = set(edge.get("verbs", []))
    # Prefer strict compass and vertical verbs in source order.
    for d in COMPASS_ORDER:
        if d in verbs:
            return d
    return None


def _direction_category(d: str | None) -> str:
    if d is None:
        return "semantic"
    if d in ("UP", "DOWN"):
        return "vertical"
    return "compass"


def _layout_vector(d: str) -> tuple[float, float]:
    vx, vy = DIRECTION_VECTORS[d]
    if d in ("NE", "SE", "SW", "NW"):
        return (vx * BASE_DX * DIAGONAL_SCALE, vy * BASE_DY * DIAGONAL_SCALE)
    return (vx * BASE_DX, vy * BASE_DY)


def _node_edges_for_chapter(graph: dict[str, Any], chapter_id: str) -> tuple[set[str], list[dict[str, Any]]]:
    """Return the nodes and internal edges of a single chapter."""
    members = set(graph["chapters"][chapter_id]["members"])
    internal_edges = [
        e for e in graph["edges"]
        if e["source"] in members and e.get("target") in members
    ]
    return members, internal_edges


def _entry_nodes(graph: dict[str, Any], chapter_id: str) -> list[str]:
    """Heuristic entry nodes: those with incoming cross-chapter edges, or lowest in-degree."""
    members = set(graph["chapters"][chapter_id]["members"])
    incoming_cross: set[str] = set()
    incoming_count: dict[str, int] = defaultdict(int)
    for e in graph["edges"]:
        if e.get("target") in members and e["source"] not in members:
            incoming_cross.add(e["target"])
        if e.get("target") in members:
            incoming_count[e["target"]] += 1
    if incoming_cross:
        return sorted(incoming_cross)
    # Fallback: nodes with smallest in-degree (likely starts of sub-graphs).
    return sorted(members, key=lambda n: (incoming_count.get(n, 0), n))[:1]


def _place_nodes_bfs(members: set[str], internal_edges: list[dict[str, Any]],
                     entry_nodes: list[str]) -> dict[str, tuple[float, float]]:
    """Place nodes by BFS using directional offsets."""
    positions: dict[str, tuple[float, float]] = {}

    # Seed entry nodes near the origin, spaced horizontally.
    for i, n in enumerate(entry_nodes):
        positions[n] = (i * BASE_DX, 0.0)

    # Build adjacency list from internal edges.
    adj: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for e in internal_edges:
        adj[e["source"]].append((e["target"], e))

    visited = set(positions.keys())
    queue = list(entry_nodes)
    idx = 0
    while idx < len(queue):
        src = queue[idx]
        idx += 1
        sx, sy = positions[src]
        for tgt, edge in adj[src]:
            d = _primary_direction(edge)
            if tgt not in positions:
                if d:
                    dx, dy = _layout_vector(d)
                    # Slight deterministic jitter for non-compass/vertical to reduce stacking.
                    if _direction_category(d) == "semantic":
                        dx, dy = _semantic_offset(src, tgt, positions)
                    positions[tgt] = (sx + dx, sy + dy)
                else:
                    positions[tgt] = _semantic_position(src, tgt, positions)
                visited.add(tgt)
                queue.append(tgt)
            # If already placed, we will validate the constraint later.

    # Place any isolated nodes that were not reached.
    for n in sorted(members):
        if n not in positions:
            positions[n] = (0.0, 0.0)

    return positions


def _semantic_position(src: str, tgt: str, positions: dict[str, tuple[float, float]]) -> tuple[float, float]:
    """Place a semantically-labelled neighbour to the right of the source."""
    sx, sy = positions[src]
    # Count existing semantic neighbours to fan them out.
    count = sum(1 for k, v in positions.items() if v[0] > sx + BASE_DX * 0.7 and abs(v[1] - sy) < BASE_DY * 0.5)
    return (sx + BASE_DX, sy + (count % 3 - 1) * BASE_DY * 0.6)


def _semantic_offset(src: str, tgt: str, positions: dict[str, tuple[float, float]]) -> tuple[float, float]:
    """Deterministic offset for edges classified as semantic."""
    return _semantic_position(src, tgt, positions)


def _remove_overlaps(positions: dict[str, tuple[float, float]],
                     members: set[str]) -> dict[str, tuple[float, float]]:
    """Iteratively push apart overlapping node boxes."""
    # Ensure deterministic order.
    nodes = sorted(members)
    pos = {n: list(positions.get(n, (0.0, 0.0))) for n in nodes}

    box_w = NODE_WIDTH + 40
    box_h = NODE_HEIGHT + 40

    for _ in range(200):
        moved = False
        for i, a in enumerate(nodes):
            ax, ay = pos[a]
            for b in nodes[i + 1:]:
                bx, by = pos[b]
                dx = bx - ax
                dy = by - ay
                adx = abs(dx)
                ady = abs(dy)
                if adx < box_w and ady < box_h:
                    # Overlap: push apart along the smallest overlap axis.
                    push_x = box_w - adx
                    push_y = box_h - ady
                    if push_x < push_y:
                        step = push_x / 2 + 1
                        sx = 1 if dx >= 0 else -1
                        pos[a][0] -= step * sx
                        pos[b][0] += step * sx
                    else:
                        step = push_y / 2 + 1
                        sy = 1 if dy >= 0 else -1
                        pos[a][1] -= step * sy
                        pos[b][1] += step * sy
                    moved = True
        if not moved:
            break

    return {n: (pos[n][0], pos[n][1]) for n in nodes}


def _normalize_to_origin(positions: dict[str, tuple[float, float]],
                         margin_x: float, margin_y: float) -> dict[str, tuple[float, float]]:
    """Shift all coordinates so the bounding box starts at (margin_x, margin_y)."""
    if not positions:
        return positions
    min_x = min(p[0] for p in positions.values())
    min_y = min(p[1] for p in positions.values())
    return {n: (x - min_x + margin_x, y - min_y + margin_y) for n, (x, y) in positions.items()}


def _evaluate_constraints(internal_edges: list[dict[str, Any]],
                          positions: dict[str, tuple[float, float]]) -> dict[str, Any]:
    """Count how many compass/vertical edges satisfy their directional constraint."""
    satisfied = 0
    violated = 0
    violations: list[dict[str, Any]] = []
    for e in internal_edges:
        d = _primary_direction(e)
        if not d or d not in DIRECTION_VECTORS:
            continue
        src = e["source"]
        tgt = e["target"]
        sx, sy = positions[src]
        tx, ty = positions[tgt]
        dx = tx - sx
        dy = ty - sy
        ok = False
        if d in ("NORTH", "UP"):
            ok = dy < -1
        elif d in ("SOUTH", "DOWN"):
            ok = dy > 1
        elif d == "EAST":
            ok = dx > 1
        elif d == "WEST":
            ok = dx < -1
        elif d == "NE":
            ok = dx > 1 and dy < -1
        elif d == "SE":
            ok = dx > 1 and dy > 1
        elif d == "SW":
            ok = dx < -1 and dy > 1
        elif d == "NW":
            ok = dx < -1 and dy < -1
        if ok:
            satisfied += 1
        else:
            violated += 1
            violations.append({
                "source": src,
                "target": tgt,
                "direction": d,
                "delta": (round(dx, 1), round(dy, 1)),
            })
    return {
        "satisfied": satisfied,
        "violated": violated,
        "violations": violations[:50],
    }


def layout_chapter(graph: dict[str, Any], chapter_id: str) -> dict[str, Any]:
    """Run the full layout procedure for one chapter and return positions + metrics."""
    members, internal_edges = _node_edges_for_chapter(graph, chapter_id)
    entry_nodes = _entry_nodes(graph, chapter_id)
    positions = _place_nodes_bfs(members, internal_edges, entry_nodes)
    positions = _remove_overlaps(positions, members)
    positions = _normalize_to_origin(positions, 80, 120)
    constraints = _evaluate_constraints(internal_edges, positions)

    # Compute bounding box.
    if positions:
        max_x = max(p[0] for p in positions.values()) + NODE_WIDTH
        max_y = max(p[1] for p in positions.values()) + NODE_HEIGHT
    else:
        max_x, max_y = 800, 600

    return {
        "chapter_id": chapter_id,
        "positions": positions,
        "width": math.ceil(max_x + 80),
        "height": math.ceil(max_y + 80),
        "internal_edges": len(internal_edges),
        "entry_nodes": entry_nodes,
        "constraint_evaluation": constraints,
    }


def layout_all_chapters(graph: dict[str, Any]) -> dict[str, Any]:
    """Compute a compass-oriented layout for every chapter."""
    result: dict[str, Any] = {"chapters": {}}
    total_satisfied = 0
    total_violated = 0
    for chapter_id in graph["chapters"].keys():
        layout = layout_chapter(graph, chapter_id)
        result["chapters"][chapter_id] = layout
        total_satisfied += layout["constraint_evaluation"]["satisfied"]
        total_violated += layout["constraint_evaluation"]["violated"]
    result["summary"] = {
        "total_chapters": len(result["chapters"]),
        "total_satisfied": total_satisfied,
        "total_violated": total_violated,
    }
    return result
