#!/usr/bin/env python3
"""Mission 003 Phase A — instrumented trace of the V2 BFS placement for CH_ENTRY."""

import sys
import json
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oa_layout as L

root = Path(__file__).resolve().parent.parent
with (root / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
    g = json.load(f)

members, internal_edges = L._node_edges_for_chapter(g, "CH_ENTRY")
entry = L._entry_nodes(g, "CH_ENTRY")
print("Step 1 - entry nodes (incoming cross-chapter edges):", entry)
print()

positions = {}
for i, n in enumerate(entry):
    positions[n] = (i * L.BASE_DX, 0.0)
    print(f"SEED  {n:18s} at ({i * L.BASE_DX}, 0)   <- flat row, all constraints ignored")

adj = defaultdict(list)
for e in internal_edges:
    adj[e["source"]].append((e["target"], e))

queue = list(entry)
idx = 0
print()
while idx < len(queue):
    src = queue[idx]
    idx += 1
    sx, sy = positions[src]
    for tgt, edge in adj[src]:
        d = L._primary_direction(edge)
        if tgt not in positions:
            if d:
                dx, dy = L._layout_vector(d)
                positions[tgt] = (sx + dx, sy + dy)
                print(f"BFS   {tgt:18s} at ({sx + dx:6.0f},{sy + dy:6.0f})   via {src} --{d}-->")
            else:
                p = L._semantic_position(src, tgt, positions)
                positions[tgt] = p
                lbl = edge["label"][:28]
                print(f"BFS   {tgt:18s} at ({p[0]:6.0f},{p[1]:6.0f})   via {src} --semantic: {lbl}")
            queue.append(tgt)
        else:
            print(f"SKIP  {src} --{d or 'semantic'}--> {tgt}   already placed, constraint IGNORED (first-wins)")

print()
print("Raw BFS positions BEFORE overlap removal:")
for n in sorted(positions):
    print(f"  {n:18s} ({positions[n][0]:7.1f}, {positions[n][1]:7.1f})")

print()
print("Constraint evaluation on raw BFS positions:")
raw_eval = L._evaluate_constraints(internal_edges, positions)
print(f"  satisfied={raw_eval['satisfied']} violated={raw_eval['violated']}")
for v in raw_eval["violations"]:
    print(f"  RAW-VIOLATION {v['source']} --{v['direction']}--> {v['target']} delta={v['delta']}")

# Now show what overlap removal does
after = L._remove_overlaps(positions, members)
print()
print("Movement caused by _remove_overlaps (constraint-blind pushes):")
for n in sorted(after):
    bx, by = positions[n]
    ax, ay = after[n]
    if abs(bx - ax) > 0.5 or abs(by - ay) > 0.5:
        print(f"  {n:18s} ({bx:7.1f},{by:7.1f}) -> ({ax:7.1f},{ay:7.1f})  moved dx={ax-bx:+.1f} dy={ay-by:+.1f}")

final_eval = L._evaluate_constraints(internal_edges, after)
print()
print(f"After overlap removal: satisfied={final_eval['satisfied']} violated={final_eval['violated']}")
