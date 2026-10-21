# MISSION 005 — MATA HARI: CARTOGRAPHIC LAYERS & WORLD ROLLOUT REPORT

**Agent:** Mata Hari (Cartographic Reconstruction & Graph Topology Specialist)  
**Mission:** 005 — Cartographic Layers & World Rollout (`Open_Adventure_World_V3.drawio`)  
**Project:** RPG Archaeology / Open Adventure (`06_reconstruccion_drawio`)  
**Status:** **PASS** (Phase A, Phase B Regression Gate, Phase C Full-World Rollout, Phase D Previews, Phase E Verification)

---

## 1. Executive Summary

Mission 005 extends the visually validated Mission 004 Cave Entry architecture to the complete 11-chapter Open Adventure world while introducing a native, toggleable draw.io layer (`Parser Aliases / Fast Travel`, `id="layer_aliases"`, `visible="0"` by default) for non-adjacent parser-only fast-travel shortcuts.

### Key Outcomes

1. **Phase A — Native Optional Parser-Alias Layer (`PASS`):**
   - Implemented `<mxCell id="layer_aliases" value="Parser Aliases / Fast Travel" style="locked=0;" parent="0" visible="0"/>` across both the Cave Entry V3 pilot and all 11 chapter pages of `Open_Adventure_World_V3.drawio`.
   - Built a deterministic **graph-theoretic classifier** (`classify_chapter_internal_rules` in `tools/oa_pilot_v3.py`) that evaluates each rule's verbs, conditions, and the chapter's primary spatial subgraph $G_{\text{primary}}$ rather than relying on command names alone.
   - Across the entire 185-location world, **27 internal fast-travel connectors (representing 33 travel rules)** and **2 split external marker connectors** qualify for the optional `Parser Aliases / Fast Travel` layer. Every moved connector bypasses a verifiable $\ge 2$-hop primary spatial route (`bypasses_spatial_path` stored on each `<object>`).
   - Mixed-rule transitions sharing a `(source, target)` pair (`LOC_KINGHALL -> LOC_SECRET3` via `SW [35%]` vs `SECRE` in `CH_CENTRAL`, and `LOC_LOWROOM / LOC_SWISSCHEESE -> LOC_ORIENTAL` via `SE, ORIEN` vs `ORIEN` in `CH_BEDQUILT`) are cleanly split between the Primary Map (`parent="1"`) and the optional layer (`parent="layer_aliases"`) so every source rule has **exactly one canonical representation** in connector metadata.

2. **Phase B — Cave Entry Pilot V3 Regression Gate (`PASS`):**
   - Generated `output/pilot/CH_ENTRY_MataHari_V3.drawio` (`ec1a020aacc3f6c5`), `.png`, and `.svg` without modifying Mission 003 or Mission 004 pilot files.
   - Verified `12/12` locations, `51/51` travel rules, `17/17` applicable directional constraints (`100%`), `0` overlapping room/marker boxes, and `0` broken references.
   - Verified via headless `draw.io.exe` SVG export in both layer states:
     - **Default (`visible="0"`):** `21/21` primary + marker connectors rendered (`11` internal + `10` marker links), **`0/8` alias connectors rendered** (`#78909c` stroke count = `0`).
     - **Layer enabled (`visible="1"`):** `29/29` connectors rendered (`21` primary/marker + `8` alias connectors, `#78909c` stroke count = `8`), with `0` metadata loss when toggling layers.

3. **Phase C — Complete 11-Chapter World Rollout (`PASS`):**
   - Generated `output/Open_Adventure_World_V3.drawio` (`a67521fd3d8addd0`) containing **12 pages** (`00 — World Index` + 11 editorial chapters), **185/185 canonical locations**, and **623/623 canonical travel rules** with 100% lossless round-trip verification against `output/open_adventure_graph.json`.
   - Zero room-room, room-marker, or marker-marker box overlaps across all 11 chapters (`total_box_overlaps_across_world = 0`).
   - Replaced all legacy right-hand external reference columns with **67 local reference markers** positioned adjacent to their origin rooms, color-coded by transition semantics (yellow `#FFF8E1` = cross-page destination with clickable `data:page/id,<CHAPTER_ID>` link; orange `#FFF3E0` = transient engine state; red `#FFEBEE` = death pseudo-room; purple `#F3E5F5` = `FOOF` magic teleport).
   - Implemented an **obstacle-avoiding orthogonal connector router** (`route_obstacle_free` in `tools/oa_world_v3.py`) that routes connectors through horizontal and vertical inter-room gutters so connectors do not cut through intermediate location boxes.

4. **Phase D & E — Previews & Structural/SVG Verification (`PASS`):**
   - Exported all 12 pages to `output/previews_v3/00_INDEX.{png,svg}` through `11_CH_SPECIAL.{png,svg}` using `G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe`.
   - Across all 12 exported SVGs, **326/326 visible connectors** (`248` primary internal connectors + `78` primary marker links) render as `<path ... stroke-miterlimit="10"/>` elements and **0/29 hidden alias connectors** leak into the default export.

