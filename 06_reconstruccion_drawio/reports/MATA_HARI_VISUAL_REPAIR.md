# MATA HARI VISUAL REPAIR — Mission 004

**Agent:** Mata Hari · **Date:** 2026-10-16 · **Scope:** `CH_ENTRY` (Cave Entry) 12-location pilot only  
**Deliverables:** `output/pilot/CH_ENTRY_MataHari_V2.drawio` · `output/pilot/CH_ENTRY_MataHari_V2.png` · `output/pilot/CH_ENTRY_MataHari_V2.svg` (diagnostic) · `tools/oa_pilot_v2.py`  
**Status:** `PASS` (Automated structural, directional, and rendered-SVG geometry validation PASS; visual inspection of exported PNG completed; ready for human cartographic review)

---

## 1. Root Cause of Invisible Arrows (Phase A)

### Primary Defect — Misplaced `id` on `<object>` Wrapper
**The 51 connectors in the Mission 003 pilot were never rendered at all.** This was not caused by thin strokes or low contrast.

In draw.io (`mxGraph` / `mxObjectCodec`), when a cell is wrapped in an `<object>` element to carry custom metadata attributes, **the cell `id` must be placed on the `<object id="...">` wrapper element**, not on the inner `<mxCell>`.

The Mission 001–003 generators (`tools/oa_drawio.py`, `tools/oa_drawio_v2.py`, `tools/oa_pilot.py`) placed `id="CH_ENTRY_LOC_..."` on the inner `<mxCell>` and omitted `id` on `<object>`:

```xml
<!-- Mission 003 (BROKEN): id on inner mxCell, missing on <object> -->
<object label="..." source_id="LOC_AWKWARD" ...>
  <mxCell id="CH_ENTRY_LOC_AWKWARD" style="..." vertex="1" parent="1">
    <mxGeometry x="1520" y="520" width="300" height="190" as="geometry" />
  </mxCell>
</object>
```

When draw.io imports an `<object>` without an `id` attribute, `mxObjectCodec` overwrites the inner `mxCell.id` with `null` and assigns auto-generated sequential numeric IDs (`2` through `13`). Consequently:
- Every edge's `source="CH_ENTRY_LOC_..."` and `target="CH_ENTRY_LOC_..."` referenced non-existent cell IDs.
- Because the edges had no fallback terminal coordinates (`sourcePoint` / `targetPoint`), draw.io silently dropped all 51 edges at parse time.
- The exported Mission 003 SVG (`output/pilot/_diag_CH_ENTRY.svg`) and PNG contained the 12 location boxes and 19 gutter boxes, but **zero connector `<path>` elements**.

### Secondary Defect Discovered During Visual Inspection — Label Background Occlusion
Even after restoring edge rendering via `<object id="...">`, placing long single-line movement labels with `labelBackgroundColor=#FFFFFF` at the default center (`y = 0` offset) of a short horizontal connector causes the opaque white label background rectangle to paint directly over the connector shaft and arrowheads in SVG paint order. Offsetting horizontal labels `14 px` above the shaft (`<mxPoint x="0" y="-14" as="offset" />`) leaves both the connector line and both block arrowheads 100% unobstructed.

### Minimal Rendering Fixture Proof
Created via `tools/fixture.py` → `output/pilot/_fixture.drawio` and exported via `draw.io.exe` to `output/pilot/_fixture.svg` and `output/pilot/_fixture.png`:

| Pattern | XML Structure | Rendered SVG / PNG Result |
|---|---|---|
| **Pattern A (Fixed)** | `<object id="A"><mxCell vertex="1" .../></object>` | Renders connector `<path d="M 200 40 L 348.7 40" stroke="#000000" stroke-width="2.5"/>` + filled block arrowhead `<path d="M 357.2 40 L 345.2 46 ... Z"/>` |
| **Pattern B (Mission 003)** | `<object><mxCell id="C" vertex="1" .../></object>` | **Absent from export**; nodes renumbered to `2`, `3`; edge `E_broken` dropped completely |

> **Latent defect notice (out of scope, flagged for human direction):** The same `<object>` ID placement bug exists in `tools/oa_drawio.py` and `tools/oa_drawio_v2.py` (`output/Open_Adventure_World.drawio` and `output/Open_Adventure_World_V2.drawio`). Their validators checked XML self-consistency against inner `<mxCell id="...">` attributes rather than draw.io's `<object id="...">` resolution rules. Those files have been preserved untouched per Mission 004 scope rules.

