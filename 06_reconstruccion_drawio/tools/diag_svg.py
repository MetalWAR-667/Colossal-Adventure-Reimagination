#!/usr/bin/env python3
"""Phase A diagnostic — inspect SVG export for connector geometry."""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/pilot/_diag_CH_ENTRY.svg")
svg = path.read_text(encoding="utf-8")
print("file:", path, "length:", len(svg))

paths = re.findall(r"<path[^>]*>", svg)
print("total <path> elements:", len(paths))

stroked = [p for p in paths if re.search(r"stroke:[^;\"']", p)]
print("paths with a stroke style:", len(stroked))

ids = re.findall(r'data-cell-id="([^"]+)"', svg)
print("data-cell-id count:", len(ids), "sample:", ids[:8])
edge_ids = [i for i in ids if i.startswith("ie") or i.startswith("xe")]
print("edge cell ids present:", len(edge_ids), edge_ids[:10])

markers = re.findall(r"marker-(?:end|start)(?:=|:)\"?url", svg)
print("marker refs:", len(markers))

# stroke widths distribution
widths = re.findall(r"stroke-width[:=]\s*\"?([0-9.]+)", svg)
from collections import Counter
print("stroke-width distribution:", Counter(widths).most_common(10))

for p in paths[:4]:
    print("SAMPLE:", p[:280])
