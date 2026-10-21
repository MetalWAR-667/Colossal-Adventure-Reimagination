# Schema Analysis — Open Adventure YAML

## Source provenance
- **File:** `G:\Mi unidad\RPG_Archaeology_IF\06_reconstruccion_drawio\Open_Adventure.yaml`
- **License:** BSD-2-Clause (see source header)
- **Canonical author:** Eric S. Raymond / Open Adventure project

## Top-level sections
| Section | Records |
|---------|---------|
| motions | 76 |
| hints | 10 |
| locations | 185 |
| arbitrary_messages | 213 |
| classes | 11 |
| turn_thresholds | 4 |
| objects | 70 |
| obituaries | 3 |
| actions | 58 |
| dwarflocs | 6 |

## Location schema
Every location record contains:
- `source_id` — stable identifier (e.g. `LOC_START`).
- `description.long` — full English room description (may be `null`).
- `description.short` — brief description shown on revisits (may be `null`).
- `description.maptag` — grapher-only tag (may be `null`).
- `conditions` — boolean flags (LIT, DEEP, FOREST, NOBACK, NOARRR, FLUID, OILY, ALLALIKE, ALLDIFFERENT, ABOVE, etc.).
- `sound` — ambient sound label (optional).
- `loud` — whether object sounds are drowned out (optional).
- `hints` — references to hint records (optional).
- `travel` — ordered list of movement rules.

## Condition flags observed
| Flag | Locations |
|------|-----------|
| ABOVE | 11 |
| ALLALIKE | 27 |
| ALLDIFFERENT | 12 |
| DEEP | 144 |
| FLUID | 10 |
| FOREST | 22 |
| LIT | 37 |
| NOARRR | 18 |
| NOBACK | 50 |
| OILY | 1 |

## Travel rule actions
| Action type | Rules |
|-------------|-------|
| goto | 583 |
| speak | 34 |
| special | 6 |

## Conditional travel types
| Condition type | Rules |
|----------------|-------|
| carry | 7 |
| nodwarves | 1 |
| not | 25 |
| probability | 12 |
| with | 4 |

## Classification of source records
- **Total location records:** 185
- **Playable rooms:** 162
- **Special / auxiliary records:** 23

The 23 special/auxiliary records are broken down as:
- **Null location:** `LOC_NOWHERE`
- **Death pseudo-rooms:** `LOC_NECKBROKE`, `LOC_NOMAKE`, `LOC_GRUESOME`, `LOC_FOOTSLIP`
- **Transient message states:** `LOC_DOME`, `LOC_SNAKEBLOCK`, `LOC_BUILDING1`, `LOC_NOCLIMB`, `LOC_PLANTTOP`, `LOC_CLIMBSTALK`, `LOC_CRACK`, `LOC_PARALLEL1`, `LOC_PARALLEL2`, `LOC_BADDIRECTION`, `LOC_SEWER`
- **Magic teleport destinations:** `LOC_FOOF1` … `LOC_FOOF6`

### Special/auxiliary locations
| Source ID | Category | Long description |
|-----------|----------|------------------|
| `LOC_BADDIRECTION` | no_input_transient | There is no way to go that direction. |
| `LOC_BUILDING1` | no_input_transient | (none) |
| `LOC_CLIFFTOP` | no_input_transient | Just as you reach the top, your foot slips on a loose rock and you make one last |
| `LOC_CLIMBSTALK` | no_input_transient | You clamber up the plant and scurry through the hole at the top. |
| `LOC_CRACK` | no_input_transient | The crack is far too small for you to follow.  At its widest it is barely wide e |
| `LOC_DOME` | no_input_transient | The dome is unclimbable. |
| `LOC_FOOF1` | magic_teleport | >>Foof!<< |
| `LOC_FOOF2` | magic_teleport | >>Foof!<< |
| `LOC_FOOF3` | magic_teleport | >>Foof!<< |
| `LOC_FOOF4` | magic_teleport | >>Foof!<< |
| `LOC_FOOF5` | magic_teleport | >>Foof!<< |
| `LOC_FOOF6` | magic_teleport | >>Foof!<< |
| `LOC_FOOTSLIP` | death_state | Just as you reach the top, your foot slips on a loose rock and you tumble severa |
| `LOC_GRUESOME` | death_state | There is now one more gruesome aspect to the spectacular vista. |
| `LOC_NECKBROKE` | death_state | You are at the bottom of the pit with a broken neck. |
| `LOC_NOCLIMB` | no_input_transient | There is nothing here to climb.  Use "up" or "out" to leave the pit. |
| `LOC_NOMAKE` | death_state | You didn't make it. |
| `LOC_NOWHERE` | null | (none) |
| `LOC_PARALLEL1` | no_input_transient | You have crawled through a very low wide passage parallel to and north of the Ha |
| `LOC_PARALLEL2` | no_input_transient | You have crawled through a very low wide passage parallel to and north of the Ha |
| `LOC_PLANTTOP` | no_input_transient | You have climbed up the plant and out of the pit. |
| `LOC_SEWER` | no_input_transient | The stream flows out through a pair of 1 foot diameter sewer pipes. It would be  |
| `LOC_SNAKEBLOCK` | no_input_transient | You can't get by the snake. |