---

## 2. Connection Simplification & Full Rule Preservation (Phase B)

All **51 canonical travel rules** for the 12 locations of `CH_ENTRY` are preserved without loss, alteration, or reordering:

1. **Node-level complete rule preservation (`51/51`):**
   - Every room `<object>` stores its complete canonical YAML travel rule array in `travel_rules` (JSON, verified byte-identical to `open_adventure_graph.json`).
   - Every room box displays its complete, untruncated English `long` description followed by **`EXITS (source precedence order)`**, numbered `1..N` in exact source evaluation order so conditional fallthroughs (such as `1. OUT, UPWAR → LOC_GRATE [not GRATE=GRATE_CLOSED]` followed by `2. OUT ✕ msg GRATE_NOWAY`) remain explicit.

2. **Internal room-to-room transitions (`32` rules → `19` visible connectors):**
   - **11 Primary spatial/structural connectors (`role="primary"`):**
     - **8 horizontal compass/passage connectors** (`strokeWidth=2.5`, solid `#000000`, `startArrow=block;endArrow=block`, aligned at identical vertical pixel Y across a `120 px` gap with labels offset `14 px` above the shaft).
     - **1 sloping canyon connector (`LOC_AWKWARD ↔ LOC_DEBRIS`)** (`strokeWidth=2.5`, solid `#000000`, `DOWN / E ↔ UP / W · canyon`).
     - **1 North–South connector (`LOC_MISTHALL ↔ LOC_NUGGET`)** (`strokeWidth=2.5`, solid `#000000`, `S · left ↔ N · hall`).
     - **1 vertical pit shaft (`LOC_PITTOP ↔ LOC_MISTHALL`)** (`strokeWidth=2.8`, solid blue `#1565C0`, `DOWN ↔ UP`, visually distinct from compass N/S).
     - **1 magic arrival (`LOC_FOOF1 → LOC_DEBRIS`)** (`strokeWidth=2.2`, dashed purple `#7B1FA2`, `(implicit)`).
   - **8 Parser fast-travel keyword connectors (`role="fast_travel"`):**
     - Represent the 11 non-adjacent `ENTRA`, `DEBRI`, and `PIT` keyword jump rules (`3` reciprocal pairs + `5` one-way jumps = `8` connectors).
     - Styled as restrained dashed grey lines (`#78909C`, `strokeWidth=1.4`) routed on dedicated non-overlapping bus tracks (`y = 148`, `y = 436..516`, and `y = 845`) with labels placed in riser-free horizontal windows (`Window A: x≈860`, `Window B: x≈1250`, `Window C: x≈2040`).
   - Every internal connector stores the exact list of source rules it represents in `represents_rules` JSON metadata (`internal_rules_partition: true` — exact partition of all 32 internal rules).

3. **External transitions & internal messages (`19` rules → `9` local markers + `5` in-room annotations):**
   - **5 internal `speak` rules** (`GRATE_NOWAY` in `LOC_BELOWGRATE`; `CROSS_BRIDGE` and `NO_CROSS` in `LOC_EASTBANK` and `LOC_WESTBANK`) are rendered as in-room `✕ msg` annotations in the numbered `EXITS` list and stored in `blocked_messages` metadata, rather than creating artificial destination room nodes.
   - **14 external `goto` rules** target **9 unique external destinations** (`LOC_GRATE`, `LOC_FOOF2`, `LOC_NECKBROKE`, `LOC_PARALLEL1`, `LOC_MISTWEST`, `LOC_NOMAKE`, `LOC_DOME`, `LOC_KINGHALL`, `LOC_JUMBLE`). Each unique destination is represented by **1 compact local reference marker** positioned adjacent to its origin room(s), linked by **10 short dashed connectors** (`X1..X10`) and storing all represented source rules (`14/14`) in `represents_rules` metadata.

---

## 3. Compact Stepped Visual Composition & Hierarchy (Phases C & D)

Instead of Mission 003's 7-room horizontal sprawl (`3310 × 1970 px`) and distant 19-box right-hand gutter column, `CH_ENTRY_MataHari_V2` organizes the 12 rooms into a compact, topologically faithful stepped composition (`2570 × 1255 px` — **50.3% smaller canvas area**):

