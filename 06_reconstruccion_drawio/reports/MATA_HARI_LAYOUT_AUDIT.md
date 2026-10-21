# MATA HARI LAYOUT AUDIT — Mission 003

**Agent:** Mata Hari · **Date:** 2026-10-16 · **Scope:** bounded audit + CH_ENTRY pilot
**Verdict:** V2's directional failures in CH_ENTRY are **implementation defects, not properties of the adventure**. The chapter's full constraint set is satisfiable, and the pilot satisfies 17/17 directional constraints.

---

## 1. Root-cause analysis (Phase A)

All references are to `tools/oa_layout.py` (V2 layout engine, unmodified and preserved).

### RC1 — Flat entry-row seeding ignores all constraints
`_place_nodes_bfs`, line 99: `positions[n] = (i * BASE_DX, 0.0)`.

Every node with an incoming cross-chapter edge is seeded into a horizontal row at y=0 **before any directional information is considered**. For CH_ENTRY the seeds are `LOC_BELOWGRATE, LOC_BIRDCHAMBER, LOC_FOOF1, LOC_MISTHALL, LOC_WESTBANK` (reproduce: `python tools/audit_trace_v2.py`). The row directly pre-violates `LOC_BIRDCHAMBER --WEST--> LOC_PITTOP` (both end up at x=320) and `LOC_PITTOP --DOWN--> LOC_MISTHALL` (same row, Δy=0).

### RC2 — First-placement-wins BFS discards most constraints
`_place_nodes_bfs`, lines 112–135: a node is placed by the **first** edge that reaches it; every later edge to the same node is `SKIP`ped.

Instrumented trace on CH_ENTRY: **20 of 32 internal edges (63%) had zero influence on any coordinate.** Example: `LOC_DEBRIS --WEST--> LOC_AWKWARD` was skipped because `LOC_AWKWARD` had already been placed to the *east* of `LOC_DEBRIS` via `LOC_BIRDCHAMBER --EAST-->`. The entire west-chain (belowgrate > cobble > debris > awkward > birdchamber > pittop) is never established as a chain.

### RC3 — Semantic edges always place targets to the RIGHT
`_semantic_position`, lines 136–141: `return (sx + BASE_DX, ...)`.

Edges whose verbs carry no compass word (e.g. `LOC_BELOWGRATE --DEBRI--> LOC_DEBRIS`) unconditionally place the target to the **east**. `LOC_DEBRIS` landed east of `LOC_BELOWGRATE`/`LOC_COBBLE`, directly manufacturing the observed `LOC_COBBLE --WEST--> LOC_DEBRIS` violation (Δx=+640, destination placed right).

### RC4 — Constraint-blind overlap removal
`_remove_overlaps`, lines 149–190: overlapping boxes are pushed apart along the smallest-overlap axis with **no re-check of directional constraints**. In the CH_ENTRY trace it moved 7 nodes by up to ±182 px purely vertically; the violation set was unchanged (7 before, 7 after) — the pushes are arbitrary relative to the constraint set.

### RC5 — Spacing constants guarantee overlaps
Line 34: `BASE_DX = 320` equals the overlap-test width (`NODE_WIDTH 280 + 40`); line 36: `DIAGONAL_SCALE = 0.85` makes diagonal offsets (272, 187) strictly smaller. Adjacent and diagonal placements **always** overlap, so RC4's arbitrary pushes always fire.

### RC7 — Vertical-up symbol never recognised (new finding)
Line 33: `COMPASS_ORDER` contains `"UP"`, but the source YAML's travel verb for vertical-up is **`UPWAR`** (motion symbol `UP` has words `['upwar', 'up', ...]`, yet travel rules spell the verb `UPWAR`, e.g. `{verbs: [UPWAR], action: [goto, LOC_PITTOP]}`).

Consequence: every pure `UPWAR` edge is misclassified as *semantic* and shoved east by RC3. In CH_ENTRY this hid `LOC_MISTHALL --UPWAR--> LOC_PITTOP` from the directional metrics entirely — V2's own report undercounted applicable constraints as 16; the correct number is **17**. Other chapters are affected too (e.g. `LOC_ALIKE1 --UPWAR--> LOC_MISTWEST`, `LOC_WINDING --UPWAR--> LOC_SWCHASM`).

