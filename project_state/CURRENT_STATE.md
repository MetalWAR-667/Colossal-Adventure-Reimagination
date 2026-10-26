# Current State — Colossal Adventure: Reimagination

**Document status:** `CURRENT / REVIEW`
**Documentation task:** `CAR-DOC-001` — closed and published
**Observed state at CAR-AUTO-001 preflight (2026-10-25):** local `main` at `176492ab13f418414c18df6775ec28cabaa88122`; four CAR-AUTO-001 commits ahead of local `origin/main` at `b5623864d11e0081096df5e4a61900a5ef4bc4a6`. Remote not queried live.
**Historical baseline:** `f59c413550dd3566e63af0c98a8df17a96359768`

## Project Identity

Colossal Adventure: Reimagination is an RPG Archaeology research and
reinterpretation project based on Colossal Cave Adventure. Its playable cut is
an independent Godot 4.7.2 application. Original project work is licensed
`GPL-3.0-or-later`; historical sources and third-party materials retain the
specific licenses recorded in [NOTICE.md](../NOTICE.md). The public primary
branch is `main`.

## Baseline

The first public baseline is commit
[`f59c413550dd3566e63af0c98a8df17a96359768`](https://github.com/MetalWAR-667/Colossal-Adventure-Reimagination/commit/f59c413550dd3566e63af0c98a8df17a96359768),
published on 2026-10-21. Verified evidence for those committed bytes:

- 658 files published; 657 entries in `PUBLICATION_MANIFEST.sha256`.
- Manifest SHA-256:
  `06df94326fcdffc53df2d5c7ad3d9866a353331fc4fd08535c4356c863a7eda5`.
- Zero manifest content or inventory discrepancies before publication.
- Deterministic YAML-to-JSON export: `PASS`.
- Godot 4.7.2 import: `PASS`.
- Headless suite: `PASS — 400 checks`.
- Automated contact sheet: `PASS — 11 scenes`.
- Local `HEAD`, `origin/main`, and the remote `main` reference matched after
  publication; anonymous HTTP access to the commit returned status 200.

This document and the associated change record were created after that commit.
They are current working-tree documentation, not contents of the frozen initial
baseline. See the retrospective
[publication record](changes/initial_public_baseline/CHANGE.md).

## CLOSED / VERIFIED

- The public baseline was prepared, licensed, published, and verified.
- The publishable repository is separate from the private research workspace;
  excluded research material was not published.
- Distributed Open Adventure sources and other third-party materials have a
  documented license and provenance inventory.
- Chapter 01, “El Mundo de la Superficie”, is playable in Godot 4.7.2 within
  the boundaries described by the
  [chapter README](../07_godot_open_adventure/README.md).
- `06_reconstruccion_drawio/Open_Adventure.yaml` exports deterministically to
  the Godot dataset.
- The headless suite and integrated verification script passed for the public
  baseline.
- The debug overlay is implemented and covered by focused checks: `Tab`
  toggles the composition, parser state and map camera state persist, observed
  transitions follow interpreter state, and debug navigation is read-only.
- GUT 9.7.1 is included and activated as a Godot editor plugin. It does not
  run or replace the existing 400-check suite.
- The CAR-QOL-001 terminal focus correction is closed after manual validation;
  the current suite passes 448 checks. The maximized window mode is accepted
  provisionally for this cut.
- CAR-AUTO-001 is implemented and validated for its authorized tooling and
  documents: the finalizer self-test passed 9 internal checks, the Drive-sync
  self-test passed 21 internal checks, and the committed snapshot was synced
  and hash-verified. These are tooling checks, not Godot checks.
- CAR-AUTO-001 permits local commits only for expressly authorized CAR cuts,
  followed by non-destructive synchronization of tracked files to Drive. It
  never authorizes automatic push; local `origin/main` is not live remote evidence.
- CAR-CORE-001 historical runtime-dependency Decision Gate is complete. It
  concludes that a full simulation graph can remain separate from the playable
  subset; this is an architectural finding, not an implementation.
- CAR-CORE-001 CUT A: `CLOSED / PASS`. The existing dataset now contains a
  separate, unconsumed `simulation_graph`: 185 source-ordered location IDs,
  623 travel records and six original dwarf/pirate start positions. All previous
  playable fields remain identical to the pre-cut contract. Ten Python contract
  tests and 12 Godot isolation checks passed; the unchanged game suite passes
  448 checks. Runtime consumption and CH_02 remain outside this cut. See the
  [CUT A record](changes/car_core_001_cut_a_global_data_contract/CHANGE.md).
- CAR-CORE-001 CUT B: `CLOSED / PASS` for the authorized player travel cycle.
  Source-ordered rules, automatic HERE cascades, oldloc/oldlc2, BACK and input
  turns are implemented. Special 1/2 paths are verified in isolated source
  fixtures; special 3 and death stop at explicitly typed pending dependencies,
  without implementing the global object/actor or reincarnation subsystems.
  Verification: 54 focused travel checks, 448 game checks, 10 Python CUT A tests
  and 12 isolation checks passed. SEWER now returns automatically to BUILDING;
  LOOK and rejected nonempty commands consume an input turn. CH_02 and the
  simulation graph remain isolated. See the
  [CUT B record](changes/car_core_001_cut_b_historical_travel_cycle/CHANGE.md).
- CAR-CORE-001 CUT C: `CLOSED / PASS` for historical darkness, lamp and
  battery lifecycle. `LIT` plus lamp state/place controls room and object
  visibility; accepted inputs consume lamp energy once before execution;
  warnings, automatic fresh-battery replacement and exhaustion use the source
  constants 330/30/2500. `wzdark`, LOOK exemption and a reproducible 35-percent
  pit-fall check are implemented. Lethal falls stop at typed `DEATH_PENDING`;
  no croak, reincarnation, score or inventory-loss behavior is included.
  Verification: 61 focused CUT C checks, 54 CUT B, 448 game checks, 10 Python
  CUT A tests and 12 isolation checks passed; the complete verifier passed.
  CH_02 and the simulation graph remain isolated. See the
  [CUT C record](changes/car_core_001_cut_c_darkness_lamp_batteries/CHANGE.md).
- CAR-CORE-001 CUT D: `CLOSED / PASS` for historical death and
  reincarnation. Typed deaths from CUT B/C now enter one explicit dialogue
  state, preserve their diagnosis, count once and suspend normal commands.
  The three YAML obituaries, two permitted reincarnations, closing-cave fixture,
  historical inventory/lamp placement, BUILDING return and 30/20/10/0 survival
  score are verified. Obituaries live in a separate static
  `historical_runtime` projection; the playable-contract hash remains intact.
  Verification: 34 focused CUT D checks, 61 CUT C, 54 CUT B, 448 game checks,
  10 Python CUT A tests and 12 isolation checks passed; the complete verifier
  passed. CH_02 and actor simulation remain closed. See the
  [CUT D record](changes/car_core_001_cut_d_historical_death_reincarnation/CHANGE.md).
- CAR-ART-001 is `CLOSED / DECISION RECORDED`: the human selected C — Línea
  solar on 2026-10-25. This closes the art-direction gate only;
  conceptual-browser playback remains unverified. Runtime pilot integration
  is tracked separately in CAR-ART-003.
- CAR-ART-002 is `CLOSED / PASS — EXPERIMENTAL PROTOTYPE LOC_START` after human
  visual acceptance on 2026-10-25. That closure covered the isolated prototype;
  its later runtime pilot belongs to CAR-ART-003. See the
  [prototype record](changes/car_art_002_vector_drawing_playback_prototype/CHANGE.md).

- CAR-ART-003: `CLOSED / PASS — RUNTIME INTEGRATION PILOT`. Human visual and
  interaction acceptance was granted on 2026-10-25 for baseline
  `bc23adcc3178a81125e632bbf22a1812b0d0cc39`. The accepted pilot integrates progressive
  `LOC_START` into the playable main scene, with illustration → narration →
  navigation graph → exits → command input. Other illustrations retain the
  legacy consumer and TAB retains the debug composition without illustration.
  Verification: 448 unchanged game checks, 66 unchanged prototype checks,
  62 focused headless integration checks and 71 graphics integration checks
  (the extra nine cover eight PNG captures and rendered final/skip equality).
  See the [integration record](changes/car_art_003_runtime_illustration_ui_integration_i/CHANGE.md).

- CAR-ART-004: `CLOSED / PASS — WITH DOCUMENTED EXCEPTION` on 2026-10-25.
  The nine new CH_01 illustrations are `IMPLEMENTED / TECHNICAL PASS / HUMAN
  ACCEPTED`; `LOC_START` retains its prior acceptance and is not counted in the
  nine. `GRATE` was deferred within CAR-ART-004 and is not counted as complete
  in that accepted nine-piece batch. CAR-ART-005 later supplied and received
  acceptance for its closed/open state variants; this resolves the functional
  exception without changing CAR-ART-004's original inventory or history.
  Existing results remain documented: 448 original game checks,
  66 START prototype checks, 62 integration/fallback checks, 455 batch
  headless checks and 582 graphical checks; suites were not rerun for this
  documentary closure. Preparation measured 2.084–3.271 s on the test machine.
- CAR-CORE-002 Decision Gate: `CLOSED / VIABLE WITH CONDITIONS` on 2026-10-25.
  Full historical room reconstruction is verified viable as an inert,
  deterministic structural projection prior to puzzle and actor mechanics.
  See the [Decision Gate record](changes/car_core_002_complete_room_reconstruction_decision_gate/CHANGE.md).
- CAR-CORE-002 / R1: `CLOSED / PASS` on 2026-10-25. The canonical room inventory
  is established as a reproducible reference from authoritative sources: 185
  locations, 623 travel records, 70 objects, 11 editorial chapters (100% coverage,
  0 duplicates, 0 fallback), draw.io visual correspondence, structural dependency
  matrix, 26 unit and negative tests, and zero regressions across existing engine
  and illustration suites. Runtime Godot, `WorldData`, and CH_01 playable
  boundary remain untouched. See the
  [R1 record](changes/car_core_002_r1_canonical_room_inventory/CHANGE.md).
- CAR-CORE-002 / R2: `CLOSED / PASS` on 2026-10-25. The complete historical structural
  projection is generated deterministically and versioned under
  `07_godot_open_adventure/godot/data/structural_world.json`: 185 locations with
  descriptions, flags and ordered outbound travel, 623 travel records, 70 objects,
  11 chapters, 6 dwarf start positions, and static dependency matrix. 34 unit/negative
  tests in `test_structural_projection.py` and 23 Godot headless isolation checks in
  `test_structural_projection_isolation.gd` passed. Playable CH_01 contract
  (`chapter_01_surface.json` digest `a49db669...`) and runtime scripts remain
  untouched. See the
  [R2 record](changes/car_core_002_r2_complete_structural_data_projection/CHANGE.md).
- CAR-CORE-002 / R3: `CLOSED / PASS` on 2026-10-25. The structural loader and
  enabled view are implemented in Godot 4.7.2 via `StructuralCatalog` and
  additive queries in `WorldData`: 185 historical locations, 623 travel records,
  70 objects, 11 chapters and 6 dwarflocs loaded and validated. Exactly 34
  locations (`CH_SURFACE`) are enabled in runtime, while 151 remain inert.
  37 Godot unit/negative/isolation tests passed in `test_structural_loader.gd`.
  Playable CH_01 contract digest (`a49db669...`), `GameState.gd`, `Interpreter.gd`,
  and `CommandParser.gd` remain untouched. See the
  [R3 record](changes/car_core_002_r3_structural_loader_enabled_view/CHANGE.md).
- CAR-CORE-002 / R4: `CLOSED / PASS` on 2026-10-25. Structural validation and
  contract freeze are completed and sealed: `CAR_CORE_002_STRUCTURAL_CONTRACT.md`
  and `CAR_CORE_002_TRACEABILITY_MATRIX.md` formalize the authority chain,
  schema v1, travel precedence, static vs. runtime objects, LOADED vs. ENABLED
  separation, deep defensive copies, fail-closed policy, and R5 compatibility.
  The Godot test suite `test_structural_contract_freeze.gd` verified all 34
  checks with 0 failures. Baseline digests (`a49db669...`, `afa33c88...`,
  `fda199af...`) and functional isolation of CH_01 are fully preserved. See the
  [R4 record](changes/car_core_002_r4_structural_validation_contract_freeze/CHANGE.md).
- CAR-CORE-002 / R5 Decision Gate: `CLOSED / DECISION GATE — VIABLE WITH CONDITIONS`
  on 2026-10-25. The technical navigation audit confirmed that expanding navigation
  beyond CH_01 is viable under Alternative C (subgraph with verified dependencies)
  without breaking R1–R4 contracts. Anti-bypass strictness, English text fallback,
  and isolation of missing mechanics/dwarves are established. See the
  [Decision Gate record](changes/car_core_002_r5_navigation_decision_gate/CHANGE.md) and
  [audit report](changes/car_core_002_r5_navigation_decision_gate/NAVIGATION_AUDIT.md).
- CAR-CORE-002 / R5-PRE: `CLOSED / VERIFIED — R5A READY` on 2026-10-26.
  Historical travel semantics crosscheck against Open Adventure 1.22 C code
  confirmed that Godot's CUT B travel resolver (`Interpreter._select_rule`,
  `_select_from`, `_next_distinct`) faithfully replicates the C algorithm
  (`playermove`, `traveleq`). All 19 differential test scenarios for `LOC_GRATE`
  and `LOC_BELOWGRATE` matched with 100% precision. The `DEPENDENCY_PENDING`
  safeguard prevents uninstantiated objects from falsely triggering fallback rules.
  Dwarves are confirmed inactive before `LOC_MISTHALL` (`DEEP == false`).
  See the [R5-PRE record](changes/car_core_002_r5_pre_historical_travel_semantics_crosscheck/CHANGE.md)
  and [crosscheck report](changes/car_core_002_r5_pre_historical_travel_semantics_crosscheck/HISTORICAL_TRAVEL_CROSSCHECK.md).
