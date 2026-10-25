"""Compile only the original CAR-ART-001 C/START study, never production art.
This is a bounded authoring conversion (M/L/H/V/Q/Z), not an SVG importer.
Python standard library; quadratic subdivision error <= 0.25 canvas pixels.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "project_state/changes/car_art_001_vector_direction_gate/studies/build_studies.py"


def paths(text):
    tokens = re.findall(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", text)
    i, current, subpaths, points = 0, (0., 0.), [], []
    while i < len(tokens):
        command = tokens[i]
        i += 1
        relative = command.islower()
        op = command.upper()
        if op not in "MLHVQZ":
            raise ValueError(f"Unsupported study command: {command}")
        count = {"M": 2, "L": 2, "H": 1, "V": 1, "Q": 4, "Z": 0}[op]
        values = list(map(float, tokens[i:i + count]))
        i += count
        def point(x, y):
            return (x + current[0], y + current[1]) if relative else (x, y)
        if op == "Z":
            if points[-1] != points[0]:
                points.append(points[0])
            current = points[0]
        elif op in ("M", "L"):
            end = point(*values)
            if op == "M":
                if points:
                    subpaths.append(points)
                points = []
            points.append(end)
            current = end
        elif op in ("H", "V"):
            end = point(values[0], 0) if op == "H" and relative else (values[0], current[1]) if op == "H" else point(0, values[0]) if relative else (current[0], values[0])
            points.append(end)
            current = end
        elif op == "Q":
            control, end = point(*values[:2]), point(*values[2:])
            def flatten(a, b, c):
                # Quadratic midpoint deviation from chord bounds flatness.
                deviation = math.hypot(a[0] - 2*b[0] + c[0], a[1] - 2*b[1] + c[1]) / 4
                if deviation <= .25:
                    points.append(c)
                else:
                    ab = tuple((a[k] + b[k])/2 for k in (0, 1))
                    bc = tuple((b[k] + c[k])/2 for k in (0, 1))
                    mid = tuple((ab[k] + bc[k])/2 for k in (0, 1))
                    flatten(a, ab, mid)
                    flatten(mid, bc, c)
            flatten(current, control, end)
            current = end
    if points:
        subpaths.append(points)
    return [[[round(x, 5), round(y, 5)] for x, y in p] for p in subpaths]


def interior(poly):
    cells = []
    for y in range(400):
        crossings = []
        for a, b in zip(poly, poly[1:]):
            if (a[1] > y+.5) != (b[1] > y+.5):
                crossings.append(a[0] + (y+.5-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        crossings.sort()
        assert len(crossings) % 2 == 0
        for left, right in zip(crossings[::2], crossings[1::2]):
            cells.extend(y*640+x for x in range(max(0, math.ceil(left-.5)), min(640, math.ceil(right-.5))))
    return cells


def build():
    spec = importlib.util.spec_from_file_location("car_art_study", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    drawing = module.start("C")
    regions = []
    for index, (path, color, seed) in enumerate(drawing.fills):
        polygon, = paths(path)
        assert polygon[0] == polygon[-1]
        cells = interior(polygon)
        # Original conceptual seeds may be on boundaries/outside. Choose the
        # nearest actual interior cell explicitly; keep the source seed too.
        cell = min(cells, key=lambda n: ((n % 640 + .5-seed[0])**2 + (n//640 + .5-seed[1])**2, n))
        mask_bytes = b"".join(struct.pack("<i", n) for n in cells)
        regions.append(dict(id=f"region_{index:02}", polygon=polygon, color=color,
                            source_seed=seed, seed=[cell % 640, cell//640],
                            raster_area=len(cells), mask_sha256=hashlib.sha256(mask_bytes).hexdigest()))
    lines = []
    for path, phase in drawing.strokes:
        for polyline in paths(path):
            if len(polyline) > 1:
                lines.append(dict(points=polyline, phase=phase, width=1.35 if phase == "detail" else 2.6))
    data = dict(format="CAR-ART-002-experimental-v1", room="LOC_START", grid=[640, 400],
                provenance="Original C / Línea solar START study; experimental, not a final asset.",
                source_sha256_lf=hashlib.sha256(SOURCE.read_text(encoding="utf-8").encode("utf-8")).hexdigest(),
                background=drawing.p["paper"], ink=drawing.p["ink"],
                seconds=dict(contour=1.4, detail=.7, fill=1.4), lines=lines, regions=regions)
    (HERE / "loc_start.json").write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"C / START: {len(lines)} polylines, {len(regions)} closed regions, {sum(r['raster_area'] for r in regions)} region cells")


if __name__ == "__main__":
    build()