### Not the adventure's fault
Exhaustive constraint analysis of CH_ENTRY (Bellman-Ford on the difference-constraint system, see §2): **zero positive cycles — all 17 directional constraints are simultaneously satisfiable.** The four "known examples" in the mission brief (WESTEND/EASTEND, COBBLE/DEBRIS, KINGHALL/FLOORHOLE, START/BUILDING) are all in the same category: greedy-placement artifacts.

---

## 2. What was changed (Phase B)

New files only; **no existing tool or output was modified**:

| File | Purpose |
|---|---|
| `tools/oa_layout_v3.py` | Constraint-solver layout: difference constraints per axis, solved exactly with Bellman-Ford longest paths; positive cycles are *proven contradictions* and are dropped + reported, never silently violated. Text-aware node heights computed **before** layout so vertical gaps always clear the real boxes. Deterministic slot search (anchored to first internal neighbour) for nodes with free axes; constraint-aware overlap resolution as safety net. Corrected direction classifier (`UPWAR` recognised; `DOWNS` still treated as the semantic word "downstream", not vertical). |
| `tools/oa_pilot.py` | Pilot generator + validation + baseline comparison. Nodes carry full metadata (unchanged schema, bilingual-ready), exit summaries in **original rule-precedence order**, directional connection points (exit/entry perimeter hints per compass direction; UP/DOWN use a distinct 0.72 channel so vertical and compass channels never coincide), parallel lanes for reciprocal edge pairs, gutter markers for cross-page/speak/special rules with **exact destination ID + chapter page**. |
| `tools/audit_trace_v2.py` | Instrumented V2 trace used for §1 evidence. |
| `tools/debug_pilot.py` | Position/metric dump used during development. |

Editorial placement hint (documented, affects placement only, never metrics): `LOC_WESTBANK` is placed west of `LOC_EASTBANK`, justified by the source descriptions *"east bank of a fissure"* / *"west side of the fissure"*.

## 3. Baseline vs pilot — identical measurement definitions (Phase D)

Measurements use the **corrected** classifier (17 applicable constraints) for both layouts; box intersections/crossings are approximations under a directional-connector L-path model.

| Metric | V2 baseline | Pilot (v3) |
|---|---|---|
| Locations present | 12/12 | 12/12 |
| Travel rules preserved | 51/51 | 51/51 (32 internal edges + 19 markers + exit summaries in source order) |
| Applicable directional constraints | 17 | 17 |
| Satisfied | **9** | **17** |
| Violated | **8** | **0** |
| Proven contradictory constraints | — (not measured by V2) | **0** (all 17 provably satisfiable) |
| Location-box overlaps | 0 | 0 |
| Text-overflow risk (nodes whose content exceeds box height) | **9 of 12** (fixed 150 px boxes; worst: `LOC_MISTHALL` needs +190 px) | **0** (heights computed from content, 110–340 px) |
| Edge/box intersections (approx.) | 18 | 11 |
| Edge crossings (approx., excluding edges sharing endpoints) | 15 | 17 |
| Page size | 2040 × 748 | 3310 × 1970 |

Honest reading: the pilot trades compactness (larger page, driven by text-aware heights and constraint-satisfying spacing) and a marginal crossing increase under the crude L-model (15→17, while box intersections drop 18→11) for full directional correctness, zero overflow, and zero overlap. Priority order of the mission (legibility > non-overlap > semantics > compass consistency > routing > compactness) is respected. The remaining box intersections come from long-haul *semantic* shortcut verbs (`PIT`, `ENTRA`, `DEBRI` — "teleport-style" navigation words) which inherently span the map; draw.io's orthogonal router typically dodges boxes better than the L-model predicts, but that claim needs the pending visual check.

