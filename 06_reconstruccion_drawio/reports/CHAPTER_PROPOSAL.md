# Chapter Organization Proposal

**Status:** Editorial interpretation produced for navigation purposes.

**Method:** deterministic rule-based assignment with explicit pattern sets

**Total locations assigned:** 185

## Rationale

The chapters below are artificial navigation aids. They were derived from:
1. Natural geographical or thematic boundaries (surface vs. cave, reservoir, volcano).
2. Topological connectivity (maze clusters, secret-canyon networks).
3. Major transitions (grate, Hall of Mists, Y2, chasm).
4. Puzzle dependencies (dragon area, troll bridge, ogre storeroom).
5. Labyrinth organization (all-alike maze vs. all-different maze).
6. Practical readability on a diagrams.net canvas.

Magic-word teleport destinations (`LOC_FOOF*`) inherit the chapter of their
target location so the teleport context is visible. Death and transient
pseudo-locations are grouped in a dedicated chapter so they do not clutter
playable region pages.

## Chapter summary

| Chapter | Locations | Description |
|---------|-----------|-------------|
| 01 — Surface World | 34 | Above ground: building, road, hill, valley, forest, grate, and ledge. |
| 02 — Cave Entry | 12 | First chambers beneath the grate up to the Hall of Mists. |
| 03 — Hall of Mountain King & Twopit | 18 | Central cave complex, Mountain King hall, Twopit Room, Giant Room, and waterfall. |
| 04 — Maze (All Alike) | 33 | The classic maze of twisty little passages, all alike. |
| 05 — Bedquilt & Secret Canyons | 17 | Bedquilt, Swiss Cheese Room, Slab Room, and the secret canyons above. |
| 06 — Oriental Room & Plover Passage | 12 | Soft Room, Oriental Room, misty cavern, alcove, Plover Room, and dark-room. |
| 07 — Reservoir & Cliff Ascent | 12 | Underground reservoir, mirror canyon, and the treacherous cliff climb. |
| 08 — Repository & Volcano | 13 | Dwarvish repository, chasm, volcano overlook, and barren room. |
| 09 — Witt's End & Maze All-Different | 18 | Construction area, Witt's End, and the maze of twisting passages, all different. |
| 10 — Y2, Windows & Dusty Room | 9 | Y2, jumble, window on pit, broken passage, small pit, and dusty rock room. |
| 11 — Special & Transient States | 7 | Death pseudo-rooms, transient message states, and the null location. |

## 01 — Surface World
- **Chapter ID:** `CH_SURFACE`
- **Locations:** 34
- **Description:** Above ground: building, road, hill, valley, forest, grate, and ledge.
- **Members:** `LOC_BUILDING`, `LOC_CLIFF`, `LOC_FOOF2`, `LOC_FOOF4`, `LOC_FOREST1`, `LOC_FOREST10`, `LOC_FOREST11`, `LOC_FOREST12`, `LOC_FOREST13`, `LOC_FOREST14`, `LOC_FOREST15`, `LOC_FOREST16`, `LOC_FOREST17`, `LOC_FOREST18`, `LOC_FOREST19`, `LOC_FOREST2`, `LOC_FOREST20`, `LOC_FOREST21`, `LOC_FOREST22`, `LOC_FOREST3`, `LOC_FOREST4`, `LOC_FOREST5`, `LOC_FOREST6`, `LOC_FOREST7`, `LOC_FOREST8`, `LOC_FOREST9`, `LOC_GRATE`, `LOC_HILL`, `LOC_LEDGE`, `LOC_ROADEND`, `LOC_SEWER`, `LOC_SLIT`, `LOC_START`, `LOC_VALLEY`

## 02 — Cave Entry
- **Chapter ID:** `CH_ENTRY`
- **Locations:** 12
- **Description:** First chambers beneath the grate up to the Hall of Mists.
- **Members:** `LOC_AWKWARD`, `LOC_BELOWGRATE`, `LOC_BIRDCHAMBER`, `LOC_COBBLE`, `LOC_CRACK`, `LOC_DEBRIS`, `LOC_EASTBANK`, `LOC_FOOF1`, `LOC_MISTHALL`, `LOC_NUGGET`, `LOC_PITTOP`, `LOC_WESTBANK`

## 03 — Hall of Mountain King & Twopit
- **Chapter ID:** `CH_CENTRAL`
- **Locations:** 18
- **Description:** Central cave complex, Mountain King hall, Twopit Room, Giant Room, and waterfall.
- **Members:** `LOC_BUILDING1`, `LOC_CAVEIN`, `LOC_CLIMBSTALK`, `LOC_CROSSOVER`, `LOC_EASTEND`, `LOC_EASTPIT`, `LOC_FLOORHOLE`, `LOC_GIANTROOM`, `LOC_IMMENSE`, `LOC_KINGHALL`, `LOC_NARROW`, `LOC_NOCLIMB`, `LOC_PLANTTOP`, `LOC_SOUTHSIDE`, `LOC_WATERFALL`, `LOC_WESTEND`, `LOC_WESTPIT`, `LOC_WESTSIDE`

