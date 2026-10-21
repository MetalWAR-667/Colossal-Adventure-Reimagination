#!/usr/bin/env python3
"""Debug helper: print pilot positions and comparison metrics."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oa_pilot as P

root = Path(__file__).resolve().parent.parent
with (root / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
    graph = json.load(f)

out = root / "output" / "pilot" / "CH_ENTRY_MataHari.drawio"
pilot = P.generate_pilot(graph, out)
lay = pilot["layout"]

print("PILOT POSITIONS (x, y, height):")
for n in sorted(lay["positions"]):
    x, y = lay["positions"][n]
    h = pilot["heights"][n]
    print(f"  {n:18s} x={x:7.0f} y={y:7.0f} h={h}")

print()
comp = P.compare(graph, pilot)
b = comp["baseline_v2"]
p = comp["pilot"]
print(f"baseline: satisfied={b['satisfied']}/{b['applicable_constraints']} "
      f"box_hits={b['edge_box_intersections']} crossings={b['edge_crossings']} "
      f"overlaps={b['box_overlaps']} size={b['width']}x{b['height']}")
print(f"pilot:    satisfied={p['satisfied']}/{p['applicable_constraints']} "
      f"box_hits={p['edge_box_intersections']} crossings={p['edge_crossings']} "
      f"overlaps={p['box_overlaps']} size={p['width']}x{p['height']}")
