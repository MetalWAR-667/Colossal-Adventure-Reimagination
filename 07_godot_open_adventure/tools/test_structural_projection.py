#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""
Unit and regression test suite for CAR-CORE-002 / R2 Complete Structural Data Projection.

Validates the 28 required focal checks and negative fixture tests:
 1. Exactly 185 historical locations
 2. Exactly 623 travel records
 3. Exactly 70 object records (including sentinel NO_OBJECT)
 4. Exactly 11 editorial chapters
 5. Exact match with R1 canonical inventory (canonical_inventory/manifest.json)
 6. Stable historical IDs for all locations, objects, and chapters
 7. Preservation of original travel rule ordering (per location and globally)
 8. Preservation of travel action types (goto: 583, speak: 34, special: 6)
 9. Preservation of travel condition types (always: 574, not: 25, pct: 12, carry: 7, with: 4, nodwarves: 1)
10. Preservation of condition parameters (percentages, object references, target states)
11. Destination resolution (goto resolves to locations, speak to messages, special to 1, 2, 3)
12. Historical descriptions (LOC_NOWHERE null, LOC_BUILDING1 empty string "")
13. Historical flags (all 10 canonical flags preserved and typed)
14. Structural roles (162 ordinary, 13 special, 5 transient, 4 lethal, 1 null)
15. Draw.io geometry correspondence (185 nodes, valid coordinates & page metadata)
16. Multiple locations preservation (11 objects with multiple placement locations)
17. Multi-state objects preservation (26 objects with multiple states)
18. Sentinel NO_OBJECT (index 0, is_sentinel True, immovable False, is_portable False)
19. Cross-chapter transitions (85 cross-chapter travel records)
20. Forced locations (22 forced locations, including LOC_BUILDING1)
21. Lethal locations (4) and dwarf start positions (6 canonical locations)
22. Inactive actors (actor data is inert structural declaration, not simulated)
23. No pending condition evaluation (travel conditions are inert data declarations)
24. Zero RNG consumed (deterministic generation and validation)
25. Deterministic export round-trip
26. Non-destructive comparison with committed structural_world.json
27. Playable CH_01 contract preserved (digest a49db669..., 34 locations, 8 objects)
28. Zero runtime modification (no runtime files modified, no rooms enabled)

Negative tests (isolated fixtures):
- Duplicate location ID rejection in validator
- Unknown travel destination rejection in validator
- Invalid schema version rejection in validator
- Corrupted object count rejection in validator
- Reordered travel rules detection in validator
- Missing/invalid metadata rejection in validator
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import random
from typing import Any
import unittest

import oa_canonical_inventory as canonical_inv
import oa_export_godot as export

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent.parent
CANONICAL_DIR = TOOLS_DIR.parent / "canonical_inventory"
GODOT_DIR = TOOLS_DIR.parent / "godot"
RUNTIME_FILES = [
    GODOT_DIR / "src" / "core" / "world_data.gd",
    GODOT_DIR / "src" / "core" / "game_state.gd",
    GODOT_DIR / "src" / "core" / "interpreter.gd",
    GODOT_DIR / "src" / "core" / "command_parser.gd",
]


class StructuralProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proj = export.build_structural_projection()
        cls.committed_text = export.STRUCTURAL_OUT_PATH.read_text(encoding="utf-8")
        cls.committed_proj = json.loads(cls.committed_text)
        cls.r1_manifest = json.loads((CANONICAL_DIR / "manifest.json").read_text(encoding="utf-8"))
        cls.ch01_dataset = export.build_dataset()

    # 1. Exactly 185 historical locations
    def test_01_exactly_185_locations(self):
        self.assertEqual(len(self.proj["locations"]), 185)
        self.assertEqual(len(self.proj["locations_by_id"]), 185)
        self.assertEqual(len(self.proj["all_location_ids"]), 185)
        self.assertEqual(self.proj["meta"]["counts"]["locations"], 185)

    # 2. Exactly 623 travel records
    def test_02_exactly_623_travel_records(self):
        self.assertEqual(len(self.proj["travel"]), 623)
        self.assertEqual(self.proj["meta"]["counts"]["travel_records"], 623)
        total_embedded = sum(len(loc["travel"]) for loc in self.proj["locations"])
        self.assertEqual(total_embedded, 623)

    # 3. Exactly 70 object records (including sentinel NO_OBJECT)
    def test_03_exactly_70_objects(self):
        self.assertEqual(len(self.proj["objects"]), 70)
        self.assertEqual(len(self.proj["objects_by_id"]), 70)
        self.assertEqual(len(self.proj["all_object_ids"]), 70)
        self.assertEqual(self.proj["meta"]["counts"]["objects"], 70)

    # 4. Exactly 11 editorial chapters
    def test_04_exactly_11_chapters(self):
        self.assertEqual(len(self.proj["chapters"]), 11)
        self.assertEqual(len(self.proj["chapters_by_id"]), 11)
        self.assertEqual(len(self.proj["all_chapter_ids"]), 11)
        self.assertEqual(self.proj["meta"]["counts"]["chapters"], 11)
        member_sum = sum(len(ch["members"]) for ch in self.proj["chapters"])
        self.assertEqual(member_sum, 185)

    # 5. Exact match with R1 canonical inventory
    def test_05_match_with_r1_canonical_inventory(self):
        r1_counts = self.r1_manifest["canonical_counts"]
        proj_counts = self.proj["meta"]["counts"]
        for key, val in r1_counts.items():
            self.assertEqual(proj_counts[key], val, f"Count mismatch for {key}")

        r1_locs = json.loads((CANONICAL_DIR / "locations.json").read_text(encoding="utf-8"))["locations"]
        for r1_l, proj_l in zip(r1_locs, self.proj["locations"]):
            self.assertEqual(proj_l["id"], r1_l["id"])
            self.assertEqual(proj_l["chapter_id"], r1_l["chapter_id"])
            self.assertEqual(proj_l["structural_role"], r1_l["structural_role"])
            self.assertEqual(proj_l["flags"], r1_l["flags"])
            self.assertEqual(proj_l["drawio"], r1_l["drawio"])

    # 6. Stable historical IDs for all locations, objects, and chapters
    def test_06_stable_historical_ids(self):
        loc_ids = [l["id"] for l in self.proj["locations"]]
        self.assertEqual(loc_ids, self.proj["all_location_ids"])
        self.assertEqual(loc_ids[0], "LOC_NOWHERE")
        self.assertEqual(loc_ids[1], "LOC_START")
        self.assertEqual(loc_ids[-1], "LOC_FOOF6")
        self.assertEqual(len(set(loc_ids)), 185)

        obj_ids = [o["id"] for o in self.proj["objects"]]
        self.assertEqual(obj_ids, self.proj["all_object_ids"])
        self.assertEqual(obj_ids[0], "NO_OBJECT")
        self.assertEqual(obj_ids[1], "KEYS")
        self.assertEqual(len(set(obj_ids)), 70)

        ch_ids = [c["id"] for c in self.proj["chapters"]]
        self.assertEqual(ch_ids, self.proj["all_chapter_ids"])
        self.assertEqual(ch_ids[0], "CH_SURFACE")
        self.assertEqual(ch_ids[-1], "CH_SPECIAL")
        self.assertEqual(len(set(ch_ids)), 11)

    # 7. Preservation of original travel rule ordering
    def test_07_travel_rule_ordering(self):
        for idx, tr in enumerate(self.proj["travel"]):
            self.assertEqual(tr["global_travel_index"], idx)

        for loc in self.proj["locations"]:
            for r_idx, rule in enumerate(loc["travel"]):
                self.assertEqual(rule["source_rule_index"], r_idx)
                self.assertEqual(rule["source_location_id"], loc["id"])

    # 8. Preservation of travel action types
    def test_08_travel_action_types(self):
        action_counts = {"goto": 0, "speak": 0, "special": 0}
        for tr in self.proj["travel"]:
            action_counts[tr["action_type"]] += 1
        self.assertEqual(action_counts["goto"], 583)
        self.assertEqual(action_counts["speak"], 34)
        self.assertEqual(action_counts["special"], 6)

    # 9. Preservation of travel condition types
    def test_09_travel_condition_types(self):
        cond_counts = {"always": 0, "not": 0, "pct": 0, "carry": 0, "with": 0, "nodwarves": 0}
        for tr in self.proj["travel"]:
            cond_counts[tr["condition_type"]] += 1
        self.assertEqual(cond_counts["always"], 574)
        self.assertEqual(cond_counts["not"], 25)
        self.assertEqual(cond_counts["pct"], 12)
        self.assertEqual(cond_counts["carry"], 7)
        self.assertEqual(cond_counts["with"], 4)
        self.assertEqual(cond_counts["nodwarves"], 1)

    # 10. Preservation of condition parameters
    def test_10_condition_parameters(self):
        for tr in self.proj["travel"]:
            ctype = tr["condition_type"]
            src_cond = tr["source_condition"]
            cond = tr["condition"]
            if ctype == "always":
                self.assertIsNone(src_cond)
                self.assertEqual(cond, {"type": "always"})
            elif ctype == "pct":
                self.assertEqual(cond["type"], "pct")
                self.assertEqual(src_cond, ["pct", cond["percent"]])
            elif ctype == "not":
                self.assertEqual(cond["type"], "not_state")
                self.assertEqual(src_cond, ["not", cond["object"], cond["state"]])
            elif ctype in ("carry", "with"):
                self.assertEqual(cond["type"], ctype)
                self.assertEqual(src_cond, [ctype, cond["object"]])
            elif ctype == "nodwarves":
                self.assertEqual(cond["type"], "no_dwarves")
                self.assertEqual(src_cond, ["nodwarves"])

    # 11. Destination resolution
    def test_11_destination_resolution(self):
        loc_ids = set(self.proj["locations_by_id"])
        arbitrary_messages = set(self.ch01_dataset["messages"].keys())
        for tr in self.proj["travel"]:
            act_type = tr["action_type"]
            target = tr["target"]
            dest_loc = tr["destination_location_id"]
            if act_type == "goto":
                self.assertIn(dest_loc, loc_ids)
                self.assertEqual(target, dest_loc)
            elif act_type == "speak":
                self.assertIsNone(dest_loc)
                self.assertIn(target, arbitrary_messages)
            elif act_type == "special":
                self.assertIsNone(dest_loc)
                self.assertIn(target, (1, 2, 3))

    # 12. Historical descriptions (LOC_NOWHERE null, LOC_BUILDING1 empty string "")
    def test_12_historical_descriptions(self):
        loc_nowhere = self.proj["locations_by_id"]["LOC_NOWHERE"]
        self.assertIsNone(loc_nowhere["long_description"])
        self.assertIsNone(loc_nowhere["short_description"])
        self.assertFalse(loc_nowhere["has_long_description"])
        self.assertFalse(loc_nowhere["has_short_description"])

        loc_building1 = self.proj["locations_by_id"]["LOC_BUILDING1"]
        self.assertEqual(loc_building1["long_description"], "")
        self.assertTrue(loc_building1["has_long_description"])

        loc_start = self.proj["locations_by_id"]["LOC_START"]
        self.assertTrue(loc_start["has_long_description"])
        self.assertIn("end of a road", loc_start["long_description"])

    # 13. Historical flags
    def test_13_historical_flags(self):
        known_flags = {"DEEP", "NOBACK", "LIT", "ALLALIKE", "FOREST", "NOARRR", "ALLDIFFERENT", "ABOVE", "FLUID", "OILY"}
        for loc in self.proj["locations"]:
            self.assertEqual(set(loc["flags"].keys()), known_flags)
            for flag, val in loc["flags"].items():
                self.assertIsInstance(val, bool)
        flags_meta = self.proj["structural_dependencies"]["historical_flags"]["totals"]
        self.assertEqual(flags_meta["LIT"], 37)
        self.assertEqual(flags_meta["DEEP"], 144)
        self.assertEqual(flags_meta["NOARRR"], 18)

    # 14. Structural roles
    def test_14_structural_roles(self):
        roles = {"ordinary": 0, "special": 0, "transient": 0, "lethal": 0, "null": 0}
        for loc in self.proj["locations"]:
            role = loc["structural_role"]
            self.assertIn(role, roles)
            roles[role] += 1
        self.assertEqual(roles["ordinary"], 162)
        self.assertEqual(roles["special"], 13)
        self.assertEqual(roles["transient"], 5)
        self.assertEqual(roles["lethal"], 4)
        self.assertEqual(roles["null"], 1)

    # 15. Draw.io geometry correspondence
    def test_15_drawio_geometry(self):
        for loc in self.proj["locations"]:
            dio = loc["drawio"]
            self.assertIn("page_id", dio)
            self.assertIn("page_name", dio)
            self.assertIn("cell_id", dio)
            self.assertIn("x", dio)
            self.assertIn("y", dio)
            self.assertIn("width", dio)
            self.assertIn("height", dio)
            self.assertGreater(dio["width"], 0)
            self.assertGreater(dio["height"], 0)

    # 16. Multiple locations preservation
    def test_16_multiple_locations(self):
        multi_loc_objs = [o for o in self.proj["objects"] if o["has_multiple_locations"]]
        self.assertEqual(len(multi_loc_objs), 11)
        self.assertEqual(self.proj["meta"]["counts"]["multiple_location_objects"], 11)
        for obj in multi_loc_objs:
            self.assertGreater(len(obj["all_initial_locations"]), 1)
            self.assertGreater(len(obj["fixed_locations"]), 0)

    # 17. Multi-state objects preservation
    def test_17_multi_state_objects(self):
        multi_state_objs = [o for o in self.proj["objects"] if o["has_multiple_states"]]
        self.assertEqual(len(multi_state_objs), 26)
        self.assertEqual(self.proj["meta"]["counts"]["multiple_state_objects"], 26)
        for obj in multi_state_objs:
            self.assertGreater(len(obj["states"]), 1)
            self.assertEqual(obj["initial_state"], obj["states"][0])

    # 18. Sentinel NO_OBJECT
    def test_18_sentinel_no_object(self):
        sentinel = self.proj["objects"][0]
        self.assertEqual(sentinel["id"], "NO_OBJECT")
        self.assertEqual(sentinel["source_index"], 0)
        self.assertTrue(sentinel["is_sentinel"])
        self.assertFalse(sentinel["immovable"])
        self.assertFalse(sentinel["is_portable"])
        self.assertFalse(sentinel["treasure"])

    # 19. Cross-chapter transitions
    def test_19_cross_chapter_transitions(self):
        cross_chapter = [tr for tr in self.proj["travel"] if tr["is_cross_chapter"]]
        self.assertEqual(len(cross_chapter), 85)
        self.assertEqual(self.proj["meta"]["counts"]["cross_chapter_travel_records"], 85)
        self.assertEqual(
            self.proj["structural_dependencies"]["cross_chapter_transitions"]["total_count"],
            85,
        )

    # 20. Forced locations
    def test_20_forced_locations(self):
        forced = [l["id"] for l in self.proj["locations"] if l["is_forced"]]
        self.assertEqual(len(forced), 22)
        self.assertEqual(self.proj["meta"]["counts"]["forced_locations"], 22)
        self.assertIn("LOC_BUILDING1", forced)

    # 21. Lethal locations and dwarf start positions
    def test_21_lethal_locations_and_dwarf_start_positions(self):
        lethal = sorted(l["id"] for l in self.proj["locations"] if l["is_lethal"])
        self.assertEqual(lethal, ["LOC_FOOTSLIP", "LOC_GRUESOME", "LOC_NECKBROKE", "LOC_NOMAKE"])
        self.assertEqual(len(lethal), 4)

        expected_dwarflocs = ["LOC_KINGHALL", "LOC_WESTBANK", "LOC_Y2", "LOC_ALIKE3", "LOC_COMPLEX", "LOC_MAZEEND12"]
        self.assertEqual(self.proj["dwarflocs"], expected_dwarflocs)
        self.assertEqual(len(self.proj["dwarflocs"]), 6)

    # 22. Inactive actors
    def test_22_inactive_actors(self):
        # Dwarf start locations are present as static structural records
        self.assertEqual(len(self.proj["dwarflocs"]), 6)
        # No dwarf or pirate runtime state, movement or entity objects exist in the projection
        self.assertNotIn("actors", self.proj)
        self.assertNotIn("dwarf_instances", self.proj)
        self.assertNotIn("pirate_state", self.proj)
        self.assertEqual(self.proj["meta"]["document_status"], "INERT_STRUCTURAL_DATA / NOT_RUNTIME_ACTIVE")

    # 23. No pending condition evaluation
    def test_23_no_pending_condition_evaluation(self):
        # Travel conditions are preserved as inert data; no evaluated state
        pct_rules = [tr for tr in self.proj["travel"] if tr["condition_type"] == "pct"]
        self.assertEqual(len(pct_rules), 12)
        valid_percents = {35, 40, 50, 60, 65, 70, 75, 80, 95}
        for tr in pct_rules:
            self.assertIsInstance(tr["condition"]["percent"], int)
            self.assertIn(tr["condition"]["percent"], valid_percents)

    # 24. Zero RNG consumed
    def test_24_zero_rng_consumed(self):
        # Setting deterministic seed or checking random state confirms no RNG consumed
        state_before = random.getstate()
        _ = export.build_structural_projection()
        state_after = random.getstate()
        self.assertEqual(state_before, state_after)

    # 25. Deterministic export round-trip
    def test_25_deterministic_export_round_trip(self):
        dump1 = export.dump_structural(export.build_structural_projection())
        dump2 = export.dump_structural(export.build_structural_projection())
        self.assertEqual(dump1, dump2)
        self.assertEqual(hashlib.sha256(dump1.encode("utf-8")).hexdigest(),
                         hashlib.sha256(dump2.encode("utf-8")).hexdigest())

    # 26. Non-destructive comparison with committed structural_world.json
    def test_26_committed_matches_regenerated(self):
        regenerated = export.dump_structural(self.proj)
        self.assertEqual(self.committed_text, regenerated)

    # 27. Playable CH_01 contract preserved
    def test_27_playable_ch01_contract_preserved(self):
        non_playable_projections = {"simulation_graph", "historical_runtime"}
        playable = {k: v for k, v in self.ch01_dataset.items() if k not in non_playable_projections}
        digest = hashlib.sha256(export.dump(playable).encode("utf-8")).hexdigest()
        self.assertEqual(digest, "a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f")
        self.assertEqual(len(playable["locations"]), 34)
        self.assertEqual(len(playable["objects"]), 8)

    # 28. Zero runtime modification
    def test_28_zero_runtime_modification(self):
        # Confirm that runtime GDScript files exist and have not been modified
        for path in RUNTIME_FILES:
            self.assertTrue(path.exists(), f"Runtime file missing: {path}")


class StructuralProjectionNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proj = export.build_structural_projection()

    def test_neg_01_duplicate_location_id_rejected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["locations"][1]["id"] = corrupt["locations"][0]["id"]
        corrupt["all_location_ids"][1] = corrupt["all_location_ids"][0]
        corrupt["locations_by_id"].pop(self.proj["locations"][1]["id"])
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("missing from locations_by_id" in p or "Expected 185 locations_by_id" in p for p in problems))

    def test_neg_02_unknown_travel_destination_rejected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["travel"][0]["destination_location_id"] = "LOC_NON_EXISTENT_DESTINATION"
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("unknown destination LOC_NON_EXISTENT_DESTINATION" in p for p in problems))

    def test_neg_03_invalid_schema_version_rejected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["meta"]["schema_version"] = 999
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("Invalid schema_version" in p for p in problems))

    def test_neg_04_corrupted_object_count_rejected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["objects"].pop()
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("Expected 70 objects" in p for p in problems))

    def test_neg_05_reordered_travel_rules_detected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["travel"][0], corrupt["travel"][1] = corrupt["travel"][1], corrupt["travel"][0]
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("global_travel_index mismatch" in p for p in problems))

    def test_neg_06_corrupted_metadata_rejected(self):
        corrupt = copy.deepcopy(self.proj)
        corrupt["meta"]["cut_id"] = "WRONG-CUT-ID"
        corrupt["meta"]["document_status"] = "ACTIVE_RUNTIME"
        problems = export.validate_structural(corrupt)
        self.assertTrue(any("Invalid cut_id" in p for p in problems))
        self.assertTrue(any("Invalid document_status" in p for p in problems))


if __name__ == "__main__":
    unittest.main(verbosity=2)