## Motion vocabulary (76 symbols)
| Symbol | Words | oldstyle |
|--------|-------|----------|
| MOT_0 |  | True |
| HERE |  | True |
| MOT_2 | road, hill | True |
| ENTER | enter | True |
| MOT_4 | upstr | True |
| MOT_5 | downs | True |
| MOT_6 | fores | True |
| FORWARD | forwa, conti, onwar | True |
| BACK | back, retur, retre | True |
| MOT_9 | valle | True |
| MOT_10 | stair | True |
| OUTSIDE | out, outsi, exit, leave | True |
| MOT_12 | build, house | True |
| MOT_13 | gully | True |
| STREAM | strea | True |
| MOT_15 | fork | True |
| MOT_16 | bed | True |
| CRAWL | crawl | True |
| MOT_18 | cobbl | True |
| INSIDE | inwar, insid, in | True |
| MOT_20 | surfa | True |
| NUL | null, nowhe | True |
| MOT_22 | dark | True |
| MOT_23 | passa, tunne | True |
| MOT_24 | low | True |
| MOT_25 | canyo | True |
| MOT_26 | awkwa | True |
| MOT_27 | giant | True |
| MOT_28 | view | True |
| UP | upwar, up, u, above, ascen | True |
| DOWN | d, downw, down, desce | True |
| MOT_31 | pit | True |
| MOT_32 | outdo | True |
| MOT_33 | crack | True |
| MOT_34 | steps | True |
| MOT_35 | dome | True |
| LEFT | left | True |
| RIGHT | right | True |
| MOT_38 | hall | True |
| MOT_39 | jump | True |
| MOT_40 | barre | True |
| MOT_41 | over | True |
| MOT_42 | acros | True |
| EAST | east, e | True |
| WEST | west, w | True |
| NORTH | north, n | True |
| SOUTH | south, s | True |
| NE | ne | True |
| SE | se | True |
| SW | sw | True |
| NW | nw | True |
| MOT_51 | debri | True |
| MOT_52 | hole | True |
| MOT_53 | wall | True |
| MOT_54 | broke | True |
| MOT_55 | y2 | True |
| MOT_56 | climb | True |
| LOOK | l, x, look, exami, touch, descr | False |
| MOT_58 | floor | True |
| MOT_59 | room | True |
| MOT_60 | slit | True |
| MOT_61 | slab, slabr | True |
| XYZZY | xyzzy | True |
| DEPRESSION | depre | True |
| ENTRANCE | entra | True |
| PLUGH | plugh | True |
| MOT_66 | secre | True |
| CAVE | cave | True |
| CROSS | cross | True |
| BEDQUILT | bedqu | True |
| PLOVER | plove | True |
| ORIENTAL | orien | True |
| CAVERN | caver | True |
| SHELLROOM | shell | True |
| RESERVOIR | reser | True |
| OFFICE | main, offic | True |

## Object schema
Each object record may contain:
- `source_id` — symbolic name (some are `OBJ_*`).
- `words` — parser vocabulary.
- `inventory` — inventory description.
- `locations` — one or two start locations (may be `LOC_NOWHERE`).
- `states` — state labels for condition tests.
- `descriptions` / `changes` / `sounds` / `texts` — state-dependent strings.
- `immovable` and `treasure` flags.

**Treasure objects:** 20
**Immovable objects:** 33

## Notes and ambiguities
- The source explicitly warns that numeric IDs should not be assumed; the count is exactly 185 location records.
- Empty `long` descriptions occur only for pseudo-locations (`LOC_NOWHERE`, some transient states).
- `travel` rules are evaluated in source order; conditional rules must be preserved exactly.
- Motion word symbols like `MOT_2` have no human-readable heading in the source and are represented by their first listed synonym.
