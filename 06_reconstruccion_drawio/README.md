# MISSION 001 — Open Adventure Cartography

**Agent:** 007 — RPG Archaeology  
**Mission:** Transform the Open Adventure YAML database into an editable,
multi-page diagrams.net (`.drawio`) document for historical research,
translation, and annotation.

## Workspace layout

```
06_reconstruccion_drawio/
├── Open_Adventure.yaml          # canonical source (unchanged)
├── tools/                       # reusable conversion code
│   ├── oa_parser.py             # YAML → deterministic IR
│   ├── oa_graph.py              # IR → world graph + statistics
│   ├── oa_chapters.py           # editorial chapter assignment
│   ├── oa_drawio.py             # graph → native .drawio XML
│   ├── oa_validate.py           # coverage / integrity / determinism tests
│   ├── oa_schema.py             # SCHEMA_ANALYSIS.md generator
│   └── run_pipeline.py          # end-to-end orchestration
├── output/
│   ├── Open_Adventure_World.drawio   # final editable map
│   └── open_adventure_graph.json     # deterministic intermediate graph
└── reports/
    ├── SCHEMA_ANALYSIS.md       # verified YAML schema
    ├── CHAPTER_PROPOSAL.md      # chapter organization and rationale
    └── VALIDATION_REPORT.md     # coverage and test evidence
```

## Quick start

Requires Python 3.x with PyYAML.

```powershell
# Mission 001 — initial multipage map
python tools/run_pipeline.py

# Mission 002 — compass-oriented V2 map
python tools/run_v2.py
```

## Design principles

- **Source fidelity:** The YAML is never modified. Every location identifier,
  description, travel rule, and condition is preserved.
- **No invented data:** Connections, chapters, and metadata are derived from
  the source. Where inference is required, it is flagged as editorial.
- **Editability:** The `.drawio` file is native diagrams.net XML. Nodes contain
  bilingual metadata fields (`description_en`, `description_es`, etc.) so
  future Spanish translations can be added without overwriting English source
  text.
- **Determinism:** Identical input produces byte-identical output (verified by
  the validation suite).

## Chapter organization

The adventure is split into 11 editorial chapters:

1. Surface World
2. Cave Entry
3. Hall of Mountain King & Twopit
4. Maze (All Alike)
5. Bedquilt & Secret Canyons
6. Oriental Room & Plover Passage
7. Reservoir & Cliff Ascent
8. Repository & Volcano
9. Witt's End & Maze All-Different
10. Y2, Windows & Dusty Room
11. Special & Transient States

See `reports/CHAPTER_PROPOSAL.md` for the full rationale and member lists.

## Validation

The `oa_validate.py` suite checks:

- XML well-formedness
- Page and cell structure
- Complete source location coverage (185 nodes)
- Preservation of chapter assignments
- Round-trip of complete English descriptions
- Edge reference integrity (623 travel rules)
- Deterministic regeneration

Run it standalone:

```powershell
python tools/oa_validate.py
```

## Limitations

- Layout is an initial grid. Humans are expected to rearrange nodes in
  diagrams.net for clarity.
- Cross-page edges are shown as off-page connector markers rather than full
  inter-page hyperlinks (native draw.io hyperlinks between pages are not used).
- Graphical inspection was not performed by an automated renderer; open the
  `.drawio` file in diagrams.net to verify visually.

## Mission 002 — Compass-oriented V2

A second layout pass produced `output/Open_Adventure_World_V2.drawio`:

- Compass-oriented, graph-aware placement (north = up, smaller Y).
- Exit summaries inside each location box.
- Compass legend on every chapter page.
- UP/DOWN vertical edges styled separately from compass N/S.
- Cross-page connectors annotated with destination chapter.
- Pseudo-locations shaded grey for visual distinction.

Run `python tools/run_v2.py` and see `reports/LAYOUT_V2_REPORT.md` for
directional-constraint metrics and the required manual-validation notice.

## License and provenance

Source data: `Open_Adventure.yaml` — BSD-2-Clause, Eric S. Raymond / Open
Adventure project. Generated artifacts preserve this provenance.