- CAR-CORE-002 / R5A: `CLOSED / PASS` on 2026-10-26. Cave mouth pilot
  (`LOC_BELOWGRATE`) is implemented in Godot 4.7.2 via atomic and idempotent
  enablement in `WorldData` from `StructuralCatalog`. Playable world expands
  from 34 to 35 locations (34 `CH_SURFACE` + `LOC_BELOWGRATE`); 150 historical
  locations remain inert. The steel grate unlocks and permits bidirectional
  traversal (`ENTER` / `DOWN` / `OUT` / `UP` / `BACK`) while interior passages
  (`WEST` / `PIT` / `DEBRI`) are strictly blocked as unenabled frontiers. English
  historical descriptions (long and short) are transparently displayed without
  altering the Spanish translation dataset. 51 focused integration checks in
  `test_cave_mouth_pilot.gd` and all 7 `verify.ps1` phases passed cleanly with
  zero regressions on CUT A–D. See the
  [R5A record](changes/car_core_002_r5a_cave_mouth_pilot/CHANGE.md).
- CAR-CORE-002 / R5A-POST: `CLOSED / VERIFIED / RECONCILED` on 2026-10-26.
  Focused test coverage and structural lighting audit resolved the apparent
  metrics reporting discrepancy in R5A (10 vs 11 scenes, 36 vs 62 UI checks,
  19 vs 455 art checks, 10 vs 150 grate checks, 448 -> 459 engine checks).
  Confirmed zero loss of test coverage, zero alterations in `verify.ps1` other
  than adding `test_cave_mouth_pilot.gd` (51 checks), and 1503 total passed
  checks across the full suite (+63 checks net in Godot engine Phase 3: 51 pilot
  + 11 dataset/exits + 1 frontier check; 766 Phase 3 checks total). Provenance of
  `LIT` was cross-checked against Open Adventure 1.22 C source and YAML,
  reconciling exactly 37 LIT rooms out of 185 (31 in CH_SURFACE, 2 in CH_ENTRY,
  3 in CH_REPOSITORY, 1 in CH_ORIENTAL_PLOVER; 148 dark rooms), confirming natural
  sunlight through the grate for `LOC_BELOWGRATE` and absence of artificial
  lighting bleed into dark rooms. Structural enablement in `WorldData` is strictly
  whitelisted and fail-closed. Google Drive sync for commit `fb5b0ad` verified.
  See the [R5A-POST record](changes/car_core_002_r5a_post_coverage_lighting_audit/CHANGE.md).
