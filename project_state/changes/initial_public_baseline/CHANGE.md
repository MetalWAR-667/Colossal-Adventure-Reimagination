# Initial Public Baseline — Publication & Verification Record

**Status:** `CLOSED / PASS — PUBLICATION`  
**Baseline commit:** `f59c413550dd3566e63af0c98a8df17a96359768`  
**Branch:** `main`  
**Publication date:** 2026-10-21

## Objective

Prepare and publish a clean, traceable, and reproducible public version of
Colossal Adventure: Reimagination without importing excluded private material
or local development tooling.

## Historical Context

The public repository was prepared independently from the research workspace.
Before publication, its inventory, third-party provenance, and license
boundaries were audited. Original work was established as
`GPL-3.0-or-later`; Open Adventure and exceptional third-party files retain the
BSD-2-Clause, CC-BY-4.0, MIT-0, MIT, or SIL OFL terms identified in
[NOTICE.md](../../../NOTICE.md). Local Godot and ripgrep distributions and the
pip-installed GDToolkit environment were classified as local tools rather than
public dependencies. GUT 9.7.1 was included under its own notices and activated
as an editor plugin.

## Published Result

- Full commit:
  [`f59c413550dd3566e63af0c98a8df17a96359768`](https://github.com/MetalWAR-667/Colossal-Adventure-Reimagination/commit/f59c413550dd3566e63af0c98a8df17a96359768).
- Branch: `main`.
- Published files: 658.
- `PUBLICATION_MANIFEST.sha256`: 657 entries.
- Manifest SHA-256:
  `06df94326fcdffc53df2d5c7ad3d9866a353331fc4fd08535c4356c863a7eda5`.
- Manifest discrepancies before publication: 0.
- Local `HEAD`, local `origin/main`, and remote `refs/heads/main` matched after
  the push.
- Anonymous HTTP access to the public commit returned status 200.

## Validation Evidence

The release preparation actually executed and observed:

- `python 07_godot_open_adventure/tools/oa_export_godot.py --check`:
  generated data matched the committed dataset.
- `07_godot_open_adventure/tools/verify.ps1 -Godot <local Godot 4.7.2>` on a
  temporary copy: export check, Godot import, 400-check headless suite, and an
  11-scene contact sheet all passed.
- Manifest validation: 657 entries, zero missing files, zero unexpected files,
  and zero SHA-256 mismatches.
- Candidate review: no local executables or high-confidence credential matches
  in the published set.
- Post-push verification: 658 files in the commit, clean working tree, matching
  local and remote commit IDs, and required license/documentation files present.

These checks do not constitute human graphical or gameplay acceptance. The
older [chapter reconstruction report](../../../07_godot_open_adventure/reports/RECONSTRUCTION_CH01.md)
records an earlier 194-check stage and its own visual inspection; the published
baseline later passed 400 checks, while current project documentation still
keeps human graphical review pending.

## Accepted Exceptions

The owner explicitly accepted only the pre-existing whitespace diagnostics in
the initial staged baseline:

- 265 instances of trailing whitespace.
- 24 instances of a new blank line at end of file.
- 289 total findings.
- 0 findings of any other class.

This was a one-time historical exception. It does not waive future errors or
authorize formatting historical sources, fixtures, contracts, or evidence.

## Scope Exclusions

- Local Godot and ripgrep binaries.
- Private research material.
- Resources with insufficient provenance for redistribution.
- Caches, credentials, and non-redistributable external tools.

The precise publication boundary and license exceptions are recorded in
[NOTICE.md](../../../NOTICE.md) and the root
[README](../../../README.md).

## Residual Risks

- Human graphical and gameplay-experience review remains pending.
- GUT is installed and activated but is not used by the existing suite.
- The recorded style diagnostics remain: 31 `gdlint` findings and 9 files
  reported by `gdformat --check`.
- Steamworks is not integrated and remains a separate pending legal and
  technical decision.

## Closure

The initial public baseline is closed and remains identified by its immutable
commit and manifest hash. This file is a retrospective record created after
publication; it was not present in the initial commit. Creating or later
committing this documentation does not reopen, alter, or replace that baseline.

