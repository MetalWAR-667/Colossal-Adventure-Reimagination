# CAR-QOL-001 — Terminal Focus Closure

**Status:** `CLOSED / PASS`
**Commit:** pending publication of this record
**Scope:** terminal input continuity only

## Result

`LineEdit.keep_editing_on_text_submit` is enabled so Enter no longer ends the
editing session. The existing deferred focus path remains in place for layout
changes and command handling.

Manual validation passed for normal commands, unknown commands, and empty
lines: the field remains ready for the next command without an extra Enter.
Selection/copy, normal/debug switching, Spanish responses, and the provisionally
maximized window mode remain accepted.

## Verification

With Godot 4.7.2, `tools/verify.ps1` passed export determinism, project import,
the headless suite, and automated scene capture. The suite reports 448 checks:
the previous 445 plus three regression assertions covering the editing property
and `text_submitted` handling for unknown and empty commands.

The historical public baseline remains distinct: its frozen suite reported 400
checks. No parser, YAML, exporter, travel rule, translation, or historical data
was changed by this cut.

## Next gate

`CH_02` remains `PROPOSED / NOT IMPLEMENTED`; no implementation is authorized.