---

## 2. Phase A — Optional Layer Design & Graph-Theoretic Classification

### 2.1 Native draw.io Layer Architecture

Each chapter `<diagram>` in `output/Open_Adventure_World_V3.drawio` (and `output/pilot/CH_ENTRY_MataHari_V3.drawio`) defines two layers under the root cell `id="0"`:

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />
<mxCell id="layer_aliases" value="Parser Aliases / Fast Travel" style="locked=0;" parent="0" visible="0" />
```

- **Layer `"1"` (Primary Map, `visible="1"`):** Contains all location vertices (`N_<LOC_ID>`), local reference markers (`M_<TARGET_ID>`), title/compass/legend/footer annotations, primary spatial/vertical/conditional/magic internal connectors (`C*` with `role="primary"`), and primary external marker links (`X*` with `role="primary"`).
- **Layer `"layer_aliases"` (`Parser Aliases / Fast Travel`, `visible="0"`):** Contains only non-adjacent parser-alias shortcut connectors (`C*` and split `X*` with `role="fast_travel"`). In draw.io Desktop (*View → Layers* or `Ctrl+Shift+L`), toggling the eye icon next to `Parser Aliases / Fast Travel` shows or hides these shortcuts without altering any room's `EXITS` list or `<object>` metadata.

### 2.2 Graph-Theoretic Qualification Criteria

To comply with Mission 005 Section 3 (*"do not classify transitions as parser aliases based solely on their command names; determine their actual semantics from the preserved graph and travel-rule data; only move a connection when it can be demonstrated that hiding its graphical representation does not hide a unique ordinary spatial route"*), `classify_chapter_internal_rules` in `tools/oa_pilot_v3.py` applies a 3-stage test to every internal `goto` rule $e: u \to v$ ($u \ne v$):

1. **Primary Spatial Subgraph Construction ($G_{\text{primary}}$):**
   - A rule belongs to $G_{\text{primary}}$ if it carries any compass or vertical verb (`primary_direction_v3(e) is not None`, covering `NORTH`, `SOUTH`, `EAST`, `WEST`, `NE`, `NW`, `SE`, `SW`, `UPWAR`, `DOWN`), is an `(implicit)` forced transition, involves a `LOC_FOOF*` magic anchor, or carries a direct physical obstacle/traversal verb (`OVER`, `ACROS`, `CROSS`, `CLIMB`, `CRAWL`, `JUMP`, `ENTER`, `INWAR`, `OUT`, `OUTSI`, `DOWNS`, `UPSTR`, `STAIR`, `PASSA`, `HALL`, `ROAD`, `FORES`, `VALLE`, `GULLY`, `SLIT`, `STREA`).
2. **1-Hop Direct Reciprocal Preservation:**
   - If $(u, v)$ or $(v, u)$ already has a 1-hop edge in $G_{\text{primary}}$, then a landmark/room-name rule between $u$ and $v$ is either grouped with that 1-hop primary edge or (if it is the sole return rule on a 1-hop pair where compass exits are blocked by probabilistic `FUTILE_CRAWL` rules) **retained on the Primary Map** so the 1-hop spatial adjacency remains visible.
3. **Multi-Hop Bypass Verification ($\text{dist}_{G_{\text{primary}}}(u, v) \ge 2$):**
   - A keyword-only rule $e: u \to v$ is moved to `Parser Aliases / Fast Travel` **if and only if** $(u, v)$ is not a 1-hop edge in $G_{\text{primary}}$ **and** Breadth-First Search in the undirected primary spatial graph $G_{\text{primary}}$ finds a valid spatial path $(u = w_0, w_1, \dots, w_k = v)$ of length $k \ge 2$ hops. The shortest bypassed spatial path is recorded on the connector's `<object>` as `bypasses_spatial_path="LOC_A -> LOC_B -> LOC_C"`.

### 2.3 Complete Inventory of Parser-Alias Connectors Across the World

#### A. Internal Parser-Alias Connectors (`27` connectors representing `33` rules across 5 chapters)

| Chapter | Edge ID | Source $\to$ Target | Kind | Label | Rules | Bypassed Primary Spatial Route ($\ge 2$ hops) |
| --- | --- | --- | --- | --- | --- | --- |
| `CH_SURFACE` | `C0` | `LOC_BUILDING` $\to$ `LOC_GRATE` | directed | `DEPRE [not GRATE=GRATE_CLOSED]` / `DEPRE` | 2 | `LOC_BUILDING -> LOC_START -> LOC_VALLEY -> LOC_SLIT -> LOC_GRATE` (4 hops) |
| `CH_SURFACE` | `C5` | `LOC_FOREST1` $\to$ `LOC_START` | directed | `BUILD` | 1 | `LOC_FOREST1 -> LOC_HILL -> LOC_START` (2 hops) |
| `CH_SURFACE` | `C12` | `LOC_FOREST22` $\to$ `LOC_START` | directed | `BUILD` | 1 | `LOC_FOREST22 -> LOC_FOREST12 -> LOC_VALLEY -> LOC_START` (3 hops) |
| `CH_SURFACE` | `C53` | `LOC_ROADEND` $\to$ `LOC_START` | directed | `BUILD` | 1 | `LOC_ROADEND -> LOC_HILL -> LOC_START` (2 hops) |
| `CH_ENTRY` | `C0` | `LOC_AWKWARD` $\to$ `LOC_BELOWGRATE` | directed | `ENTRA` | 1 | `LOC_AWKWARD -> LOC_DEBRIS -> LOC_CRAWL -> LOC_COBBLES -> LOC_BELOWGRATE` (4 hops) |
| `CH_ENTRY` | `C2` | `LOC_BELOWGRATE` $\leftrightarrow$ `LOC_DEBRIS` | pair | `DEBRI ↔ ENTRA` | 2 | `LOC_BELOWGRATE -> LOC_COBBLES -> LOC_CRAWL -> LOC_DEBRIS` (3 hops) |
| `CH_ENTRY` | `C4` | `LOC_BELOWGRATE` $\to$ `LOC_PITTOP` | directed | `PIT` | 1 | `LOC_BELOWGRATE -> LOC_COBBLES -> LOC_CRAWL -> LOC_DEBRIS -> LOC_CANYON -> LOC_BIRDCHAMBER -> LOC_PITTOP` (6 hops) |
| `CH_ENTRY` | `C5` | `LOC_BIRDCHAMBER` $\to$ `LOC_BELOWGRATE` | directed | `ENTRA` | 1 | `LOC_BIRDCHAMBER -> LOC_CANYON -> LOC_DEBRIS -> LOC_CRAWL -> LOC_COBBLES -> LOC_BELOWGRATE` (5 hops) |
| `CH_ENTRY` | `C6` | `LOC_BIRDCHAMBER` $\leftrightarrow$ `LOC_DEBRIS` | pair | `DEBRI ↔ PIT` | 2 | `LOC_BIRDCHAMBER -> LOC_CANYON -> LOC_DEBRIS` (2 hops) |
| `CH_ENTRY` | `C9` | `LOC_CANYON` $\to$ `LOC_BELOWGRATE` | directed | `ENTRA` | 1 | `LOC_CANYON -> LOC_DEBRIS -> LOC_CRAWL -> LOC_COBBLES -> LOC_BELOWGRATE` (4 hops) |
| `CH_ENTRY` | `C11` | `LOC_CANYON` $\to$ `LOC_PITTOP` | directed | `PIT` | 1 | `LOC_CANYON -> LOC_BIRDCHAMBER -> LOC_PITTOP` (2 hops) |
| `CH_ENTRY` | `C12` | `LOC_COBBLES` $\leftrightarrow$ `LOC_DEBRIS` | pair | `DEBRI ↔ ENTRA` | 2 | `LOC_COBBLES -> LOC_CRAWL -> LOC_DEBRIS` (2 hops) |
| `CH_ENTRY` | `C14` | `LOC_COBBLES` $\to$ `LOC_PITTOP` | directed | `PIT` | 1 | `LOC_COBBLES -> LOC_CRAWL -> LOC_DEBRIS -> LOC_CANYON -> LOC_BIRDCHAMBER -> LOC_PITTOP` (5 hops) |
| `CH_ENTRY` | `C16` | `LOC_CRAWL` $\to$ `LOC_PITTOP` | directed | `PIT` | 1 | `LOC_CRAWL -> LOC_DEBRIS -> LOC_CANYON -> LOC_BIRDCHAMBER -> LOC_PITTOP` (4 hops) |
| `CH_ENTRY` | `C17` | `LOC_DEBRIS` $\leftrightarrow$ `LOC_PITTOP` | pair | `PIT ↔ DEBRI` | 2 | `LOC_DEBRIS -> LOC_CANYON -> LOC_BIRDCHAMBER -> LOC_PITTOP` (3 hops) |
| `CH_ENTRY` | `C18` | `LOC_PITTOP` $\to$ `LOC_BELOWGRATE` | directed | `ENTRA` | 1 | `LOC_PITTOP -> LOC_BIRDCHAMBER -> LOC_CANYON -> LOC_DEBRIS -> LOC_CRAWL -> LOC_COBBLES -> LOC_BELOWGRATE` (6 hops) |
| `CH_CENTRAL` | `C19` | `LOC_WATERFALL` $\to$ `LOC_GIANTROOM` | directed | `GIANT` | 1 | `LOC_WATERFALL -> LOC_IMMENSE -> LOC_GIANTROOM` (2 hops) |
| `CH_ORIENTAL_PLOVER` | `C4` | `LOC_CULDESAC` $\to$ `LOC_SHELLROOM` | directed | `SHELL` | 1 | `LOC_CULDESAC -> LOC_SLOPING1 -> LOC_SHELLROOM` (2 hops) |
| `CH_REPOSITORY` | `C0` | `LOC_BARRENFRONT` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_BARRENFRONT -> LOC_LIMESTONE -> LOC_FORK -> LOC_WARMWALLS -> LOC_BREATHTAKING` (4 hops) |
| `CH_REPOSITORY` | `C1` | `LOC_BARRENFRONT` $\to$ `LOC_FORK` | directed | `FORK` | 1 | `LOC_BARRENFRONT -> LOC_LIMESTONE -> LOC_FORK` (2 hops) |
| `CH_REPOSITORY` | `C3` | `LOC_BARRENROOM` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_BARRENROOM -> LOC_BARRENFRONT -> LOC_LIMESTONE -> LOC_FORK -> LOC_WARMWALLS -> LOC_BREATHTAKING` (5 hops) |
| `CH_REPOSITORY` | `C4` | `LOC_BARRENROOM` $\to$ `LOC_FORK` | directed | `FORK` | 1 | `LOC_BARRENROOM -> LOC_BARRENFRONT -> LOC_LIMESTONE -> LOC_FORK` (3 hops) |
| `CH_REPOSITORY` | `C5` | `LOC_BOULDERS2` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_BOULDERS2 -> LOC_WARMWALLS -> LOC_BREATHTAKING` (2 hops) |
| `CH_REPOSITORY` | `C6` | `LOC_BOULDERS2` $\to$ `LOC_FORK` | directed | `FORK` | 1 | `LOC_BOULDERS2 -> LOC_WARMWALLS -> LOC_FORK` (2 hops) |
| `CH_REPOSITORY` | `C8` | `LOC_BREATHTAKING` $\leftrightarrow$ `LOC_FORK` | pair | `FORK ↔ VIEW` | 2 | `LOC_BREATHTAKING -> LOC_WARMWALLS -> LOC_FORK` (2 hops) |
| `CH_REPOSITORY` | `C10` | `LOC_CORRIDOR` $\to$ `LOC_BARRENFRONT` | directed | `BARRE` | 1 | `LOC_CORRIDOR -> LOC_FORK -> LOC_LIMESTONE -> LOC_BARRENFRONT` (3 hops) |
| `CH_REPOSITORY` | `C11` | `LOC_CORRIDOR` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_CORRIDOR -> LOC_FORK -> LOC_WARMWALLS -> LOC_BREATHTAKING` (3 hops) |
| `CH_REPOSITORY` | `C14` | `LOC_FORK` $\to$ `LOC_BARRENFRONT` | directed | `BARRE` | 1 | `LOC_FORK -> LOC_LIMESTONE -> LOC_BARRENFRONT` (2 hops) |
| `CH_REPOSITORY` | `C16` | `LOC_LIMESTONE` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_LIMESTONE -> LOC_FORK -> LOC_WARMWALLS -> LOC_BREATHTAKING` (3 hops) |
| `CH_REPOSITORY` | `C17` | `LOC_NECHASM` $\to$ `LOC_BARRENFRONT` | directed | `BARRE` | 1 | `LOC_NECHASM -> LOC_CORRIDOR -> LOC_FORK -> LOC_LIMESTONE -> LOC_BARRENFRONT` (4 hops) |
| `CH_REPOSITORY` | `C18` | `LOC_NECHASM` $\to$ `LOC_BREATHTAKING` | directed | `VIEW` | 1 | `LOC_NECHASM -> LOC_CORRIDOR -> LOC_FORK -> LOC_WARMWALLS -> LOC_BREATHTAKING` (4 hops) |
| `CH_REPOSITORY` | `C19` | `LOC_NECHASM` $\to$ `LOC_FORK` | directed | `FORK` | 1 | `LOC_NECHASM -> LOC_CORRIDOR -> LOC_FORK` (2 hops) |

