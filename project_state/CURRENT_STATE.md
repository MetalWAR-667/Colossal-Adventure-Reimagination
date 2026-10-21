# Current State — Colossal Adventure: Reimagination

**Document status:** `REVIEW`  
**Documentation task:** `CAR-DOC-001` — implemented, pending human review  
**Observed baseline:** `main` at `f59c413550dd3566e63af0c98a8df17a96359768`

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

## ACTIVE

- `CAR-DOC-001`: initial project-state documentation is implemented and awaits
  human review. No technical implementation workstream is recorded as active.

## PENDING / PROPOSED

These items are not authorized implementation cuts:

- Human graphical and gameplay-experience review of chapter 01.
- Effective integration of project tests with GUT.
- Selection of the next playable cut.
- Expansion beyond chapter 01; chapters 02–11 are not implemented.
- UX and art-direction improvements, subject to the existing project evidence
  and a separately approved scope.

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

**PROPOSED / NOT AUTHORIZED:** perform the human review of chapter 01, then
prioritize one small next cut using that evidence. This proposal does not select
chapter 02 or authorize implementation.

