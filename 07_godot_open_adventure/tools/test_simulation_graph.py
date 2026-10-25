"""CUT A contract tests against canonical YAML; run with python <this file>."""
import copy
import hashlib
import unittest

import oa_export_godot as export


class SimulationGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ir, _, _ = export.load_yaml_source()
        cls.dataset = export.build_dataset()
        cls.graph = cls.dataset["simulation_graph"]

    def test_source_inventory_and_order(self):
        self.assertEqual(len(self.ir["locations"]), 185)
        self.assertEqual(sum(len(s.get("travel") or []) for _, s in self.ir["locations"]), 623)
        self.assertEqual([x["id"] for x in self.graph["locations"]], [n for n, _ in self.ir["locations"]])
        self.assertEqual([x["source_index"] for x in self.graph["locations"]], list(range(185)))
        self.assertEqual((self.graph["location_count"], self.graph["travel_record_count"]), (185, 623))

    def test_every_travel_row_round_trips_in_order(self):
        record_index = 0
        for (name, source), location in zip(self.ir["locations"], self.graph["locations"]):
            rows = source.get("travel") or []
            self.assertEqual(len(rows), len(location["travel"]), name)
            for index, (raw, row) in enumerate(zip(rows, location["travel"])):
                self.assertEqual(row["source_index"], index)
                self.assertEqual(row["source_record_index"], record_index)
                self.assertEqual(row["verbs"], raw["verbs"])
                self.assertEqual([row["action_type"], row["target"]], raw["action"])
                self.assertEqual(row["source_condition"], raw.get("cond"))
                record_index += 1
        self.assertEqual(record_index, 623)

    def test_flags_and_forced_derivation(self):
        forced = []
        for (name, source), loc in zip(self.ir["locations"], self.graph["locations"]):
            self.assertEqual(loc["source_conditions"], source.get("conditions") or {})
            for flag in ("DEEP", "NOARRR"):
                self.assertEqual(loc["flags"][flag], bool((source.get("conditions") or {}).get(flag)))
            # make_dungeon.py expands [] to motion 1 (HERE); init.c checks
            # description pointer, not text length. LOC_BUILDING1 has "".
            rows = source.get("travel") or []
            expected = name != "LOC_NOWHERE" and source["description"]["long"] is not None and bool(rows) and rows[0]["verbs"] == []
            self.assertEqual(loc["flags"]["FORCED"], expected, name)
            if expected:
                forced.append(name)
        self.assertEqual(len(forced), 22)
        self.assertIn("LOC_BUILDING1", forced)

    def test_dwarf_start_positions(self):
        expected = ["LOC_KINGHALL", "LOC_WESTBANK", "LOC_Y2", "LOC_ALIKE3", "LOC_COMPLEX", "LOC_MAZEEND12"]
        self.assertEqual(self.ir["dwarflocs"], expected)
        self.assertEqual(self.graph["dwarflocs"], expected)

    def test_destination_classes(self):
        locations = {n for n, _ in self.ir["locations"]}
        messages = {n for n, _ in self.ir["arbitrary_messages"]}
        counts = {"goto": 0, "speak": 0, "special": 0}
        for loc in self.graph["locations"]:
            for row in loc["travel"]:
                kind, target = row["action_type"], row["target"]
                counts[kind] += 1
                if kind == "goto":
                    self.assertIn(target, locations)
                    self.assertEqual(row["target_resolution"], "location")
                elif kind == "speak":
                    self.assertIn(target, messages)
                    self.assertEqual(row["target_resolution"], "message")
                else:
                    self.assertIs(type(target), int)
                    self.assertIn(target, (1, 2, 3))
                    self.assertEqual(row["target_resolution"], "special_handler")
        self.assertEqual(sum(counts.values()), 623)
        self.assertEqual(counts["special"], 6)

    def test_nodwarves_is_not_a_player_predicate(self):
        marked = [(loc["id"], row) for loc in self.graph["locations"] for row in loc["travel"] if row["nodwarves"]]
        self.assertEqual(len(marked), 1)
        name, row = marked[0]
        self.assertEqual((name, row["target"]), ("LOC_LONGWEST", "LOC_DIFFERENT1"))
        self.assertEqual(row["source_condition"], ["nodwarves"])
        self.assertIsNone(row["condition"])

    def test_ordinary_conditions(self):
        for loc in self.graph["locations"]:
            for row in loc["travel"]:
                raw = row["source_condition"]
                if row["nodwarves"]:
                    continue
                if raw is None:
                    expected = {"type": "always"}
                elif raw[0] == "pct":
                    expected = {"type": "pct", "percent": raw[1]}
                elif raw[0] == "not":
                    expected = {"type": "not_state", "object": raw[1], "state": raw[2]}
                else:
                    expected = {"type": raw[0], "object": raw[1]}
                self.assertEqual(row["condition"], expected)

    def test_playable_contract_matches_pre_cut_bytes(self):
        playable = {k: v for k, v in self.dataset.items() if k != "simulation_graph"}
        # Canonical dump of the complete pre-CUT-A dataset at f8796e6.
        digest = hashlib.sha256(export.dump(playable).encode("utf-8")).hexdigest()
        self.assertEqual(digest, "a49db669ea659a36cfe8a057ec0f511cfb559e8e875a3c3047bf38bb64ffb77f")
        self.assertEqual(len(playable["locations"]), 34)
        self.assertEqual(set(self.graph), {"schema_version", "location_count", "travel_record_count", "locations", "dwarflocs"})
        for loc in self.graph["locations"]:
            self.assertEqual(set(loc), {"id", "source_index", "source_conditions", "flags", "travel"})

    def test_deterministic_export(self):
        self.assertEqual(export.dump(self.dataset).encode(), export.dump(export.build_dataset()).encode())
        # Git may check out text as CRLF; canonical generated bytes stay LF.
        self.assertEqual(export.OUT_PATH.read_text(encoding="utf-8"), export.dump(self.dataset))

    def test_invalid_source_is_rejected(self):
        invalid = copy.deepcopy(self.ir)
        invalid["locations"][1][1]["travel"][0]["action"] = ["goto", "LOC_NOT_IN_SOURCE"]
        with self.assertRaisesRegex(ValueError, "unresolved location"):
            export.build_simulation_graph(invalid)
        invalid = copy.deepcopy(self.ir)
        invalid["locations"][1][1]["travel"].pop()
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            export.build_simulation_graph(invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
