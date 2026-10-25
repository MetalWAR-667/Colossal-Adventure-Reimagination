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
- CAR-ART-001 is `CLOSED / DECISION RECORDED`: the human selected C — Línea
  solar on 2026-10-25. This closes the art-direction gate only; production
  renderer integration and conceptual-browser playback remain unverified.

## ACTIVE

- CAR-ART-002: experimental `LOC_START` playback prototype implemented and
  technically verified; `REVIEW / MANUAL_VALIDATION PENDING`. The isolated
  Godot scene is not integrated into the game or its parser. See the
  [prototype record](changes/car_art_002_vector_drawing_playback_prototype/CHANGE.md).

## PENDING / PROPOSED

These items are not authorized implementation cuts:

- Human graphical and gameplay-experience review of chapter 01.
- Effective integration of project tests with GUT.
- Selection of the next playable cut.
- Expansion beyond chapter 01; chapters 02–11 are not implemented.
- Further UX improvements beyond the recorded CAR-ART-001 direction, subject
  to existing project evidence and a separately approved scope.
- CAR-CORE-001 CUT A — proposed global data-contract cut; not authorized.
- Human visual acceptance of CAR-ART-002 and any subsequent production
  integration; the existing 448 game checks and 62 separate prototype checks
  do not replace that acceptance.
- CAR-ART-003 — migration of all eleven CH_01 illustrations; `NOT AUTHORIZED`.
- CH_02 playable integration remains blocked by the global runtime dependencies
  identified in CAR-CORE-001. Chapters beyond CH_01 are not implemented or
  authorized.

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

**REVIEW / MANUAL_VALIDATION PENDING:** the responsible human reviews the
actual CAR-ART-002 `LOC_START` animation, its pace and spatial fill, using the
isolated Godot scene. Production integration and CAR-ART-003 are not authorized
by this record. CAR-CORE-001 CUT A remains
`PROPOSED / NOT AUTHORIZED`: emit and verify the ordered global simulation graph
alongside the playable subset, with no runtime behavior change. CH_02 remains
blocked for playable integration until the global travel, forced movement,
lighting, death, and actor dependencies are implemented and verified in
authorized cuts.