| Tier | Y Coordinate | Rooms (West → East) | Topological Role |
|---|---|---|---|
| **Upper Tier** | `y = 175` | `LOC_CRACK (60)` · `LOC_PITTOP (470)` · `LOC_BIRDCHAMBER (880)` · `LOC_AWKWARD (1290)` · `LOC_FOOF1 (1660)` | Upper Canyon, Bird Chamber, Small Pit Rim & `XYZZY` Foof arrival |
| **Middle Tier (West)** | `y = 660` | `LOC_WESTBANK (60)` · `LOC_EASTBANK (470)` · `LOC_MISTHALL (880)` | Deep Cave (`DEEP=True`): Hall of Mists & Fissure Banks (below `LOC_PITTOP`) |
| **Middle Tier (East)** | `y = 660` | `LOC_DEBRIS (1400)` · `LOC_COBBLE (1810)` · `LOC_BELOWGRATE (2220)` | Surface Entry Crawl (`LIT=True`) & Debris Room, stepped **down (`+485 px`) and east (`+110 px`)** from `LOC_AWKWARD` |
| **South Tier** | `y = 1060` | `LOC_NUGGET (880)` | Nugget of Gold Room (south of `LOC_MISTHALL`) |

### Key Cartographic Improvements
- **Honest canyon slope (`LOC_AWKWARD ↔ LOC_DEBRIS`):** Because `LOC_DEBRIS` describes *"an awkward canyon leads upward and west"* (`UPWAR, WEST → LOC_AWKWARD`) and `LOC_AWKWARD` has `DOWN, EAST, DEBRI → LOC_DEBRIS`, placing `LOC_AWKWARD` at `(1290, 175)` and `LOC_DEBRIS` at `(1400, 660)` satisfies both the primary `EAST`/`WEST` constraint (`dx = +110`) **and** the secondary `DOWN`/`UPWAR` elevation change (`dy = +485`).
- **Gold-nugget stairs puzzle clarity (`LOC_PITTOP ↔ LOC_MISTHALL`):** The blue vertical shaft (`DOWN ↔ UP`) between `LOC_PITTOP` and `LOC_MISTHALL` is flanked directly by its two conditional failure states: `☠ LOC_NECKBROKE` (`DOWN [carry NUGGET]` below `LOC_PITTOP`) and `⚠ LOC_DOME` (`UP [carry NUGGET]` above `LOC_MISTHALL`).
- **Surface grate orientation (`M_LOC_GRATE`):** Positioned directly above `LOC_BELOWGRATE` (`OUT, UPWAR [not GRATE=GRATE_CLOSED]`), reflecting the physical grate to the surface above the chamber.
- **Visual hierarchy:**
  - Playable rooms: white fill (`#FFFFFF`), dark border (`#333333`), full untruncated description + numbered exits.
  - Transient/special pseudo-rooms: dashed border, grey (`#F5F5F5` for `LOC_CRACK`) or light purple (`#F3E5F5` for `LOC_FOOF1`).
  - Local reference markers: yellow (`#FFF9C4`, stroke `#F57C00`) for cross-chapter rooms, orange (`#FFF3E0`, stroke `#E65100`) for transient states (`LOC_DOME`), red (`#FFEBEE`, stroke `#C62828`) for death hazards (`LOC_NECKBROKE`, `LOC_NOMAKE`), and purple (`#F3E5F5`, stroke `#7B1FA2`) for magic word teleports (`LOC_FOOF2`).

---

## 4. Validation Results (Phase E)