Pilot coordinates (y=520 row, west→east cave chain):
`LOC_CRACK(440) · LOC_PITTOP(800) · LOC_BIRDCHAMBER(1160) · LOC_AWKWARD(1520) · LOC_DEBRIS(1880) · LOC_COBBLE(2240) · LOC_BELOWGRATE(2600)`; `LOC_MISTHALL` below `LOC_PITTOP` (Δy=+400), `LOC_NUGGET` south of `LOC_MISTHALL`, `LOC_EASTBANK` west of `LOC_MISTHALL`, `LOC_WESTBANK` west of `LOC_EASTBANK`, `LOC_FOOF1` above `LOC_DEBRIS`.

## 4. Validation and regression protection

| Check | Result |
|---|---|
| 12/12 pilot locations, IDs match chapter membership, no duplicates | PASS |
| 51/51 travel rules preserved (32 internal edges + 19 markers; exit summaries in source order) | PASS |
| English descriptions round-trip (`description_en` == YAML long text) | PASS |
| No unintended destinations introduced | PASS (edges reference only source-recorded targets) |
| Location-box overlaps in generated XML | PASS (0) |
| Native draw.io XML parses | PASS |
| Node IDs stable (same `CH_ENTRY_<LOC>` scheme as V2) | PASS |
| Deterministic regeneration | PASS (byte-identical, SHA-256 prefix `4fedddcf36ebc700`) |
| Preserved V2 full-map validation (`python tools/oa_validate_v2.py`) | PASS (185/185, 623/623, hash `d7834725142d3cf2` unchanged) |
| `Open_Adventure.yaml` untouched | PASS (SHA-256 `4ee2c645…f35747`, identical to Mission 001 record) |

## 5. Render / export evidence (Phase C)

- Executable verified at `G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe` (inspected before invocation).
- Command used:
  `& 'G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe' -x -f png -s 2 --crop -o output\pilot\CH_ENTRY_MataHari.png output\pilot\CH_ENTRY_MataHari.drawio`
- Export succeeded: `output/pilot/CH_ENTRY_MataHari.png`, 6305 × 3862 px, RGB, 13.7 % non-white coverage, expected palette colours present (marker yellow `#FFF9C4`, speak-marker grey `#EEEEEE`, pseudo-location grey `#F5F5F5`).
- **Visual inspection:** this model cannot ingest images, so genuine visual review was **not performed**. Human visual inspection is **PENDING**: open `output/pilot/CH_ENTRY_MataHari.drawio` (or the PNG) and check readability, arrow directions, connector routing around boxes, and label legibility.

## 6. Reproduction

```powershell
cd 'G:\Mi unidad\RPG_Archaeology_IF\06_reconstruccion_drawio'
python tools/audit_trace_v2.py     # Phase A evidence (V2 trace)
python tools/oa_pilot.py           # generate + validate + compare (JSON to stdout)
python tools/debug_pilot.py        # positions + metric deltas
& 'G:\Mi unidad\RPG_Archaeology_IF\draw.io\draw.io.exe' -x -f png -s 2 --crop `
  -o output\pilot\CH_ENTRY_MataHari.png output\pilot\CH_ENTRY_MataHari.drawio
python tools/oa_validate_v2.py     # regression: preserved V2 must stay PASS
```

## 7. Status

- **Structural validation:** PASS
- **Directional validation:** PASS (17/17, 0 contradictions, 0 unresolved overlaps)
- **Render/export:** PASS (PNG produced)
- **Visual inspection:** PENDING (human)
- **Human approval required before** applying v3 to the other ten chapters.

## 8. Remaining imperfections

1. Edge-crossing count under the L-model is marginally higher than baseline (17 vs 15); draw.io's real router may improve this — verify visually.
2. Long-haul semantic shortcuts (`PIT`, `ENTRA`, `DEBRI`) still produce some box-adjacent routing (11 approx. intersections) — inherent to those rules being long-distance; could be refined with explicit waypoints after visual review.
3. Page is larger than V2 (3310 × 1970) — the cost of readable, non-overflowing text and honest spacing.
4. The `UPWAR` classification fix (RC7) also changes the *applicable-constraint count* for other chapters; full-map regeneration after approval must use the corrected classifier and re-baseline all chapter metrics.