- CAR-CORE-002 / R5B: `CLOSED / PASS` on 2026-10-26. Hall of Mists Vestibule
  (`CH_ENTRY` Safe Subgraph) is implemented in Godot 4.7.2. Exactly six
  additional locations from `StructuralCatalog` are enabled in runtime:
  `LOC_COBBLE` (LIT=true), `LOC_DEBRIS`, `LOC_AWKWARD`, `LOC_BIRDCHAMBER`,
  `LOC_PITTOP`, and `LOC_CRACK` (forced transitory bounce back to `LOC_PITTOP`).
  Playable world expands from 35 to 41 locations (34 `CH_SURFACE` + 7 `CH_ENTRY`);
  exactly 144 historical locations remain inert. Interior frontiers towards
  `LOC_MISTHALL` remain strictly blocked; downward movement at `LOC_PITTOP` is
  fail-closed via `DEPENDENCY_PENDING` on `NUGGET`. Zero dwarves, zero actors,
  zero new objects (8 functional objects preserved). All 50 focused checks in
  `test_hall_of_mists_vestibule.gd` and 1,552 checks across all 7 `verify.ps1`
  phases passed cleanly with zero regressions on CUT A–D. See the
  [R5B record](changes/car_core_002_r5b_hall_of_mists_vestibule/CHANGE.md).