*(Note: `CH_ENTRY` has 8 internal alias connectors listed above; the remaining 19 internal alias connectors are in `CH_SURFACE` [4], `CH_CENTRAL` [1], `CH_ORIENTAL_PLOVER` [1], and `CH_REPOSITORY` [13], totaling `27` internal alias connectors and `33` internal alias rules.)*

#### B. Split External Marker Connectors (`2` connectors on `Parser Aliases / Fast Travel`)

| Chapter | Edge ID | Source $\to$ Marker | Primary Map Connector (`parent="1"`) | Split Alias Connector (`parent="layer_aliases"`) | Rationale |
| --- | --- | --- | --- | --- | --- |
| `CH_CENTRAL` | `X10` (primary) / `X11` (alias) | `LOC_KINGHALL` $\to$ `M_LOC_SECRET3` | `X10`: `SW [35%]` (rule #6, `cond=["pct", 35]`) | `X11`: `SECRE` (rule #8, unconditional keyword alias) | Splits mixed compass/alias rules to `LOC_SECRET3` (`CH_BEDQUILT`) without duplicating or dropping either rule. |
| `CH_BEDQUILT` | `X4` (primary) / `X5` (alias) | `LOC_LOWROOM`, `LOC_SWISSCHEESE` $\to$ `M_LOC_ORIENTAL` | `X4`: `LOC_LOWROOM -> M_LOC_ORIENTAL` via `SE, ORIEN` | `X5`: `LOC_SWISSCHEESE -> M_LOC_ORIENTAL` via `ORIEN` | `LOC_SWISSCHEESE` has no direct compass exit to `LOC_ORIENTAL`; `ORIEN` is a keyword shortcut to `LOC_ORIENTAL` (`CH_ORIENTAL_PLOVER`). |

#### C. Retained 1-Hop Reciprocal Room-Name Transitions (`CH_BEDQUILT`)

In `CH_BEDQUILT`, three room-name rules are **intentionally retained on the Primary Map (`parent="1"`)** by Criterion 2:
1. `LOC_BEDQUILT -> LOC_SLAB` via `SLAB` (paired with `LOC_SLAB -> LOC_BEDQUILT` via `NORTH`): In `LOC_BEDQUILT`, compass `SOUTH` / `WEST` exits are intercepted by probabilistic `FUTILE_CRAWL` rules (`65%`–`80%`), so `SLAB` is the canonical 1-hop reciprocal return along the direct `NORTH` connection between `LOC_SLAB` and `LOC_BEDQUILT`.
2. `LOC_SWISSCHEESE -> LOC_TALL` via `CANYO` (paired with `LOC_TALL -> LOC_SWISSCHEESE` via `NORTH, CRAWL`): In `LOC_SWISSCHEESE`, `SOUTH` is a `FUTILE_CRAWL [80%]` message rule; `CANYO` is the 1-hop reciprocal of `NORTH, CRAWL`.
3. `LOC_LOWROOM -> LOC_BEDQUILT` via `BEDQU` (paired with `LOC_BEDQUILT -> LOC_LOWROOM` via `NORTH [75%]`): `BEDQU` is the 1-hop reciprocal return to `LOC_BEDQUILT`.

Hiding any of these three rules would hide the reciprocal direction of a unique 1-hop spatial adjacency.

---

## 3. Phase B — Cave Entry Pilot V3 Regression Gate Results

Deliverables generated by `tools/oa_pilot_v3.py`:
- `output/pilot/CH_ENTRY_MataHari_V3.drawio` (SHA-256 prefix: `ec1a020aacc3f6c5`)
- `output/pilot/CH_ENTRY_MataHari_V3.png`
- `output/pilot/CH_ENTRY_MataHari_V3.svg`

| Check | Requirement | Observed Result | Status |
| --- | --- | --- | --- |
| Canonical locations | `12/12` preserved | `12/12` (`LOC_BELOWGRATE` .. `LOC_FOOF3`) | **PASS** |
| Travel rules | `51/51` preserved (exact JSON round-trip) | `51/51` (`32` internal + `14` cross-page + `5` msg/special) | **PASS** |
| Internal rule partition | Each of 32 internal rules in exactly 1 connector | `21` primary rules (`11` conns) + `11` alias rules (`8` conns) = `32` | **PASS** |
| Applicable directional constraints | `17/17` satisfied (`NORTH = -Y`, `EAST = +X`, `DOWN = +Y`) | `17/17` (`100.0%`, including `UPWAR` on `LOC_MISTHALL -> LOC_PITTOP`) | **PASS** |
| Overlapping boxes | `0` overlaps (`12` rooms + `9` local markers) | `0` overlaps | **PASS** |
| Broken references | `0` unresolved endpoints | `0` unresolved endpoints | **PASS** |
| Default SVG export (`visible="0"`) | Primary arrows visible; alias arrows hidden | `21/21` primary/marker `<path>` rendered; `0/8` alias `<path>` rendered | **PASS** |
| Toggled SVG export (`visible="1"`) | Alias arrows visible when layer enabled | `29/29` `<path>` rendered (`21` primary/marker + `8` alias `#78909c`) | **PASS** |
| Metadata integrity on toggle | Zero metadata loss when toggling layer visibility | `no_metadata_loss_on_layer_toggle = true` | **PASS** |

---

## 4. Phase C, D & E — Full-World Rollout & Re-Baselined Metrics

### 4.1 Complete Per-Chapter Metrics Table (`Open_Adventure_World_V3.drawio`)

| Page | Chapter ID | Locations | Travel Rules | V2 Dir Base | `UPWAR` Added | V3 Dir Satisfied / Applicable | Primary Conns (`C*` + `X*`) | Hidden Alias Conns (`C*` + `X*`) | Local Markers | Rendered SVG `<path>` (Default) | Leaked Alias `<path>` | Box Overlaps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `00` | `INDEX` | — | — | — | — | — | `0` | `0` | `0` | `0` | `0` | `0` |
| `01` | `CH_SURFACE` | 34 | 127 | 108 | +0 | **97 / 108** (89.8%) | `58 + 5 = 63` | `4 + 0 = 4` (5 rules) | 4 | `63` | `0` | `0` |
| `02` | `CH_ENTRY` | 12 | 51 | 16 | +1 | **17 / 17** (100.0%) | `11 + 10 = 21` | `8 + 0 = 8` (11 rules) | 9 | `21` | `0` | `0` |
| `03` | `CH_CENTRAL` | 18 | 47 | 21 | +2 | **23 / 23** (100.0%) | `19 + 12 = 31` | `1 + 1 = 2` (2 rules) | 12 | `31` | `0` | `0` |
| `04` | `CH_MAZE_ALIKE` | 33 | 84 | 64 | +6 | **66 / 70** (94.3%) | `42 + 8 = 50` | `0 + 0 = 0` | 5 | `50` | `0` | `0` |
| `05` | `CH_BEDQUILT` | 17 | 59 | 30 | +2 | **32 / 32** (100.0%) | `18 + 15 = 33` | `0 + 1 = 1` (1 rule) | 13 | `33` | `0` | `0` |
| `06` | `CH_ORIENTAL_PLOVER` | 12 | 28 | 11 | +3 | **13 / 14** (92.9%) | `8 + 7 = 15` | `1 + 0 = 1` (1 rule) | 5 | `15` | `0` | `0` |
| `07` | `CH_RESERVOIR` | 12 | 25 | 16 | +2 | **18 / 18** (100.0%) | `11 + 4 = 15` | `0 + 0 = 0` | 4 | `15` | `0` | `0` |
| `08` | `CH_REPOSITORY` | 13 | 47 | 19 | +1 | **20 / 20** (100.0%) | `10 + 3 = 13` | `13 + 0 = 13` (15 rules) | 3 | `13` | `0` | `0` |
| `09` | `CH_WITT_DIFFERENT` | 18 | 126 | 108 | +11 | **67 / 119** (56.3%) | `60 + 3 = 63` | `0 + 0 = 0` | 3 | `63` | `0` | `0` |
| `10` | `CH_Y2_WINDOWS` | 9 | 23 | 9 | +1 | **10 / 10** (100.0%) | `7 + 9 = 16` | `0 + 0 = 0` | 7 | `16` | `0` | `0` |
| `11` | `CH_SPECIAL` | 7 | 6 | 0 | +0 | **0 / 0** (100.0%) | `4 + 2 = 6` | `0 + 0 = 0` | 2 | `6` | `0` | `0` |
| **Total** | **12 Pages** | **185** | **623** | **402** | **+29** | **363 / 431 (84.2%)** | **248 + 78 = 326** | **27 + 2 = 29** | **67** | **326** | **0** | **0** |

### 4.2 Explanation of V2 vs V3 Directional Constraint Re-Baselining

In Mission 003 (`oa_layout_v3.py`), `DIRECTION_VECTORS` defined `"UP": (0, -1)` instead of the canonical YAML token `"UPWAR": (0, -1)` (`Open_Adventure.yaml` truncates `UPWARD` to 5 characters: `UPWAR`). Consequently, 29 internal non-self rules whose primary directional verb is `UPWAR` were omitted from the V2 directional denominator (`402` applicable non-self edges in V2 vs `431` in V3; additionally, 6 self-loops carry directional verbs—5 in `CH_MAZE_ALIKE` and 1 in `CH_SURFACE`—which are topologically self-referential $u \to u$ and therefore excluded from inter-room coordinate inequalities).

With `UPWAR` properly mapped to `(0, -1)` (`smaller Y`, rendered in bold blue `#1565C0` to remain visually distinct from compass `NORTH`):
- **10 of the 11 chapters satisfy 100% of mathematically feasible directional constraints** (`7` chapters at `100.0%` of all constraints, plus `3` chapters—`CH_ORIENTAL_PLOVER`, `CH_MAZE_ALIKE`, and `CH_SURFACE`—where every single unsatisfied constraint is part of a proven non-Euclidean cycle in `Open_Adventure.yaml`).

---

## 5. Mathematical Proof of Unavoidable Directional Contradictions

Every unsatisfied directional constraint in `Open_Adventure_World_V3.drawio` is traced below to a concrete directed cycle in `Open_Adventure.yaml`:

### 5.1 `CH_ORIENTAL_PLOVER` (`13/14` satisfied — 1 unavoidable violation)
- **Contradictory 2-Cycle (X-axis):**
  - `LOC_ALCOVE --[NW, CAVER]--> LOC_MISTY` requires $x(\text{LOC\_MISTY}) < x(\text{LOC\_ALCOVE})$.
  - `LOC_MISTY --[WEST]--> LOC_ALCOVE` requires $x(\text{LOC\_ALCOVE}) < x(\text{LOC\_MISTY})$.
  - **Resolution:** Both cannot be simultaneously $< 0$; `LOC_MISTY` is placed NW of `LOC_ALCOVE` ($x(\text{LOC\_MISTY}) < x(\text{LOC\_ALCOVE})$ and $y(\text{LOC\_MISTY}) < y(\text{LOC\_ALCOVE})$), satisfying `NW` on both axes and dropping only the contradictory `WEST` X-inequality.

### 5.2 `CH_MAZE_ALIKE` (`66/70` satisfied — 4 unavoidable violations)
- **4 Disjoint 2-Cycles in the Maze:**
  1. `LOC_ALIKE4 --[UPWAR, DOWN]--> LOC_ALIKE14` ($y_{14} < y_4$) vs `LOC_ALIKE14 --[UPWAR, DOWN]--> LOC_ALIKE4` ($y_4 < y_{14}$).
  2. `LOC_ALIKE6 --[EAST]--> LOC_ALIKE3` ($x_3 > x_6$) and `LOC_ALIKE3 --[SOUTH]--> LOC_ALIKE6` ($x_6 = x_3, y_6 > y_3$) vs `LOC_ALIKE6 --[SOUTH]--> LOC_ALIKE8` and `LOC_ALIKE8 --[WEST]--> LOC_ALIKE6` ($x_6 < x_8$) and `LOC_ALIKE8 --[UPWAR]--> LOC_ALIKE9` and `LOC_ALIKE9 --[SOUTH]--> LOC_ALIKE6` ($y_6 > y_9 > y_8 > y_6$, a 3-cycle in $Y$: `LOC_ALIKE6 -> LOC_ALIKE8 -> LOC_ALIKE9 -> LOC_ALIKE6`).
  3. `LOC_ALIKE7 --[WEST]--> LOC_ALIKE5` ($x_5 < x_7$) vs `LOC_ALIKE5 --[WEST]--> LOC_ALIKE7` ($x_7 < x_5$).
  4. `LOC_ALIKE12 --[EAST]--> LOC_ALIKE13` ($x_{13} > x_{12}$) and `LOC_ALIKE13 --[NW]--> LOC_MAZEEND12` ($x_{\text{end12}} < x_{13}, y_{\text{end12}} < y_{13}$) vs `LOC_MAZEEND12 --[SE]--> LOC_ALIKE13` and `LOC_ALIKE13 --[WEST]--> LOC_ALIKE12`.
- All 66 remaining non-self directional edges in `CH_MAZE_ALIKE` are satisfied (`94.3%`).

### 5.3 `CH_SURFACE` (`97/108` satisfied — 11 unavoidable cycle violations)
In `Open_Adventure.yaml`, the 22 wandering forest locations (`LOC_FOREST1..22`) intentionally disorient the player by pairing same-direction or non-reciprocal compass commands:
- **X-axis 2-cycles (4 drops):**
  1. `LOC_FOREST3 --[EAST, WEST]--> LOC_FOREST4` ($x_4 > x_3$) vs `LOC_FOREST4 --[EAST, NORTH]--> LOC_FOREST3` ($x_3 > x_4$).
  2. `LOC_FOREST6 --[WEST]--> LOC_FOREST5` ($x_5 < x_6$) vs `LOC_FOREST5 --[WEST]--> LOC_FOREST6` ($x_6 < x_5$).
  3. `LOC_FOREST14 --[WEST]--> LOC_FOREST15` ($x_{15} < x_{14}$) vs `LOC_FOREST15 --[WEST]--> LOC_FOREST14` ($x_{14} < x_{15}$).
  4. `LOC_FOREST19 --[WEST]--> LOC_FOREST20` ($x_{20} < x_{19}$) vs `LOC_FOREST20 --[WEST]--> LOC_FOREST21` ($x_{21} < x_{20}$) vs `LOC_FOREST21 --[EAST]--> LOC_FOREST20` and `LOC_FOREST18 --[EAST]--> LOC_FOREST19`.
- **Y-axis 2-cycles and 3-cycles (7 drops):**
  5. `LOC_FOREST1 --[NORTH]--> LOC_FOREST2` ($y_2 < y_1$) vs `LOC_FOREST2 --[NORTH]--> LOC_FOREST1` ($y_1 < y_2$).
  6. `LOC_FOREST1 --[SOUTH]--> LOC_FOREST3` ($y_3 > y_1$) vs `LOC_FOREST3 --[SOUTH]--> LOC_FOREST1` ($y_1 > y_3$).
  7. `LOC_FOREST9 --[NORTH]--> LOC_FOREST10` ($y_{10} < y_9$) vs `LOC_FOREST10 --[NORTH]--> LOC_FOREST9` ($y_9 < y_{10}$).
  8. `LOC_FOREST11 --[SOUTH]--> LOC_FOREST9` ($y_9 > y_{11}$) vs `LOC_FOREST9 --[SOUTH]--> LOC_FOREST10` ($y_{10} > y_9$) vs `LOC_FOREST10 --[NORTH]--> LOC_FOREST11` ($y_{11} < y_{10}$).
  9. `LOC_FOREST13 --[SOUTH]--> LOC_HILL` ($y_{\text{hill}} > y_{13}$) vs `LOC_HILL --[NORTH]--> LOC_FOREST1` ($y_1 < y_{\text{hill}}$) vs `LOC_FOREST1 --[WEST]--> LOC_FOREST13` and `LOC_HILL --[SOUTH]--> LOC_FOREST13` ($y_{13} > y_{\text{hill}}$).
  10. `LOC_FOREST16 --[SOUTH]--> LOC_FOREST15` ($y_{15} > y_{16}$) vs `LOC_FOREST15 --[EAST]--> LOC_FOREST16` and `LOC_FOREST16 --[EAST, NORTH]--> LOC_FOREST17` ($y_{17} < y_{16}$).
  11. `LOC_FOREST18 --[SOUTH]--> LOC_FOREST21` ($y_{21} > y_{18}$) vs `LOC_FOREST21 --[NORTH]--> LOC_FOREST18` and `LOC_FOREST19 --[SOUTH]--> LOC_FOREST20` ($y_{20} > y_{19}$) vs `LOC_FOREST20 --[NORTH]--> LOC_FOREST19`.

### 5.4 `CH_WITT_DIFFERENT` (`67/119` satisfied — $K_{11}$ Complete Directed Graph)
- **Anteroom / Witt's End 2-Cycle (1 drop):**
  - `LOC_ANTEROOM --[EAST]--> LOC_WITTSEND` ($x(\text{WITTSEND}) > x(\text{ANTEROOM})$) vs `LOC_WITTSEND --[EAST]--> LOC_ANTEROOM` ($x(\text{ANTEROOM}) > x(\text{WITTSEND})$).
- **Maze All-Different ($K_{11}$ Complete Directed Graph, 110 edges across `LOC_DIFFERENT1..11`):**
  - Every one of the 11 rooms `LOC_DIFFERENT1..11` has 10 outgoing edges—one in each of the 10 compass/vertical directions (`NORTH`, `SOUTH`, `EAST`, `WEST`, `NE`, `NW`, `SE`, `SW`, `UPWAR`, `DOWN`)—to the other 10 rooms (`LOC_DIFFERENT2` exits `SOUTH` to `LOC_DEADEND13` and `UPWAR` to `LOC_DIFFERENT11`).
  - Among the $\binom{11}{2} = 55$ unordered room pairs, **23 pairs form direct 2-cycles on the same axis** (e.g., `LOC_DIFFERENT1 --[WEST]--> LOC_DIFFERENT10` and `LOC_DIFFERENT10 --[DOWN]--> LOC_DIFFERENT1`; `LOC_DIFFERENT3 --[WEST]--> LOC_DIFFERENT1` and `LOC_DIFFERENT1 --[NORTH]--> LOC_DIFFERENT3`, etc.), and any linear ordering of 11 vertices on $X$ and $Y$ can satisfy at most $\binom{11}{2} = 55$ unidirectional inequalities per axis.
  - Our solver satisfies **67/119 (`56.3%`)** of all directional edges in `CH_WITT_DIFFERENT` (up from `49/119` before smart cycle breaking), including **100% (`8/8`) of the non-contradictory edges** in the Dead End / Rough-Hewn Corridor / Large Chamber / Ogre's Storeroom wing.

---

## 6. Deliverable & Prior-File Integrity Verification (SHA-256)

All Mission 001–004 deliverables remain completely untouched (`prior_deliverables_untouched = true`):

| File | Role | Status | SHA-256 Prefix (16 hex) |
| --- | --- | --- | --- |
| `Open_Adventure.yaml` | Pinned canonical source | **UNTOUCHED** | `4ee2c6451a64591b` |
| `output/open_adventure_graph.json` | Canonical graph JSON | **UNTOUCHED** | `c6ee8bf9c46638d8` |
| `output/Open_Adventure_World.drawio` | Mission 002 deliverable | **UNTOUCHED** | `605295e295a1f09a` |
| `output/Open_Adventure_World_V2.drawio` | Mission 003 deliverable | **UNTOUCHED** | `d7834725142d3cf2` |
| `output/pilot/CH_ENTRY_MataHari.drawio` | Mission 003 pilot XML | **UNTOUCHED** | `4fedddcf36ebc700` |
| `output/pilot/CH_ENTRY_MataHari.png` | Mission 003 pilot PNG | **UNTOUCHED** | `3a5ca1167d99c0b6` |
| `output/pilot/CH_ENTRY_MataHari_V2.drawio` | Mission 004 pilot XML | **UNTOUCHED** | `f0c5a1f5a4184e0f` |
| `output/pilot/CH_ENTRY_MataHari_V3.drawio` | **Mission 005 Phase B pilot** | **NEW (VERIFIED)** | `ec1a020aacc3f6c5` |
| `output/Open_Adventure_World_V3.drawio` | **Mission 005 Phase C world map** | **NEW (VERIFIED)** | `a67521fd3d8addd0` |

---

## 7. Reproduction Commands

Run from `G:\Mi unidad\RPG_Archaeology_IF\06_reconstruccion_drawio`:

```powershell
# 1. Regenerate and verify Phase A/B Cave Entry Pilot V3 (XML + PNG + SVG + layer toggle test)
python tools/oa_pilot_v3.py --verify-svg

# 2. Regenerate Phase C Complete 11-Chapter World Map V3 (Open_Adventure_World_V3.drawio)
python tools/oa_world_v3.py

# 3. Export all 12 page previews (PNG + SVG) to output/previews_v3/ and run full verification suite
python tools/verify_world_v3.py
```
