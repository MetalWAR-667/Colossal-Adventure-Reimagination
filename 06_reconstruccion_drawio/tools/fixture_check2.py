#!/usr/bin/env python3
"""Inspect EDGE_GOOD group content: line + arrowhead geometry."""
import re
from pathlib import Path

svg = Path("output/pilot/_fixture.svg").read_text(encoding="utf-8")
start = svg.find('data-cell-id="EDGE_GOOD"')
end = svg.find('data-cell-id="2"')
chunk = svg[start:end]
print("EDGE_GOOD group length:", len(chunk))
# strip base64 blobs for readability
chunk_clean = re.sub(r"data:image/png;base64,[A-Za-z0-9+/=]+", "<B64>", chunk)
print(chunk_clean[:3000])
