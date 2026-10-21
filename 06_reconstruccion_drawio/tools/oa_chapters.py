#!/usr/bin/env python3
"""
Editorial chapter assignment for Open Adventure locations.

This module implements a deterministic, reproducible partitioning of the
world graph into human-navigable chapters.  Chapter membership is an
editorial interpretation and is explicitly marked as such in all output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from oa_graph import build_graph, parse_open_adventure


CHAPTERS: dict[str, dict[str, Any]] = {
    "CH_SURFACE": {
        "title": "01 — Surface World",
        "description": "Above ground: building, road, hill, valley, forest, grate, and ledge.",
    },
    "CH_ENTRY": {
        "title": "02 — Cave Entry",
        "description": "First chambers beneath the grate up to the Hall of Mists.",
    },
    "CH_CENTRAL": {
        "title": "03 — Hall of Mountain King & Twopit",
        "description": "Central cave complex, Mountain King hall, Twopit Room, Giant Room, and waterfall.",
    },
    "CH_MAZE_ALIKE": {
        "title": "04 — Maze (All Alike)",
        "description": "The classic maze of twisty little passages, all alike.",
    },
    "CH_BEDQUILT": {
        "title": "05 — Bedquilt & Secret Canyons",
        "description": "Bedquilt, Swiss Cheese Room, Slab Room, and the secret canyons above.",
    },
    "CH_ORIENTAL_PLOVER": {
        "title": "06 — Oriental Room & Plover Passage",
        "description": "Soft Room, Oriental Room, misty cavern, alcove, Plover Room, and dark-room.",
    },
    "CH_RESERVOIR": {
        "title": "07 — Reservoir & Cliff Ascent",
        "description": "Underground reservoir, mirror canyon, and the treacherous cliff climb.",
    },
    "CH_REPOSITORY": {
        "title": "08 — Repository & Volcano",
        "description": "Dwarvish repository, chasm, volcano overlook, and barren room.",
    },
    "CH_WITT_DIFFERENT": {
        "title": "09 — Witt's End & Maze All-Different",
        "description": "Construction area, Witt's End, and the maze of twisting passages, all different.",
    },
    "CH_Y2_WINDOWS": {
        "title": "10 — Y2, Windows & Dusty Room",
        "description": "Y2, jumble, window on pit, broken passage, small pit, and dusty rock room.",
    },
    "CH_SPECIAL": {
        "title": "11 — Special & Transient States",
        "description": "Death pseudo-rooms, transient message states, and the null location.",
    },
}

# Explicit pattern-based membership.  Keys are chapter IDs; values are sets of
# location source identifiers.  A location matched here is never overridden by
# fallback rules.
PATTERN_ASSIGNMENTS: dict[str, set[str]] = {
    "CH_SURFACE": {
        "LOC_START", "LOC_HILL", "LOC_BUILDING", "LOC_VALLEY", "LOC_ROADEND",
        "LOC_CLIFF", "LOC_SLIT", "LOC_GRATE", "LOC_LEDGE",
        *{f"LOC_FOREST{i}" for i in range(1, 23)},
        "LOC_SEWER",  # special return to the building
    },
    "CH_ENTRY": {
        "LOC_BELOWGRATE", "LOC_COBBLE", "LOC_DEBRIS", "LOC_AWKWARD",
        "LOC_BIRDCHAMBER", "LOC_PITTOP", "LOC_MISTHALL", "LOC_CRACK",
        "LOC_EASTBANK", "LOC_WESTBANK", "LOC_NUGGET",
        "LOC_FOOF1",  # magic word target: debris room
    },
    "CH_CENTRAL": {
        "LOC_KINGHALL", "LOC_FLOORHOLE", "LOC_SOUTHSIDE", "LOC_WESTSIDE",
        "LOC_CROSSOVER", "LOC_WESTEND", "LOC_EASTEND", "LOC_WESTPIT",
        "LOC_EASTPIT", "LOC_NARROW", "LOC_BUILDING1", "LOC_NOCLIMB",
        "LOC_PLANTTOP", "LOC_CLIMBSTALK", "LOC_GIANTROOM", "LOC_CAVEIN",
        "LOC_IMMENSE", "LOC_WATERFALL",
    },
    "CH_MAZE_ALIKE": {
        *{f"LOC_ALIKE{i}" for i in range(1, 15)},
        *{f"LOC_MAZEEND{i}" for i in range(1, 13)},
        "LOC_PARALLEL1", "LOC_PARALLEL2", "LOC_LONGEAST", "LOC_LONGWEST",
        "LOC_TOPSTALACTITE", "LOC_MISTWEST", "LOC_PITBRINK", "LOC_DEADEND7",
    },
    "CH_BEDQUILT": {
        "LOC_COMPLEX", "LOC_BEDQUILT", "LOC_SWISSCHEESE", "LOC_SLAB",
        "LOC_SECRET1", "LOC_SECRET2", "LOC_THREEJUNCTION", "LOC_LOWROOM",
        "LOC_DEADCRAWL", "LOC_SECRET3", "LOC_WIDEPLACE", "LOC_TIGHTPLACE",
        "LOC_TALL", "LOC_BOULDERS1", "LOC_SECRET4", "LOC_SECRET5", "LOC_SECRET6",
    },
    "CH_ORIENTAL_PLOVER": {
        "LOC_SOFTROOM", "LOC_ORIENTAL", "LOC_MISTY", "LOC_ALCOVE",
        "LOC_PLOVER", "LOC_DARKROOM", "LOC_INCLINE", "LOC_ARCHED",
        "LOC_SHELLROOM", "LOC_SLOPING1", "LOC_CULDESAC",
        "LOC_FOOF5",  # magic word target: Plover Room
    },
    "CH_RESERVOIR": {
        "LOC_RESERVOIR", "LOC_RESBOTTOM", "LOC_RESNORTH", "LOC_TREACHEROUS",
        "LOC_STEEP", "LOC_CLIFFBASE", "LOC_CLIFFACE", "LOC_CLIFFTOP",
        "LOC_CLIFFLEDGE", "LOC_REACHDEAD", "LOC_MIRRORCANYON",
        "LOC_WINDOW2",
    },
    "CH_REPOSITORY": {
        "LOC_NE", "LOC_SW", "LOC_SWCHASM", "LOC_WINDING", "LOC_FORK",
        "LOC_CORRIDOR", "LOC_WARMWALLS", "LOC_BREATHTAKING", "LOC_BOULDERS2",
        "LOC_LIMESTONE", "LOC_BARRENFRONT", "LOC_BARRENROOM", "LOC_NECHASM",
    },
    "CH_WITT_DIFFERENT": {
        "LOC_ANTEROOM", "LOC_WITTSEND",
        *{f"LOC_DIFFERENT{i}" for i in range(1, 12)},
        "LOC_DEADEND13", "LOC_ROUGHHEWN", "LOC_BADDIRECTION",
        "LOC_LARGE", "LOC_STOREROOM",
    },
    "CH_Y2_WINDOWS": {
        "LOC_Y2", "LOC_JUMBLE", "LOC_WINDOW1", "LOC_BROKEN",
        "LOC_SMALLPITBRINK", "LOC_SMALLPIT", "LOC_DUSTY",
        "LOC_FOOF3", "LOC_FOOF6",  # magic word targets: Y2
    },
    "CH_SPECIAL": {
        "LOC_NOWHERE", "LOC_NECKBROKE", "LOC_NOMAKE", "LOC_DOME",
        "LOC_SNAKEBLOCK", "LOC_GRUESOME", "LOC_FOOTSLIP",
    },
}

# Magic-word teleport targets that resolve to a concrete destination are placed
# in the destination's chapter.  Mapping from FOOF id -> destination id.
FOOF_TARGETS: dict[str, str] = {
    "LOC_FOOF1": "LOC_DEBRIS",
    "LOC_FOOF2": "LOC_BUILDING",
    "LOC_FOOF3": "LOC_Y2",
    "LOC_FOOF4": "LOC_BUILDING",
    "LOC_FOOF5": "LOC_PLOVER",
    "LOC_FOOF6": "LOC_Y2",
}


def _build_reverse_lookup(patterns: dict[str, set[str]]) -> dict[str, str]:
    """Build loc_id -> chapter_id lookup from explicit pattern sets."""
    lookup: dict[str, str] = {}
    for chapter_id, loc_ids in patterns.items():
        for loc_id in loc_ids:
            if loc_id in lookup:
                raise ValueError(f"Location {loc_id} assigned to multiple chapters")
            lookup[loc_id] = chapter_id
    return lookup


def assign_chapters(graph: dict[str, Any]) -> dict[str, Any]:
    """Assign every location to a primary chapter and annotate the graph."""
    loc_index = {loc["source_id"]: loc for loc in graph["locations"]}
    lookup = _build_reverse_lookup(PATTERN_ASSIGNMENTS)

    # First pass: explicit patterns.
    unassigned: list[str] = []
    for loc in graph["locations"]:
        loc_id = loc["source_id"]
        if loc_id in lookup:
            loc["chapter_id"] = lookup[loc_id]
        else:
            unassigned.append(loc_id)

    # Second pass: FOOF teleports inherit their destination chapter.
    for foof_id, dest_id in FOOF_TARGETS.items():
        if foof_id in unassigned and dest_id in loc_index:
            loc_index[foof_id]["chapter_id"] = loc_index[dest_id]["chapter_id"]
            unassigned.remove(foof_id)

    # Third pass: any remaining locations fall back to Special chapter with a
    # review flag.  This should normally be empty.
    for loc_id in unassigned:
        loc_index[loc_id]["chapter_id"] = "CH_SPECIAL"
        loc_index[loc_id]["review_status"] = "auto_fallback"

    # Build chapter summaries.
    chapter_members: dict[str, list[str]] = {cid: [] for cid in CHAPTERS}
    for loc in graph["locations"]:
        cid = loc["chapter_id"]
        if cid not in chapter_members:
            chapter_members[cid] = []
        chapter_members[cid].append(loc["source_id"])

    graph["chapters"] = {
        cid: {
            "chapter_id": cid,
            **meta,
            "members": sorted(chapter_members.get(cid, [])),
            "member_count": len(chapter_members.get(cid, [])),
        }
        for cid, meta in CHAPTERS.items()
    }

    graph["chapter_provenance"] = {
        "method": "deterministic rule-based assignment with explicit pattern sets",
        "editorial": True,
        "foof_inheritance": FOOF_TARGETS,
        "unassigned_fallback": "CH_SPECIAL with review_status flag",
    }

    return graph


def chapter_assignment_report(graph: dict[str, Any]) -> str:
    """Produce a Markdown chapter proposal with rationale and membership."""
    lines = [
        "# Chapter Organization Proposal\n",
        "**Status:** Editorial interpretation produced for navigation purposes.\n",
        "**Method:** " + graph["chapter_provenance"]["method"] + "\n",
        "**Total locations assigned:** " + str(len(graph["locations"])) + "\n",
        "## Rationale\n",
        "The chapters below are artificial navigation aids. They were derived from:",
        "1. Natural geographical or thematic boundaries (surface vs. cave, reservoir, volcano).",
        "2. Topological connectivity (maze clusters, secret-canyon networks).",
        "3. Major transitions (grate, Hall of Mists, Y2, chasm).",
        "4. Puzzle dependencies (dragon area, troll bridge, ogre storeroom).",
        "5. Labyrinth organization (all-alike maze vs. all-different maze).",
        "6. Practical readability on a diagrams.net canvas.\n",
        "Magic-word teleport destinations (`LOC_FOOF*`) inherit the chapter of their",
        "target location so the teleport context is visible. Death and transient",
        "pseudo-locations are grouped in a dedicated chapter so they do not clutter",
        "playable region pages.\n",
    ]

    lines.append("## Chapter summary\n")
    lines.append("| Chapter | Locations | Description |")
    lines.append("|---------|-----------|-------------|")
    for cid, ch in graph["chapters"].items():
        lines.append(f"| {ch['title']} | {ch['member_count']} | {ch['description']} |")
    lines.append("")

    for cid, ch in graph["chapters"].items():
        lines.append(f"## {ch['title']}")
        lines.append(f"- **Chapter ID:** `{cid}`")
        lines.append(f"- **Locations:** {ch['member_count']}")
        lines.append(f"- **Description:** {ch['description']}")
        lines.append("- **Members:** " + ", ".join(f"`{m}`" for m in ch["members"]))
        lines.append("")

    lines.append("## Cross-page connections\n")
    lines.append("Connections that cross chapter boundaries are drawn as off-page "
                 "references on each chapter page, with the target chapter noted "
                 "implicitly by the marker's presence at the edge of the page. "
                 "For the complete graph, inspect the JSON export or the source YAML.\n")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    root = Path(__file__).resolve().parent.parent
    ir = parse_open_adventure(root / "Open_Adventure.yaml")
    graph = build_graph(ir)
    graph = assign_chapters(graph)
    print(json.dumps({cid: ch["member_count"] for cid, ch in graph["chapters"].items()}, indent=2))