## ACTIVE

No active implementation cut is recorded.

## PENDING / PROPOSED

These items are not authorized implementation cuts:

- CAR-CORE-002 / R5C — Magic Transit & Word Connections: `PROPOSED / NOT AUTHORIZED`.
  (Enabling `LOC_FOOF1`, `LOC_FOOF2` and bidirectional `XYZZY` transport).
- Human graphical and gameplay-experience review of chapter 01.
- Final artistic polish of `GRATE_OPEN`, accepted provisionally by the human
  in CAR-ART-005 and reserved for the project's final art review.
- Effective integration of project tests with GUT.
- Selection of the next playable cut.
- Expansion beyond chapter 01; chapters 02–11 are not implemented.
- Further UX improvements beyond the recorded CAR-ART-001 direction, subject
  to existing project evidence and a separately approved scope.
- CAR-CORE-001 CUT E — `PROPOSED / NOT AUTHORIZED`: historical dwarf and
  pirate actor state and movement over the isolated simulation graph.
- Final UI polish/resizing, possible hiding of the main graph after development,
  graph legibility at 1280 × 720 and the approximately 1.571 s initial
  preparation cost remain future work. Acceptance of CAR-ART-003 does not
  authorize these changes or open new cuts.
- Replay/revisit policy beyond immediate revisits remains a separate decision.
- CH_02 playable integration remains blocked by the global runtime dependencies
  identified in CAR-CORE-001. Chapters beyond CH_01 are not implemented or
  authorized.

