#!/usr/bin/env python3
"""Phase E — rigorous rendered-geometry validation of the V2 SVG.

Parses the ACTUAL connector paths draw.io rendered (`C0..C18` internal
connectors + `X1..X10` external marker connectors), maps them back through
the crop offset, and tests them against room and marker box interiors.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
svg = (root_dir / "output/pilot/CH_ENTRY_MataHari_V2.svg").read_text(encoding="utf-8")

tree = ET.parse(root_dir / "output/pilot/CH_ENTRY_MataHari_V2.drawio")
droot = tree.getroot().find("diagram/mxGraphModel/root")
boxes: dict[str, tuple[float, float, float, float]] = {}
for o in droot.iter("object"):
    oid = o.get("id")
    cell = o.find("mxCell")
    if cell is None or cell.get("vertex") != "1":
        continue
    gm = cell.find("mxGeometry")
    if gm is None:
        continue
    boxes[oid] = (
        float(gm.get("x")),
        float(gm.get("y")),
        float(gm.get("width")),
        float(gm.get("height")),
    )


def _seg_hits_rect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    rect: tuple[float, float, float, float],
    shrink: float = 3.0,
) -> bool:
    (x1, y1), (x2, y2) = p1, p2
    bx, by, bw, bh = rect
    bx += shrink
    by += shrink
    bw -= 2.0 * shrink
    bh -= 2.0 * shrink
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx), (dx, bx + bw - x1), (-dy, y1 - by), (dy, by + bh - y1)):
        if abs(p) < 1e-9:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                if r > t0:
                    t0 = r
            else:
                if r < t0:
                    return False
                if r < t1:
                    t1 = r
    return True


def find_rendered_rect(cid: str):
    m = re.search(
        r'data-cell-id="%s".{0,2000}?<rect x="([0-9.]+)" y="([0-9.]+)" width="([0-9.]+)" height="([0-9.]+)"'
        % re.escape(cid),
        svg,
        re.S,
    )
    if m:
        return tuple(float(v) for v in m.groups())
    return None


ref = find_rendered_rect("N_LOC_CRACK")
if ref is None:
    print("FATAL: reference rect not found")
    sys.exit(1)
fx, fy, fw, fh = boxes["N_LOC_CRACK"]
ox, oy = fx - ref[0], fy - ref[1]
print(f"crop offset derived from N_LOC_CRACK: ({ox}, {oy})")


def group_of(cid: str) -> str:
    start = svg.find(f'data-cell-id="{cid}"')
    nxt = svg.find('data-cell-id="', start + 20)
    return svg[start : nxt if nxt != -1 else len(svg)]


all_cell_ids = re.findall(r'data-cell-id="([^"]+)"', svg)
int_conn_ids = [i for i in all_cell_ids if re.fullmatch(r"C\d+", i)]
ext_conn_ids = [i for i in all_cell_ids if re.fullmatch(r"X\d+", i)]
print(f"internal connectors in SVG: {len(int_conn_ids)}/19")
print(f"external marker connectors in SVG: {len(ext_conn_ids)}/10")

obstacle_ids = [c for c in boxes if c.startswith("N_LOC") or c.startswith("M_LOC")]

total_segments = 0
total_intersections = 0
report = []
arrow_counts = {}

for cid in sorted(int_conn_ids, key=lambda x: int(x[1:])) + sorted(
    ext_conn_ids, key=lambda x: int(x[1:])
):
    g = group_of(cid)
    lines = re.findall(
        r'<path d="([^"]+)" fill="none" stroke="([^"]+)" stroke-width="([0-9.]+)"', g
    )
    segs = []
    for d, col, w in lines:
        pts = re.findall(r"([ML]) ([0-9.]+) ([0-9.]+)", d)
        coords = [(float(x) + ox, float(y) + oy) for _, x, y in pts]
        for i in range(len(coords) - 1):
            segs.append((coords[i], coords[i + 1]))
    total_segments += len(segs)
    tris = re.findall(r'<path d="(M [^"]*Z)" fill="(#[0-9A-Fa-f]{6})"', g)
    arrow_counts[cid] = len(tris)

    conn = next(o for o in droot.iter("object") if o.get("id") == cid)
    cell = conn.find("mxCell")
    src, tgt = cell.get("source"), cell.get("target")
    hits = 0
    for seg in segs:
        for bid in obstacle_ids:
            if bid in (src, tgt):
                continue
            if _seg_hits_rect(seg[0], seg[1], boxes[bid], shrink=3.0):
                hits += 1
                report.append((cid, bid, seg))
                break
    total_intersections += hits

print(f"total rendered line segments: {total_segments}")
print(f"segments intersecting foreign box interiors: {total_intersections}")
for cid, bid, seg in report[:15]:
    print(f"  {cid} crosses {bid}: {seg}")

int_pairs = [c for c in int_conn_ids if arrow_counts[c] >= 2]
int_singles = [c for c in int_conn_ids if arrow_counts[c] == 1]
ext_singles = [c for c in ext_conn_ids if arrow_counts[c] == 1]
zero_arrows = [c for c, n in arrow_counts.items() if n == 0]
print(f"internal bidirectional connectors (2 arrowheads): {len(int_pairs)}/13")
print(f"internal unidirectional connectors (1 arrowhead): {len(int_singles)}/6")
print(f"external marker connectors (1 arrowhead): {len(ext_singles)}/10")
print(f"connectors with 0 arrowheads: {len(zero_arrows)} {zero_arrows}")

colors = re.findall(r'<path d="[^"]+" fill="none" stroke="(#[0-9A-Fa-f]{6})"', svg)
print("stroke colors used:", Counter(colors).most_common())