## 04 — Maze (All Alike)
- **Chapter ID:** `CH_MAZE_ALIKE`
- **Locations:** 33
- **Description:** The classic maze of twisty little passages, all alike.
- **Members:** `LOC_ALIKE1`, `LOC_ALIKE10`, `LOC_ALIKE11`, `LOC_ALIKE12`, `LOC_ALIKE13`, `LOC_ALIKE14`, `LOC_ALIKE2`, `LOC_ALIKE3`, `LOC_ALIKE4`, `LOC_ALIKE5`, `LOC_ALIKE6`, `LOC_ALIKE7`, `LOC_ALIKE8`, `LOC_ALIKE9`, `LOC_DEADEND7`, `LOC_LONGEAST`, `LOC_LONGWEST`, `LOC_MAZEEND1`, `LOC_MAZEEND10`, `LOC_MAZEEND11`, `LOC_MAZEEND12`, `LOC_MAZEEND2`, `LOC_MAZEEND3`, `LOC_MAZEEND4`, `LOC_MAZEEND5`, `LOC_MAZEEND6`, `LOC_MAZEEND8`, `LOC_MAZEEND9`, `LOC_MISTWEST`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_PITBRINK`, `LOC_TOPSTALACTITE`

## 05 — Bedquilt & Secret Canyons
- **Chapter ID:** `CH_BEDQUILT`
- **Locations:** 17
- **Description:** Bedquilt, Swiss Cheese Room, Slab Room, and the secret canyons above.
- **Members:** `LOC_BEDQUILT`, `LOC_BOULDERS1`, `LOC_COMPLEX`, `LOC_DEADCRAWL`, `LOC_LOWROOM`, `LOC_SECRET1`, `LOC_SECRET2`, `LOC_SECRET3`, `LOC_SECRET4`, `LOC_SECRET5`, `LOC_SECRET6`, `LOC_SLAB`, `LOC_SWISSCHEESE`, `LOC_TALL`, `LOC_THREEJUNCTION`, `LOC_TIGHTPLACE`, `LOC_WIDEPLACE`

## 06 — Oriental Room & Plover Passage
- **Chapter ID:** `CH_ORIENTAL_PLOVER`
- **Locations:** 12
- **Description:** Soft Room, Oriental Room, misty cavern, alcove, Plover Room, and dark-room.
- **Members:** `LOC_ALCOVE`, `LOC_ARCHED`, `LOC_CULDESAC`, `LOC_DARKROOM`, `LOC_FOOF5`, `LOC_INCLINE`, `LOC_MISTY`, `LOC_ORIENTAL`, `LOC_PLOVER`, `LOC_SHELLROOM`, `LOC_SLOPING1`, `LOC_SOFTROOM`

## 07 — Reservoir & Cliff Ascent
- **Chapter ID:** `CH_RESERVOIR`
- **Locations:** 12
- **Description:** Underground reservoir, mirror canyon, and the treacherous cliff climb.
- **Members:** `LOC_CLIFFACE`, `LOC_CLIFFBASE`, `LOC_CLIFFLEDGE`, `LOC_CLIFFTOP`, `LOC_MIRRORCANYON`, `LOC_REACHDEAD`, `LOC_RESBOTTOM`, `LOC_RESERVOIR`, `LOC_RESNORTH`, `LOC_STEEP`, `LOC_TREACHEROUS`, `LOC_WINDOW2`

## 08 — Repository & Volcano
- **Chapter ID:** `CH_REPOSITORY`
- **Locations:** 13
- **Description:** Dwarvish repository, chasm, volcano overlook, and barren room.
- **Members:** `LOC_BARRENFRONT`, `LOC_BARRENROOM`, `LOC_BOULDERS2`, `LOC_BREATHTAKING`, `LOC_CORRIDOR`, `LOC_FORK`, `LOC_LIMESTONE`, `LOC_NE`, `LOC_NECHASM`, `LOC_SW`, `LOC_SWCHASM`, `LOC_WARMWALLS`, `LOC_WINDING`

## 09 — Witt's End & Maze All-Different
- **Chapter ID:** `CH_WITT_DIFFERENT`
- **Locations:** 18
- **Description:** Construction area, Witt's End, and the maze of twisting passages, all different.
- **Members:** `LOC_ANTEROOM`, `LOC_BADDIRECTION`, `LOC_DEADEND13`, `LOC_DIFFERENT1`, `LOC_DIFFERENT10`, `LOC_DIFFERENT11`, `LOC_DIFFERENT2`, `LOC_DIFFERENT3`, `LOC_DIFFERENT4`, `LOC_DIFFERENT5`, `LOC_DIFFERENT6`, `LOC_DIFFERENT7`, `LOC_DIFFERENT8`, `LOC_DIFFERENT9`, `LOC_LARGE`, `LOC_ROUGHHEWN`, `LOC_STOREROOM`, `LOC_WITTSEND`

## 10 — Y2, Windows & Dusty Room
- **Chapter ID:** `CH_Y2_WINDOWS`
- **Locations:** 9
- **Description:** Y2, jumble, window on pit, broken passage, small pit, and dusty rock room.
- **Members:** `LOC_BROKEN`, `LOC_DUSTY`, `LOC_FOOF3`, `LOC_FOOF6`, `LOC_JUMBLE`, `LOC_SMALLPIT`, `LOC_SMALLPITBRINK`, `LOC_WINDOW1`, `LOC_Y2`

## 11 — Special & Transient States
- **Chapter ID:** `CH_SPECIAL`
- **Locations:** 7
- **Description:** Death pseudo-rooms, transient message states, and the null location.
- **Members:** `LOC_DOME`, `LOC_FOOTSLIP`, `LOC_GRUESOME`, `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_NOWHERE`, `LOC_SNAKEBLOCK`

## Cross-page connections

Connections that cross chapter boundaries are drawn as off-page references on each chapter page, with the target chapter noted implicitly by the marker's presence at the edge of the page. For the complete graph, inspect the JSON export or the source YAML.
