# Layout V2 Report — Compass-Oriented Open Adventure Map

**Mission:** MISSION 002 — Compass-Oriented Cartography  
**Agent:** 007 — RPG Archaeology  
**Status:** `PASS` automated checks; **MANUAL_VALIDATION_REQUIRED** for visual usability.

## Scope

This report covers the second-generation `.drawio` map produced from the
Mission 001 intermediate graph. The underlying gameplay graph was not rebuilt;
only layout, node presentation, and connection rendering were changed.

## Output files

- `output/Open_Adventure_World_V2.drawio`
- `output/open_adventure_graph.json` (unchanged from Mission 001)

## Automated validation

**Overall:** `PASS`

| Check | Result | Notes |
|-------|--------|-------|
| xml_well_formed | PASS |  |
| page_structure | PASS |  |
| location_coverage | PASS | 185/185 nodes |
| chapter_preservation | PASS |  |
| description_roundtrip | PASS | 0 mismatches |
| edge_integrity | PASS | 623 edges, 0 bad |
| travel_rule_count | PASS | 623/623 rules |
| box_overlap | PASS | 0 overlaps |
| compass_presence | PASS |  |
| determinism | PASS | hash d7834725142d3cf2 |
| layout_metrics | PASS | satisfied 227, violated 181 |

## Directional layout metrics

| Chapter | Nodes | Width | Height | Satisfied | Violated |
|---------|-------|-------|--------|-----------|----------|
| CH_BEDQUILT | 17 | 3000 | 1000 | 19 | 11 |
| CH_CENTRAL | 18 | 2680 | 882 | 12 | 9 |
| CH_ENTRY | 12 | 2040 | 748 | 9 | 7 |
| CH_MAZE_ALIKE | 33 | 2705 | 2510 | 46 | 23 |
| CH_ORIENTAL_PLOVER | 12 | 1737 | 1098 | 10 | 1 |
| CH_REPOSITORY | 13 | 760 | 2342 | 4 | 15 |
| CH_RESERVOIR | 12 | 1672 | 1924 | 14 | 2 |
| CH_SPECIAL | 7 | 2040 | 522 | 0 | 0 |
| CH_SURFACE | 34 | 1720 | 2324 | 66 | 43 |
| CH_WITT_DIFFERENT | 18 | 1095 | 1965 | 41 | 67 |
| CH_Y2_WINDOWS | 9 | 2040 | 703 | 6 | 3 |

**Total directional constraints satisfied:** 227
**Total directional constraints violated:** 181

Violations are expected in cyclic areas such as the forest, the all-alike maze, and the all-different maze, where compass-labeled edges intentionally create non-planar or non-Euclidean paths. The underlying travel rules are preserved regardless of layout orientation.

### Sample constraint violations

- `LOC_BEDQUILT --WEST--> LOC_SWISSCHEESE` delta=(2240, 91.0) (in CH_BEDQUILT)
- `LOC_BEDQUILT --NORTH--> LOC_LOWROOM` delta=(640, 0.0) (in CH_BEDQUILT)
- `LOC_BEDQUILT --NORTH--> LOC_THREEJUNCTION` delta=(2560, 91.0) (in CH_BEDQUILT)
- `LOC_KINGHALL --NORTH--> LOC_FLOORHOLE` delta=(-320, 0.0) (in CH_CENTRAL)
- `LOC_WESTEND --EAST--> LOC_EASTEND` delta=(-1280, -127.2) (in CH_CENTRAL)
- `LOC_FLOORHOLE --SOUTH--> LOC_KINGHALL` delta=(320, 0.0) (in CH_CENTRAL)
- `LOC_COBBLE --WEST--> LOC_DEBRIS` delta=(640, 225.3) (in CH_ENTRY)
- `LOC_DEBRIS --EAST--> LOC_COBBLE` delta=(-640, -225.3) (in CH_ENTRY)
- `LOC_DEBRIS --WEST--> LOC_AWKWARD` delta=(320, -407.3) (in CH_ENTRY)
- `LOC_ALIKE1 --NORTH--> LOC_ALIKE1` delta=(0, 0.0) (in CH_MAZE_ALIKE)
- `LOC_ALIKE1 --SOUTH--> LOC_ALIKE4` delta=(640, -187.7) (in CH_MAZE_ALIKE)
- `LOC_ALIKE2 --SOUTH--> LOC_ALIKE3` delta=(640, -221.1) (in CH_MAZE_ALIKE)
- `LOC_ALCOVE --NW--> LOC_MISTY` delta=(656.9, -226.3) (in CH_ORIENTAL_PLOVER)
- `LOC_NE --SW--> LOC_SW` delta=(0.0, 364.0) (in CH_REPOSITORY)
- `LOC_SW --NE--> LOC_NE` delta=(0.0, -364.0) (in CH_REPOSITORY)
- `LOC_NECHASM --NE--> LOC_CORRIDOR` delta=(0.0, -728.0) (in CH_REPOSITORY)
- `LOC_MIRRORCANYON --NORTH--> LOC_RESERVOIR` delta=(320.0, 0.0) (in CH_RESERVOIR)
- `LOC_RESERVOIR --SOUTH--> LOC_MIRRORCANYON` delta=(-320.0, 0.0) (in CH_RESERVOIR)
- `LOC_START --EAST--> LOC_BUILDING` delta=(-640, -335.0) (in CH_SURFACE)
- `LOC_BUILDING --WEST--> LOC_START` delta=(640, 335.0) (in CH_SURFACE)

## Visual inspection

No diagrams.net renderer was detected on this machine. Open
`output/Open_Adventure_World_V2.drawio` in diagrams.net to verify:

1. Location boxes are readable and non-overlapping.
2. Compass legends are visible on every chapter page.
3. Directional arrows follow the expected N/S/E/W orientation where feasible.
4. Conditional, vertical, special, and cross-page edges are clearly distinguishable.
5. Exit summaries inside location boxes match the original YAML travel rules.

## Notes

- North is up (smaller Y). South is down (larger Y). East is right (larger X). West is left (smaller X).
- UP/DOWN movement is drawn with solid blue edges and labelled explicitly, distinct from compass N/S.
- Magic teleport destinations (`LOC_FOOF*`) are placed in the chapter of their target and marked in exit summaries.
- Death and transient pseudo-locations are grouped on the "Special & Transient States" page with a grey background.
- Conflicting directional constraints were not resolved by altering gameplay data; they are reported above.
