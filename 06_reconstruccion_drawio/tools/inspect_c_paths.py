#!/usr/bin/env python3
"""Inspect actual SVG path strings of all connectors in CH_ENTRY_MataHari_V2.svg."""
import re
from pathlib import Path

svg = Path("output/pilot/CH_ENTRY_MataHari_V2.svg").read_text(encoding="utf-8")
for i in range(20):
    cid = f"C{i}"
    s = svg.find(f'data-cell-id="{cid}"')
    nxt = svg.find('data-cell-id="', s + 20)
    g = svg[s:nxt]
    paths = re.findall(r'<path d="([^"]+)" fill="none"', g)
    print(f"{cid}: {paths}")