CAR-ART-004's **2.084–3.271 s** preparation time for its nine new illustrations
is a measured limitation from the test machine; it was not optimized in the
closure cut and is not a general performance guarantee. CAR-ART-005 measured
**4.189–4.243 s** initial preparation for its two GRATE variants on the capture
machine; this remains a performance limitation. The inherited static reference
remains available as fallback. The human accepted the variants; visual polish of
`GRATE_OPEN` remains deferred to the project's final art review.

## DEFERRED / OUT OF SCOPE

- Steamworks, achievements, DRM, and external-service integration.
- General migration of the existing suite to GUT.
- Bulk formatting or style normalization.
- Rewriting historical sources or evidence.
- Inclusion of material without verified redistribution rights.

Known style diagnostics, not demonstrated functional regressions:

- `gdlint`: 31 findings.
- `gdformat --check`: 9 files would be reformatted.

## Protected Boundaries

- The Open Adventure YAML is authoritative for historical world data.
- Generated data is regenerated and checked; it is not edited manually.
- Missing transitions, travel rules, or source content are not invented.
- Historical research, reproducible transformations, and original
  reinterpretation remain distinct.
- Third-party licenses, attribution, and provenance must be preserved.
- No agent independently authorizes commits, publication, architecture, or
  scope expansion; those decisions remain human-owned.

## Next Decision Gate

CAR-CORE-002 / R5A is closed with `CLOSED / PASS`.
CAR-CORE-002 / R5A-POST is closed with `CLOSED / VERIFIED / RECONCILED`.
**CAR-CORE-002 / R5B — Hall of Mists Vestibule (`CH_ENTRY` Safe Subgraph): PROPOSED / NOT AUTHORIZED**
is the next dependency cut; it requires explicit human authorization.
CAR-ART-005 is closed with documented follow-up: `GRATE_OPEN` polish remains
pending final artistic review; its accepted state selection and integration are
closed. CAR-CORE-001 CUT A is closed for the global data contract only.
CAR-CORE-001 CUT B is closed within its documented travel/dependency boundary.
CAR-CORE-001 CUT C is closed within its documented darkness/lamp/death-pending
boundary. CAR-CORE-001 CUT D is closed within its documented historical death,
reincarnation and survival-score boundary. **CAR-CORE-001 CUT E — PROPOSED /
NOT AUTHORIZED** is the next dependency cut for actor simulation; it requires
its own explicit authorization.
CH_02 remains blocked for
playable integration until the global travel, forced movement, lighting, death,
and actor dependencies are implemented and verified in authorized cuts.

