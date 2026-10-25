#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""
Unit and regression test suite for CAR-CORE-002 / R1 Canonical Room Inventory.

Validates the 20 required focal checks and negative fixture tests:
 1. Exactly 185 historical locations
 2. Exactly 623 travel records
 3. Exactly 70 object entries
 4. Exactly 11 editorial chapters
 5. Complete editorial chapter coverage (100%)
 6. Zero chapter assignment duplicates
 7. Zero fallback chapter assignments
 8. Complete draw.io correspondence (185 nodes, exact pages & geometry)
 9. Preservation of original travel rule ordering
10. Preservation of travel destination types (goto: 583, speak: 34, special: 6)
11. Preservation of travel condition types & parameters (always: 574, not: 25, pct: 12, carry: 7, with: 4, nodwarves: 1)
12. Explicit resolution / classification of references
13. Preservation of object source indices (0..69)
14. Preservation of multiple locations (11 objects)
15. Preservation of initially absent / NOWHERE objects (18 objects)
16. Preservation of multi-state objects (26 objects)
17. Correct identification of treasures (20 treasures)
18. Structural role classification (162 ordinary, 13 special, 5 transient, 4 lethal, 1 null, 22 forced)
19. Deterministic export round-trip
20. Comparison between regenerated in-memory data and committed manifests

Negative tests (isolated fixtures):
- Duplicate location ID rejection
- Unknown travel destination rejection
- Invalid editorial chapter assignment rejection
- Duplicate object index rejection
- Reordered travel rule detection
- Missing location in draw.io detection
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
from typing import Any
import unittest
import xml.etree.ElementTree as ET
import yaml

import oa_canonical_inventory as inv

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent.parent
CANONICAL_DIR = TOOLS_DIR.parent / "canonical_inventory"


def _to_clean_primitives(val: Any) -> Any:
    """Recursively convert tuples to lists for clean YAML safe_dump."""
    if isinstance(val, tuple):
        return [_to_clean_primitives(x) for x in val]
    if isinstance(val, list):
        return [_to_clean_primitives(x) for x in val]
    if isinstance(val, dict):
        return {k: _to_clean_primitives(v) for k, v in val.items()}
    return val


def _dump_clean_yaml(data: Any, path: Path) -> None:
    clean = _to_clean_primitives(data)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(clean, f, sort_keys=False)


class CanonicalInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = inv.build_canonical_inventory()
        cls.manifest = cls.data["manifest"]
        cls.locations_doc = cls.data["locations"]
        cls.travel_doc = cls.data["travel"]
        cls.objects_doc = cls.data["objects"]
        cls.chapters_doc = cls.data["chapters"]
        cls.structural_deps = cls.data["structural_dependencies"]

        with open(inv.YAML_PATH, "r", encoding="utf-8") as f:
            cls.raw_yaml = yaml.safe_load(f)

    # 1. Exactly 185 locations
    def test_01_exactly_185_locations(self):
        self.assertEqual(len(self.locations_doc["locations"]), 185)
        self.assertEqual(self.locations_doc["location_count"], 185)
        self.assertEqual(self.manifest["canonical_counts"]["locations"], 185)
        self.assertEqual(len(self.raw_yaml["locations"]), 185)

    # 2. Exactly 623 travel records
    def test_02_exactly_623_travel_records(self):
        self.assertEqual(len(self.travel_doc["records"]), 623)
        self.assertEqual(self.travel_doc["travel_record_count"], 623)
        self.assertEqual(self.manifest["canonical_counts"]["travel_records"], 623)
        raw_count = sum(len((s or {}).get("travel") or []) for _, s in self.raw_yaml["locations"])
        self.assertEqual(raw_count, 623)

    # 3. Exactly 70 object entries
    def test_03_exactly_70_objects(self):
        self.assertEqual(len(self.objects_doc["objects"]), 70)
        self.assertEqual(self.objects_doc["object_count"], 70)
        self.assertEqual(self.manifest["canonical_counts"]["objects"], 70)
        self.assertEqual(len(self.raw_yaml["objects"]), 70)

    # 4. Exactly 11 editorial chapters
    def test_04_exactly_11_chapters(self):
        self.assertEqual(len(self.chapters_doc["chapters"]), 11)
        self.assertEqual(self.chapters_doc["chapter_count"], 11)
        self.assertEqual(self.manifest["canonical_counts"]["chapters"], 11)
        expected_chapters = [
            "CH_SURFACE",
            "CH_ENTRY",
            "CH_CENTRAL",
            "CH_MAZE_ALIKE",
            "CH_BEDQUILT",
            "CH_ORIENTAL_PLOVER",
            "CH_RESERVOIR",
            "CH_REPOSITORY",
            "CH_WITT_DIFFERENT",
            "CH_Y2_WINDOWS",
            "CH_SPECIAL",
        ]
        self.assertEqual([c["id"] for c in self.chapters_doc["chapters"]], expected_chapters)

    # 5. Complete editorial chapter coverage (100% of 185 locations)
    def test_05_complete_editorial_chapter_coverage(self):
        covered_locs = set()
        expected_counts = {
            "CH_SURFACE": 34,
            "CH_ENTRY": 12,
            "CH_CENTRAL": 18,
            "CH_MAZE_ALIKE": 33,
            "CH_BEDQUILT": 17,
            "CH_ORIENTAL_PLOVER": 12,
            "CH_RESERVOIR": 12,
            "CH_REPOSITORY": 13,
            "CH_WITT_DIFFERENT": 18,
            "CH_Y2_WINDOWS": 9,
            "CH_SPECIAL": 7,
        }
        for ch in self.chapters_doc["chapters"]:
            cid = ch["id"]
            self.assertEqual(ch["member_count"], expected_counts[cid], f"Count mismatch in {cid}")
            self.assertEqual(len(ch["members"]), expected_counts[cid])
            covered_locs.update(ch["members"])

        self.assertEqual(len(covered_locs), 185)
        all_yaml_locs = {n for n, _ in self.raw_yaml["locations"]}
        self.assertEqual(covered_locs, all_yaml_locs)

    # 6. Zero chapter assignment duplicates
    def test_06_zero_chapter_duplicates(self):
        seen = set()
        duplicates = set()
        for ch in self.chapters_doc["chapters"]:
            for m in ch["members"]:
                if m in seen:
                    duplicates.add(m)
                seen.add(m)
        self.assertEqual(len(duplicates), 0, f"Duplicate assignments: {duplicates}")

    # 7. Zero fallback chapter assignments
    def test_07_zero_fallback_assignments(self):
        from oa_chapters import PATTERN_ASSIGNMENTS, FOOF_TARGETS, _build_reverse_lookup
        lookup = _build_reverse_lookup(PATTERN_ASSIGNMENTS)
        for foof, dest in FOOF_TARGETS.items():
            if foof not in lookup and dest in lookup:
                lookup[foof] = lookup[dest]

        for name, _ in self.raw_yaml["locations"]:
            self.assertIn(name, lookup, f"Location {name} relied on fallback assignment")

    # 8. Complete draw.io correspondence
    def test_08_complete_drawio_correspondence(self):
        all_yaml_locs = [n for n, _ in self.raw_yaml["locations"]]
        for loc in self.locations_doc["locations"]:
            dmeta = loc["drawio"]
            self.assertIn(loc["id"], dmeta["label"])
            self.assertEqual(loc["chapter_id"], dmeta["page_id"])
            self.assertIsInstance(dmeta["x"], float)
            self.assertIsInstance(dmeta["y"], float)
            self.assertGreater(dmeta["width"], 0)
            self.assertGreater(dmeta["height"], 0)
            self.assertTrue(bool(dmeta["cell_id"]))
        self.assertEqual([l["id"] for l in self.locations_doc["locations"]], all_yaml_locs)

    # 9. Preservation of original travel rule ordering
    def test_09_preservation_of_travel_order(self):
        global_idx = 0
        for loc_idx, (name, spec) in enumerate(self.raw_yaml["locations"]):
            rules = (spec or {}).get("travel") or []
            loc_record = self.locations_doc["locations"][loc_idx]
            self.assertEqual(loc_record["id"], name)
            self.assertEqual(loc_record["outbound_travel_count"], len(rules))

            for rule_idx, rule in enumerate(rules):
                tr = self.travel_doc["records"][global_idx]
                self.assertEqual(tr["global_travel_index"], global_idx)
                self.assertEqual(tr["source_location_id"], name)
                self.assertEqual(tr["source_location_index"], loc_idx)
                self.assertEqual(tr["source_rule_index"], rule_idx)
                self.assertEqual(tr["verbs"], rule.get("verbs") or [])
                self.assertEqual(tr["action_type"], rule["action"][0])
                self.assertEqual(tr["target"], rule["action"][1])
                self.assertEqual(tr["source_condition"], rule.get("cond"))
                global_idx += 1
        self.assertEqual(global_idx, 623)

    # 10. Preservation of travel destination types
    def test_10_preservation_of_destination_types(self):
        counts = self.travel_doc["action_type_counts"]
        self.assertEqual(counts["goto"], 583)
        self.assertEqual(counts["speak"], 34)
        self.assertEqual(counts["special"], 6)
        self.assertEqual(sum(counts.values()), 623)

        loc_ids = {n for n, _ in self.raw_yaml["locations"]}
        msg_ids = {n for n, _ in self.raw_yaml["arbitrary_messages"]}
        for tr in self.travel_doc["records"]:
            if tr["action_type"] == "goto":
                self.assertEqual(tr["target_resolution"], "location")
                self.assertIn(tr["target"], loc_ids)
                self.assertEqual(tr["destination_location_id"], tr["target"])
                self.assertIsNotNone(tr["destination_chapter_id"])
            elif tr["action_type"] == "speak":
                self.assertEqual(tr["target_resolution"], "message")
                self.assertIn(tr["target"], msg_ids)
                self.assertIsNone(tr["destination_location_id"])
            elif tr["action_type"] == "special":
                self.assertEqual(tr["target_resolution"], "special_handler")
                self.assertIn(tr["target"], (1, 2, 3))
                self.assertIsNone(tr["destination_location_id"])

    # 11. Preservation of travel conditions and parameters
    def test_11_preservation_of_travel_conditions(self):
        counts = self.travel_doc["condition_counts"]
        self.assertEqual(counts["always"], 574)
        self.assertEqual(counts["not"], 25)
        self.assertEqual(counts["pct"], 12)
        self.assertEqual(counts["carry"], 7)
        self.assertEqual(counts["with"], 4)
        self.assertEqual(counts["nodwarves"], 1)
        self.assertEqual(sum(counts.values()), 623)

        for tr in self.travel_doc["records"]:
            raw = tr["source_condition"]
            ctype = tr["condition_type"]
            cond = tr["condition"]
            if raw is None:
                self.assertEqual(ctype, "always")
                self.assertEqual(cond, {"type": "always"})
            elif raw == ["nodwarves"]:
                self.assertEqual(ctype, "nodwarves")
                self.assertEqual(cond, {"type": "no_dwarves"})
                self.assertIn("nodwarves", tr["system_dependencies"])
            elif raw[0] == "pct":
                self.assertEqual(ctype, "pct")
                self.assertEqual(cond, {"type": "pct", "percent": int(raw[1])})
                self.assertIn("probability_rng", tr["system_dependencies"])
            elif raw[0] == "carry":
                self.assertEqual(ctype, "carry")
                self.assertEqual(cond, {"type": "carry", "object": str(raw[1])})
                self.assertIn(str(raw[1]), tr["object_dependencies"])
            elif raw[0] == "with":
                self.assertEqual(ctype, "with")
                self.assertEqual(cond, {"type": "with", "object": str(raw[1])})
                self.assertIn(str(raw[1]), tr["object_dependencies"])
            elif raw[0] == "not":
                self.assertEqual(ctype, "not")
                self.assertEqual(cond, {"type": "not_state", "object": str(raw[1]), "state": str(raw[2])})
                self.assertIn(str(raw[1]), tr["object_dependencies"])
                self.assertEqual(tr["state_dependencies"], [{"object": str(raw[1]), "state": str(raw[2])}])

    # 12. Explicit resolution / classification of references
    def test_12_explicit_resolution_of_references(self):
        cross_chapter_count = self.travel_doc["cross_chapter_count"]
        self.assertEqual(cross_chapter_count, 85)
        self.assertEqual(len(self.structural_deps["cross_chapter_transitions"]["records"]), 85)

        for tr in self.structural_deps["cross_chapter_transitions"]["records"]:
            self.assertNotEqual(tr["source_chapter_id"], tr["destination_chapter_id"])

        special_rules = self.structural_deps["special_travel_destinations"]["rules"]
        self.assertEqual(len(special_rules), 6)
        special_3_rules = [r for r in special_rules if r["special_handler_id"] == 3]
        self.assertEqual(len(special_3_rules), 2)
        for r in special_3_rules:
            self.assertIn("PENDING", r["status"])

    # 13. Preservation of object source indices
    def test_13_preservation_of_object_indices(self):
        for idx, (name, spec) in enumerate(self.raw_yaml["objects"]):
            obj = self.objects_doc["objects"][idx]
            self.assertEqual(obj["source_index"], idx)
            self.assertEqual(obj["id"], name)
            if name == "NO_OBJECT":
                self.assertTrue(obj["is_sentinel"])
                self.assertFalse(obj["is_portable"])
            else:
                self.assertFalse(obj["is_sentinel"])

    # 14. Preservation of multiple locations
    def test_14_preservation_of_multiple_locations(self):
        multi_loc_objs = [o for o in self.objects_doc["objects"] if o["has_multiple_locations"]]
        self.assertEqual(len(multi_loc_objs), 11)
        self.assertEqual(self.objects_doc["counts"]["multiple_locations"], 11)
        for o in multi_loc_objs:
            self.assertGreater(len(o["all_initial_locations"]), 1)
            self.assertEqual(len(o["fixed_locations"]), len(o["all_initial_locations"]) - 1)

    # 15. Preservation of initially absent / NOWHERE objects
    def test_15_preservation_of_absent_objects(self):
        absent_objs = [o for o in self.objects_doc["objects"] if o["is_initially_absent"]]
        self.assertEqual(len(absent_objs), 18)
        self.assertEqual(self.objects_doc["counts"]["initially_absent_or_nowhere"], 18)
        absent_ids = {o["id"] for o in absent_objs}
        expected_absent = {
            "NO_OBJECT", "ROD2", "OYSTER", "DWARF", "KNIFE", "WATER", "OIL",
            "AXE", "OBJ_30", "TROLL2", "MESSAG", "BATTERY", "CAVITY", "BLOOD",
            "CHEST", "PEARL", "JADE", "AMBER"
        }
        self.assertEqual(absent_ids, expected_absent)

    # 16. Preservation of multi-state objects
    def test_16_preservation_of_multi_state_objects(self):
        multi_state_objs = [o for o in self.objects_doc["objects"] if o["has_multiple_states"]]
        self.assertEqual(len(multi_state_objs), 26)
        self.assertEqual(self.objects_doc["counts"]["multiple_states"], 26)
        for o in multi_state_objs:
            self.assertGreater(len(o["states"]), 1)
            self.assertEqual(o["initial_state"], o["states"][0])

    # 17. Correct identification of treasures
    def test_17_treasure_identification(self):
        treasures = [o for o in self.objects_doc["objects"] if o["treasure"]]
        self.assertEqual(len(treasures), 20)
        self.assertEqual(self.objects_doc["counts"]["treasures"], 20)
        yaml_treasures = [name for name, spec in self.raw_yaml["objects"] if (spec or {}).get("treasure")]
        self.assertEqual([o["id"] for o in treasures], yaml_treasures)

    # 18. Structural role classification
    def test_18_structural_role_classification(self):
        role_counts = self.locations_doc["role_counts"]
        self.assertEqual(role_counts["ordinary"], 162)
        self.assertEqual(role_counts["special"], 13)
        self.assertEqual(role_counts["transient"], 5)
        self.assertEqual(role_counts["lethal"], 4)
        self.assertEqual(role_counts["null"], 1)
        self.assertEqual(sum(role_counts.values()), 185)

        forced_count = self.locations_doc["forced_locations_count"]
        self.assertEqual(forced_count, 22)

        # Check special case rooms:
        loc_map = {l["id"]: l for l in self.locations_doc["locations"]}
        self.assertTrue(loc_map["LOC_NOWHERE"]["is_null"])
        self.assertFalse(loc_map["LOC_NOWHERE"]["has_long_description"])
        self.assertIsNone(loc_map["LOC_NOWHERE"]["long_description"])

        self.assertTrue(loc_map["LOC_BUILDING1"]["is_forced"])
        self.assertTrue(loc_map["LOC_BUILDING1"]["has_long_description"])
        self.assertEqual(loc_map["LOC_BUILDING1"]["long_description"], "")

        for lethal_id in ("LOC_NECKBROKE", "LOC_NOMAKE", "LOC_GRUESOME", "LOC_FOOTSLIP"):
            self.assertTrue(loc_map[lethal_id]["is_lethal"], lethal_id)
            self.assertTrue(loc_map[lethal_id]["is_forced"], lethal_id)

    # 19. Deterministic export round-trip
    def test_19_deterministic_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            files1 = inv.export_canonical_inventory(output_dir=tmppath)
            hashes1 = {name: inv.sha256_file(p) for name, p in files1.items()}

            files2 = inv.export_canonical_inventory(output_dir=tmppath)
            hashes2 = {name: inv.sha256_file(p) for name, p in files2.items()}

            self.assertEqual(hashes1, hashes2)

    # 20. Comparison between regenerated in-memory data and committed manifests
    def test_20_committed_manifests_match_regenerated_data(self):
        ok, errors = inv.verify_canonical_inventory(output_dir=CANONICAL_DIR)
        self.assertTrue(ok, f"Verification failed with errors: {errors}")

    # Negative tests (isolated fixtures)
    def test_neg_01_duplicate_location_id_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = copy.deepcopy(self.raw_yaml)
            bad_yaml["locations"].append(["LOC_START", bad_yaml["locations"][1][1]])
            bad_yaml_path = Path(tmpdir) / "bad.yaml"
            _dump_clean_yaml(bad_yaml, bad_yaml_path)
            with self.assertRaises(ValueError):
                inv.build_canonical_inventory(yaml_path=bad_yaml_path)

    def test_neg_02_unknown_travel_destination_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = copy.deepcopy(self.raw_yaml)
            bad_yaml["locations"][1][1]["travel"][0]["action"] = ["goto", "LOC_NON_EXISTENT_XYZ"]
            bad_yaml_path = Path(tmpdir) / "bad.yaml"
            _dump_clean_yaml(bad_yaml, bad_yaml_path)
            with self.assertRaises(ValueError):
                inv.build_canonical_inventory(yaml_path=bad_yaml_path)

    def test_neg_03_invalid_editorial_chapter_assignment_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = copy.deepcopy(self.raw_yaml)
            bad_yaml["locations"][1] = ["LOC_NEW_UNKNOWN", bad_yaml["locations"][1][1]]
            bad_yaml_path = Path(tmpdir) / "bad.yaml"
            _dump_clean_yaml(bad_yaml, bad_yaml_path)
            with self.assertRaises(ValueError):
                inv.build_canonical_inventory(yaml_path=bad_yaml_path)

    def test_neg_04_duplicate_object_index_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = copy.deepcopy(self.raw_yaml)
            bad_yaml["objects"].append(["NEW_KEYS", bad_yaml["objects"][1][1]])
            bad_yaml_path = Path(tmpdir) / "bad.yaml"
            _dump_clean_yaml(bad_yaml, bad_yaml_path)
            with self.assertRaises(ValueError):
                inv.build_canonical_inventory(yaml_path=bad_yaml_path)

    def test_neg_05_reordered_travel_rules_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_yaml = copy.deepcopy(self.raw_yaml)
            rules = bad_yaml["locations"][1][1]["travel"]
            rules[0], rules[1] = rules[1], rules[0]
            bad_yaml_path = Path(tmpdir) / "bad.yaml"
            _dump_clean_yaml(bad_yaml, bad_yaml_path)
            data = inv.build_canonical_inventory(yaml_path=bad_yaml_path)
            self.assertNotEqual(
                data["travel"]["records"][0]["verbs"],
                self.travel_doc["records"][0]["verbs"]
            )

    def test_neg_06_missing_location_in_drawio_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tree = ET.parse(inv.DRAWIO_PATH)
            root = tree.getroot()
            for obj in root.iter("object"):
                if obj.get("source_id") == "LOC_START":
                    obj.attrib.pop("source_id")
                    break
            bad_drawio_path = Path(tmpdir) / "bad.drawio"
            tree.write(bad_drawio_path, encoding="utf-8")
            with self.assertRaises(ValueError):
                inv.build_canonical_inventory(drawio_path=bad_drawio_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
