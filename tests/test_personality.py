# SPDX-License-Identifier: Apache-2.0
"""Synthetic SPEC-006 tests. No BG2:EE integration or behavioral POC is claimed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from infinity_ai.personality import ALIGNMENT_AXES, HEXACO, generate_new_npc_profile  # noqa: E402


class PersonalityGeneratorTests(unittest.TestCase):
    def make(self, **kwargs):
        data = dict(npc_id="npc:new-guard-1", campaign_id="camp-1",
                    creation_branch_id="main", world_seed="world-seed",
                    npc_origin="CREATED")
        data.update(kwargs)
        return generate_new_npc_profile(**data)

    def test_deterministic_per_identity_branch_campaign_and_seed(self):
        self.assertEqual(self.make(), self.make())
        baseline = self.make()
        for change in ({"npc_id": "npc:new-guard-2"},
                       {"campaign_id": "camp-2"},
                       {"creation_branch_id": "fork"},
                       {"world_seed": "another-seed"}):
            self.assertNotEqual(baseline["seed_fingerprint"],
                                self.make(**change)["seed_fingerprint"])

    def test_profile_has_six_bounded_traits_and_nine_alignment_options(self):
        for i in range(100):
            p = self.make(npc_id=f"npc:generated-{i}")
            self.assertEqual(set(p["hexaco"]), set(HEXACO))
            self.assertTrue(all(0 <= v <= 100 for v in p["hexaco"].values()))
            code = p["alignment_initial"]["code"]
            self.assertIn(code, ALIGNMENT_AXES)
            self.assertEqual((p["alignment_initial"]["ethical"],
                              p["alignment_initial"]["moral"]), ALIGNMENT_AXES[code])
            self.assertEqual(len(set(p["values"])), 3)
            self.assertEqual(len(set(p["drives"])), 2)
            self.assertEqual(len(set(p["vulnerabilities"])), 2)
            self.assertNotIn("biography", p)
            self.assertNotIn("engine_alignment", p)

    def test_alignment_is_weighted_separately_from_hexaco(self):
        for code in ALIGNMENT_AXES:
            weights = {x: (1 if x == code else 0) for x in ALIGNMENT_AXES}
            p = self.make(alignment_weights=weights)
            self.assertEqual(p["alignment_initial"]["code"], code)

    def test_rejects_invalid_distributions(self):
        bad = ({}, {"LG": 1}, {x: 0 for x in ALIGNMENT_AXES},
               {x: (-1 if x == "LG" else 1) for x in ALIGNMENT_AXES},
               {x: (float("nan") if x == "LG" else 1) for x in ALIGNMENT_AXES},
               {x: (True if x == "LG" else 1) for x in ALIGNMENT_AXES})
        for weights in bad:
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                self.make(alignment_weights=weights)

    def test_refuses_canonical_or_unvalidated_identities(self):
        for origin in ("CANONICAL", "CURATED", "", None):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                self.make(npc_origin=origin)
        with self.assertRaises(ValueError):
            self.make(npc_id="invalid")
        with self.assertRaises(ValueError):
            self.make(world_seed="")

    def test_provenance_does_not_pretend_to_observe_game(self):
        p = self.make()
        self.assertEqual(p["alignment_initial"]["provenance"], "GENERATED")
        self.assertEqual(p["origin"], "CREATED")
        self.assertEqual(p["creation_context"]["creation_branch_id"], "main")


if __name__ == "__main__":
    unittest.main()
