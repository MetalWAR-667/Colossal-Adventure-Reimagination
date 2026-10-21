#!/usr/bin/env python3
"""
Mission 005 — Automated export and SVG/PNG verification across all 12 pages
of `output/Open_Adventure_World_V3.drawio` and `output/pilot/CH_ENTRY_MataHari_V3.drawio`.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from oa_chapters import CHAPTERS
from oa_pilot_v3 import ALIAS_LAYER_ID, validate_pilot_v3, verify_pilot_v3_svg
from oa_world_v3 import validate_world_v3

EXPECTED_PRIOR_SHA256_PREFIXES = {
    "Open_Adventure.yaml": "4ee2c6451a64591b",
    "output/Open_Adventure_World.drawio": "605295e295a1f09a",
    "output/Open_Adventure_World_V2.drawio": "d7834725142d3cf2",
    "output/open_adventure_graph.json": "c6ee8bf9c46638d8",
    "output/pilot/CH_ENTRY_MataHari.drawio": "4fedddcf36ebc700",
    "output/pilot/CH_ENTRY_MataHari.png": "3a5ca1167d99c0b6",
    "output/pilot/CH_ENTRY_MataHari_V2.drawio": "f0c5a1f5a4184e0f",
}


def sha256_prefix(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def export_world_previews(
    world_drawio: Path,
    previews_dir: Path,
    drawio_exe: Path,
) -> list[dict[str, Any]]:
    previews_dir.mkdir(parents=True, exist_ok=True)
    tree = ET.parse(world_drawio)
    diagrams = list(tree.getroot().findall("diagram"))

    pat_stroke = re.compile(
        r'<path d="M [^"]+" fill="none" stroke="([^"]+)"[^>]*stroke-miterlimit="10"'
    )
    results: list[dict[str, Any]] = []

    for page_idx, diag in enumerate(diagrams):
        did = diag.get("id")
        dname = diag.get("name")
        slug = f"{page_idx:02d}_{did}"
        png_path = previews_dir / f"{slug}.png"
        svg_path = previews_dir / f"{slug}.svg"

        mg = diag.find("mxGraphModel")
        pw = int(mg.get("pageWidth", "2000")) if mg is not None else 2000
        ph = int(mg.get("pageHeight", "2000")) if mg is not None else 2000
        png_scale = "1" if max(pw, ph) > 4000 else "2"

        subprocess.run(
            [
                str(drawio_exe), "-x", "-f", "png", "-s", png_scale,
                "-p", str(page_idx + 1), "-o", str(png_path), str(world_drawio),
            ],
            check=True,
        )
        subprocess.run(
            [
                str(drawio_exe), "-x", "-f", "svg", "--embed-svg-fonts", "false",
                "-p", str(page_idx + 1), "-o", str(svg_path), str(world_drawio),
            ],
            check=True,
        )

        root = diag.find("mxGraphModel/root")
        objs = list(root.iter("object"))
        visible_edges = [
            o for o in objs
            if o.find("mxCell") is not None
            and o.find("mxCell").get("edge") == "1"
            and o.find("mxCell").get("parent") == "1"
        ]
        hidden_alias_edges = [
            o for o in objs
            if o.find("mxCell") is not None
            and o.find("mxCell").get("edge") == "1"
            and o.find("mxCell").get("parent") == ALIAS_LAYER_ID
        ]

        svg_text = svg_path.read_text(encoding="utf-8")
        strokes = pat_stroke.findall(svg_text)
        alias_strokes = [c for c in strokes if c.lower() == "#78909c"]

        results.append({
            "page_index": page_idx,
            "diagram_id": did,
            "diagram_name": dname,
            "png": str(png_path.relative_to(world_drawio.parent.parent)),
            "png_bytes": png_path.stat().st_size,
            "svg": str(svg_path.relative_to(world_drawio.parent.parent)),
            "expected_visible_connectors": len(visible_edges),
            "expected_hidden_alias_connectors": len(hidden_alias_edges),
            "rendered_svg_connectors": len(strokes),
            "rendered_alias_strokes_in_default_svg": len(alias_strokes),
            "svg_render_exact_match": (
                len(strokes) == len(visible_edges) and len(alias_strokes) == 0
            ),
        })

    return results


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    drawio_exe = root_dir.parent / "draw.io" / "draw.io.exe"
    with (root_dir / "output" / "open_adventure_graph.json").open(encoding="utf-8") as f:
        graph = json.load(f)

    # 1. Verify prior Mission 001–004 deliverables untouched
    prior_hashes = {}
    all_prior_ok = True
    for rel, exp in EXPECTED_PRIOR_SHA256_PREFIXES.items():
        actual = sha256_prefix(root_dir / rel)
        ok = actual == exp
        if not ok:
            all_prior_ok = False
        prior_hashes[rel] = {"sha256_16": actual, "matches_expected": ok}

    # 2. Export & verify all 12 pages of Open_Adventure_World_V3.drawio
    world_v3 = root_dir / "output" / "Open_Adventure_World_V3.drawio"
    previews_dir = root_dir / "output" / "previews_v3"
    page_exports = export_world_previews(world_v3, previews_dir, drawio_exe)

    # 3. Structural validation
    world_val = validate_world_v3(graph, world_v3)
    pilot_v3 = root_dir / "output" / "pilot" / "CH_ENTRY_MataHari_V3.drawio"
    pilot_val = validate_pilot_v3(graph, pilot_v3)

    summary = {
        "prior_deliverables_untouched": all_prior_ok,
        "prior_hashes": prior_hashes,
        "pilot_v3_sha256_16": sha256_prefix(pilot_v3),
        "world_v3_sha256_16": sha256_prefix(world_v3),
        "pilot_validation": pilot_val,
        "world_validation": {k: v for k, v in world_val.items() if k != "per_chapter"},
        "all_12_pages_svg_render_exact_match": all(
            p["svg_render_exact_match"] for p in page_exports
        ),
        "page_exports": page_exports,
    }
    out_json = root_dir / "output" / "previews_v3" / "verification_summary_v3.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({
        "prior_deliverables_untouched": summary["prior_deliverables_untouched"],
        "pilot_v3_sha256_16": summary["pilot_v3_sha256_16"],
        "world_v3_sha256_16": summary["world_v3_sha256_16"],
        "all_12_pages_svg_render_exact_match": summary["all_12_pages_svg_render_exact_match"],
        "world_validation": summary["world_validation"],
        "pages": [
            {
                "idx": p["page_index"],
                "id": p["diagram_id"],
                "vis_conns": p["rendered_svg_connectors"],
                "hidden_aliases": p["expected_hidden_alias_connectors"],
                "alias_leaked": p["rendered_alias_strokes_in_default_svg"],
                "ok": p["svg_render_exact_match"],
            }
            for p in page_exports
        ],
    }, indent=2))