| Check Category | Metric | Mission 003 Pilot | Mission 004 Pilot V2 | Status |
|---|---|---|---|---|
| **Structural** | Locations preserved | `12/12` | `12/12` | `PASS` |
| **Structural** | Canonical travel rules preserved | `51/51` | `51/51` (exact JSON round-trip) | `PASS` |
| **Structural** | Internal rules partitioned across connectors | `32/32` (unrendered) | `32/32` across `19` connectors | `PASS` |
| **Structural** | External `goto` rules on local markers | `14` (in distant gutter) | `14/14` across `9` local markers | `PASS` |
| **Structural** | Internal `speak` rules preserved | `5` (as gutter boxes) | `5/5` in-room annotations + metadata | `PASS` |
| **Structural** | Untruncated English `long` descriptions | `10/12` (2 truncated) | `12/12` (0 truncated) | `PASS` |
| **Structural** | Dangling connector endpoints (`<object id>`) | **51 dangling** | **`0` dangling** (`29/29` resolve) | `PASS` |
| **Structural** | Deterministic XML generation | `PASS` | `PASS` (SHA-256 `f0c5a1f5a4184e0f`) | `PASS` |
| **Directional** | Applicable primary directional constraints | `17/17` | **`17/17` (`0` violations, `0` dropped)** | `PASS` |
| **Directional** | Compound canyon slope (`AWKWARD ↔ DEBRIS`) | `dy = 0` (flat row) | **`dx = +110, dy = +485` (`DOWN, E` / `UP, W`)** | `PASS` |
| **Rendered SVG** | Visible connectors rendered in SVG | **`0`** | **`29/29`** (`19` internal + `10` external) | `PASS` |
| **Rendered SVG** | Bidirectional / unidirectional arrowheads | `0` / `0` | **`13` double + `16` single (`0` missing)** | `PASS` |
| **Rendered SVG** | Line segments crossing foreign box interiors | N/A (`0` rendered) | **`0 / 62` segments** | `PASS` |
| **Rendered SVG** | Room / marker box overlaps | `0` | **`0`** | `PASS` |
| **Canvas & PNG** | Page size / PNG dimensions (`-s 2 --crop`) | `3310 × 1970` (`6305 × 3862`) | **`2570 × 1255` (`4906 × 2454`, 27.8% ink)** | `PASS` |

### Preserved Prior Deliverables (Unmodified SHA-256 Hashes)
- `Open_Adventure.yaml`: `4ee2c6451a64591b…`
- `output/Open_Adventure_World.drawio`: `605295e295a1f09a…`
- `output/Open_Adventure_World_V2.drawio`: `d7834725142d3cf2…`
- `output/open_adventure_graph.json`: `c6ee8bf9c46638d8…`
- `output/pilot/CH_ENTRY_MataHari.drawio`: `4fedddcf36ebc700…`
- `output/pilot/CH_ENTRY_MataHari.png`: `3a5ca1167d99c0b6…`

---

## 5. Reproduction Commands

```powershell
cd 'G:\Mi unidad\RPG_Archaeology_IF\06_reconstruccion_drawio'

# 1. Phase A minimal rendering fixture (.drawio + .svg + .png)
python tools/fixture.py
& 'G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe' -x -f png -s 2 --crop -o 'output\pilot\_fixture.png' 'output\pilot\_fixture.drawio' | Out-Null

# 2. Generate CH_ENTRY_MataHari_V2.drawio and run structural validation
python tools/oa_pilot_v2.py

# 3. Export PNG and SVG via draw.io Desktop
& 'G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe' -x -f png -s 2 --crop -o 'output\pilot\CH_ENTRY_MataHari_V2.png' 'output\pilot\CH_ENTRY_MataHari_V2.drawio' | Out-Null
& 'G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe' -x -f svg --crop -o 'output\pilot\CH_ENTRY_MataHari_V2.svg' 'output\pilot\CH_ENTRY_MataHari_V2.drawio' | Out-Null

# 4. Run rendered-SVG geometry verification and final check battery
python tools/verify_svg_v2.py
python tools/final_check_v2.py
```

---

## 6. Remaining Limitations & Recommended Next Step

1. **Full V1/V2 world maps (`Open_Adventure_World.drawio`, `Open_Adventure_World_V2.drawio`):** Both files still carry the `<object>` missing-`id` defect identified in Phase A and are preserved untouched per Mission 004 scope constraints. Applying the `<object id="...">` fix and V2 visual hierarchy across all 11 chapters requires human authorization.
2. **Parser fast-travel aliases (`ENTRA`, `DEBRI`, `PIT`):** All 8 non-adjacent fast-travel connectors are preserved as visible dashed grey bus lines so every room-to-room transition is graphically traceable. If human review prefers hiding parser-only fast-travel aliases from the graphical layer (keeping them in room `EXITS` text and `travel_rules` metadata only), they can be toggled via `role="fast_travel"`.
3. **Recommended next step:** Human cartographic review of `output/pilot/CH_ENTRY_MataHari_V2.png` and `output/pilot/CH_ENTRY_MataHari_V2.drawio` in draw.io Desktop to authorize scaling the V2 visual cartography pipeline to the remaining 10 chapters.
