#!/usr/bin/env python3
"""Verify fixture SVG: which pattern renders?"""
import re
from pathlib import Path

svg = Path("output/pilot/_fixture.svg").read_text(encoding="utf-8")
ids = re.findall(r'data-cell-id="([^"]+)"', svg)
print("cell ids in SVG:", ids)
print("EDGE_GOOD present:", "EDGE_GOOD" in svg)
print("EDGE_BROKEN present:", "EDGE_BROKEN" in svg)
print("NODE_A present:", "NODE_A" in svg, "| NODE_C present:", "NODE_C" in svg)
paths = re.findall(r"<path[^>]{0,240}>", svg)
print("path elements:", len(paths))
for p in paths:
    print("  PATH:", p[:170])
print("marker-end refs:", len(re.findall(r"marker-end", svg)))
print("marker-start refs:", len(re.findall(r"marker-start", svg)))
