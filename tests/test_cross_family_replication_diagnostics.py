import unittest

from lab.cross_family_replication_diagnostics import (
    DIAGNOSTIC_SIGNALS,
    scenario_pairwise_diagnostics,
)
from lab.cross_family_replication_lab import FAMILIES, POLICIES


class CrossFamilyReplicationDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = scenario_pairwise_diagnostics("S1")

    def test_protocol_identity_and_scope(self):
        self.assertEqual(
            self.result["protocol_commit"],
            "786ebb3d097d999e15f72cbfce536e59566206a1",
        )
        self.assertEqual(self.result["research_scope"], "synthetic-only")

    def test_all_declared_families_and_pairs_are_recorded(self):
        self.assertEqual(set(self.result["families"]), set(FAMILIES))
        for family_name, transforms in FAMILIES.items():
            row = self.result["families"][family_name]
            self.assertEqual(row["pair_count"], 6)
            self.assertEqual(set(row["transform_names"]), set(transforms))
            self.assertEqual(len(row["pairs"]), 6)

    def test_pairwise_evidence_contains_predeclared_t2_fields(self):
        self.assertEqual(
            set(DIAGNOSTIC_SIGNALS),
            {"lexical", "semantic", "style", "watermark", "provider", "time"},
        )
        for family in self.result["families"].values():
            for row in family["pairs"].values():
                self.assertIn("final_text_difference_fraction", row)
                self.assertIn("final_metadata_identical", row)
                self.assertEqual(
                    set(row["feature_divergence"]),
                    {"lexical", "semantic", "style"},
                )
                self.assertEqual(set(row["policy_order_effects"]), set(POLICIES))
                self.assertEqual(
                    set(row["single_channel_person_top1_difference"]),
                    set(DIAGNOSTIC_SIGNALS),
                )
                self.assertTrue(row["largest_changed_channels"])
                for channel in row["largest_changed_channels"]:
                    self.assertIn(channel, row["single_channel_person_top1_difference"])
                    self.assertEqual(
                        abs(row["single_channel_person_top1_difference"][channel]),
                        row["largest_absolute_channel_delta"],
                    )

    def test_transforms_do_not_create_metadata_order_difference(self):
        for family in self.result["families"].values():
            for row in family["pairs"].values():
                self.assertTrue(row["final_metadata_identical"])

    def test_feature_divergence_is_bounded(self):
        for family in self.result["families"].values():
            for row in family["pairs"].values():
                for value in row["feature_divergence"].values():
                    self.assertGreaterEqual(value, 0.0)
                    self.assertLessEqual(value, 2.0)


if __name__ == "__main__":
    unittest.main()
