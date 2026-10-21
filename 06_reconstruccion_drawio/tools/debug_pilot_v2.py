#!/usr/bin/env python3
"""Dump V2 pilot positions and dimensions for composition review."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oa_pilot_v2 import build_external_markers, build_room_display, estimate_room_height, layout_v2

root = Path(__file__).resolve().parent.parent
with (root / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
    graph = json.load(f)

display = build_room_display(graph, "CH_ENTRY")
heights = {
    n: estimate_room_height(d["heading"], d["body"], d["exit_lines"])
    for n, d in display.items()
}
lay = layout_v2(graph, heights)
markers = build_external_markers(graph, lay["positions"], heights)

print("room positions (x, y, w=290, h):")
for n in sorted(lay["positions"]):
    x, y = lay["positions"][n]
    print(f"  {n:18s} x={x:6.0f} y={y:6.0f} h={heights[n]:4d}")

print(f"\nlocal reference markers ({len(markers)}):")
for m in markers:
    print(f"  {m['id']:18s} target={m['target']:16s} x={m['x']:6.0f} y={m['y']:6.0f} w={m['w']:4.0f} h={m['h']:3.0f}")
print("dropped constraints:", len(lay["dropped_constraints"]))
