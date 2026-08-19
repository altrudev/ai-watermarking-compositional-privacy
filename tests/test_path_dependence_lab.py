import unittest

from lab.path_dependence_lab import (
    TRANSFORM_NAMES,
    apply_path,
    run_path_dependence_experiment,
)
from lab.transformation_chain_lab import generate_population, make_artifacts


class PathDependenceLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_path_dependence_experiment(persons=6, seed=41)

    def test_all_permutations_are_evaluated(self):
        self.assertEqual(self.report["path_count"], 24)

    def test_same_transform_multiset_is_used(self):
        self.assertEqual(set(self.report["transform_multiset"]), set(TRANSFORM_NAMES))
        self.assertTrue(self.report["controlled_conditions"]["same_transform_multiset_every_path"])
        self.assertTrue(self.report["controlled_conditions"]["same_transform_count_every_path"])

    def test_final_metadata_is_identical_across_paths(self):
        self.assertTrue(self.report["controlled_conditions"]["final_metadata_identical_across_paths"])
        self.assertEqual(self.report["controlled_conditions"]["final_metadata_signature_count"], 1)

    def test_all_paths_remove_simulated_provenance(self):
        self.assertTrue(self.report["controlled_conditions"]["all_paths_remove_provider_and_watermark"])

    def test_order_produces_distinct_final_artifacts(self):
        self.assertGreater(self.report["unique_final_artifact_digests"], 1)

    def test_path_dependence_is_measured_not_assumed(self):
        spread = self.report["person_top1"]["spread"]
        self.assertGreaterEqual(spread, 0.0)
        self.assertIn(self.report["claim"]["status"], {"path_dependent", "not_established"})

    def test_best_and_worst_paths_use_same_transform_set(self):
        best = self.report["best_path"]["path"]
        worst = self.report["worst_path"]["path"]
        self.assertEqual(set(best), set(worst))
        self.assertEqual(len(best), len(TRANSFORM_NAMES))
        self.assertEqual(len(worst), len(TRANSFORM_NAMES))

    def test_pairwise_order_effects_cover_every_pair(self):
        self.assertEqual(len(self.report["pairwise_order_effects"]), 6)

    def test_utility_is_recorded_for_every_path(self):
        for row in self.report["paths"]:
            self.assertIn("semantic_retention", row["utility"])
            self.assertIn("content_word_retention", row["utility"])
            self.assertIn("length_ratio", row["utility"])

    def test_invalid_path_fails_closed(self):
        population = generate_population(persons=2, seed=41)
        artifacts = make_artifacts(population)
        with self.assertRaises(ValueError):
            apply_path(artifacts, ("paraphrase", "summarize"))

    def test_claim_boundary_is_not_universal_anonymity(self):
        self.assertIn("Synthetic identities", self.report["claim"]["boundary"])
        self.assertNotIn("proof of anonymity", self.report["claim"]["statement"].lower())


if __name__ == "__main__":
    unittest.main()
