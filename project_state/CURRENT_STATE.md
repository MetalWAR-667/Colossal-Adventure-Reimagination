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
  Legacy illustrations and fallback remain available. See the
  [production record and gallery](changes/car_art_004_ch01_vector_illustration_production/CHANGE.md).

## ACTIVE

No active implementation cut is recorded.

## PENDING / PROPOSED

These items are not authorized implementation cuts:

- Human graphical and gameplay-experience review of chapter 01.
- Final artistic polish of `GRATE_OPEN`, accepted provisionally by the human
  in CAR-ART-005 and reserved for the project's final art review.
- Effective integration of project tests with GUT.
- Selection of the next playable cut.
- Expansion beyond chapter 01; chapters 02–11 are not implemented.
- Further UX improvements beyond the recorded CAR-ART-001 direction, subject
  to existing project evidence and a separately approved scope.
- CAR-CORE-001 CUT D — `PROPOSED / NOT AUTHORIZED`: consume typed deaths,
  historical croak/reincarnation, lives, inventory placement and score effects.
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

CAR-ART-005 is closed with documented follow-up: `GRATE_OPEN` polish remains
pending final artistic review; its accepted state selection and integration are
closed. CAR-CORE-001 CUT A is closed for the global data contract only.
CAR-CORE-001 CUT B is closed within its documented travel/dependency boundary.
CAR-CORE-001 CUT C is closed within its documented darkness/lamp/death-pending
boundary. **CAR-CORE-001 CUT D — PROPOSED / NOT AUTHORIZED** is the next
decision gate: consuming typed deaths through historical croak/reincarnation,
with its own explicit scope and authorization required.
CH_02 remains blocked for
playable integration until the global travel, forced movement, lighting, death,
and actor dependencies are implemented and verified in authorized cuts.

