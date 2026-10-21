#!/usr/bin/env python3
"""Mission 004 final validation battery."""
from __future__ import annotations

import collections
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from oa_layout import _node_edges_for_chapter
from oa_pilot import evaluate_constraints_v3
from oa_pilot_v2 import build_room_display, estimate_room_height, generate_v2, layout_v2, validate_v2

root = Path(__file__).resolve().parent.parent
with (root / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
    graph = json.load(f)

out = root / "output" / "pilot" / "CH_ENTRY_MataHari_V2.drawio"

# 1. Regenerate for determinism check.
orig = out.read_bytes()
tmp = out.with_suffix(".tmp.drawio")
generate_v2(graph, tmp)
regen = tmp.read_bytes()
tmp.unlink()
det = orig == regen
print("determinism:", det, hashlib.sha256(orig).hexdigest()[:16])

# 2. Directional constraints on the FINAL positions (corrected classifier,
#    identical definitions to Mission 003).
display = build_room_display(graph, "CH_ENTRY")
heights = {
    n: estimate_room_height(d["heading"], d["body"], d["exit_lines"])
    for n, d in display.items()
}
lay = layout_v2(graph, heights)
members, internal_edges = _node_edges_for_chapter(graph, "CH_ENTRY")
ev = evaluate_constraints_v3(internal_edges, lay["positions"])
print(f"directional constraints: {ev['satisfied']}/{ev['satisfied'] + ev['violated']}")
for v in ev["violations"]:
    print("  VIOLATION:", v)
print("dropped (proven contradictory):", len(lay["dropped_constraints"]))

# Also verify secondary UPWAR/DOWN slope between LOC_AWKWARD and LOC_DEBRIS:
awk_x, awk_y = lay["positions"]["LOC_AWKWARD"]
deb_x, deb_y = lay["positions"]["LOC_DEBRIS"]
print(
    f"canyon slope AWKWARD->DEBRIS (DOWN, EAST): dx={deb_x - awk_x:+.0f}, dy={deb_y - awk_y:+.0f} "
    f"({'PASS' if deb_x > awk_x and deb_y > awk_y else 'FAIL'})"
)

# 3. Structural validation.
print(json.dumps(validate_v2(graph, out), indent=2, ensure_ascii=False))

# 4. PNG sanity.
img = Image.open(root / "output" / "pilot" / "CH_ENTRY_MataHari_V2.png")
print("png:", img.format, img.size, img.mode)
small = img.convert("RGB").resize((img.width // 10, img.height // 10))
colors = collections.Counter(
    small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata()
)
non_white = sum(c for rgb, c in colors.items() if rgb != (255, 255, 255))
print("png non-white share: {:.1%}".format(non_white / (small.width * small.height)))

# 5. Prior deliverables untouched.
for f in [
    "Open_Adventure.yaml",
    "output/Open_Adventure_World.drawio",
    "output/Open_Adventure_World_V2.drawio",
    "output/open_adventure_graph.json",
    "output/pilot/CH_ENTRY_MataHari.drawio",
    "output/pilot/CH_ENTRY_MataHari.png",
]:
    p = root / f
    print(f"  {f}: {hashlib.sha256(p.read_bytes()).hexdigest()[:16]}")
