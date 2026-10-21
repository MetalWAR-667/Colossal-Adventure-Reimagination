#!/usr/bin/env python3
"""Phase A diagnostic 2 — enumerate all data-cell-ids and locate edge structures."""
import re
from pathlib import Path

svg = Path("output/pilot/_diag_CH_ENTRY.svg").read_text(encoding="utf-8")

ids = re.findall(r'data-cell-id="([^"]+)"', svg)
print("ALL data-cell-ids (%d):" % len(ids))
print(ids)

print()
ctx = svg.find("ie0")
while ctx != -1 and ctx < len(svg):
    print("--- context around offset", ctx, "---")
    print(svg[max(0, ctx - 200):ctx + 300].replace("\n", " ")[:500])
    nxt = svg.find("ie0", ctx + 1)
    if nxt == ctx:
        break
    ctx = nxt
    if ctx > 4000000:
        break

print()
# How many <g data-cell-id groups contain a rect with stroke (boxes)?
groups = re.findall(r'<g data-cell-id="([^"]+)">(.{0,4000}?)(?=<g data-cell-id=|</g><g data-cell-id=)', svg, re.S)
print("groups found:", len(groups))
for gid, body in groups[:40]:
    has_stroke = "stroke:" in body and "none" not in body[:200]
    print(f"  {gid:30s} len={len(body):6d} stroked-rect={'stroke=' in body}")
