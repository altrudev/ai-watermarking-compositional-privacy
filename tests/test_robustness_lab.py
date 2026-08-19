import unittest

from lab.robustness_lab import (
    POLICIES, _commuting_control, apply_path, generate_population, make_artifacts, path_matrix
)

class RobustnessLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = generate_population(persons=4, seed=41)
        cls.artifacts = make_artifacts(cls.population, seed=7041)

    def test_synthetic_only_population(self):
        self.assertTrue(all(row.person_id.startswith("syn-") for row in self.population))

    def test_population_is_deterministic(self):
        self.assertEqual(self.population, generate_population(persons=4, seed=41))

    def test_path_requires_exact_transform_multiset(self):
        with self.assertRaises(ValueError):
            apply_path(self.artifacts[:8], ("paraphrase", "summarize"))

    def test_path_count_is_all_permutations(self):
        self.assertEqual(path_matrix(persons=4, seed=41, artifact_limit=8)["path_count"], 24)

    def test_metadata_is_controlled_across_paths(self):
        self.assertTrue(path_matrix(persons=4, seed=41, artifact_limit=8)["final_metadata_identical_across_paths"])

    def test_population_change_executes(self):
        small = path_matrix(persons=4, seed=41, artifact_limit=8)
        larger = path_matrix(persons=6, seed=41, artifact_limit=8)
        self.assertNotEqual(small["population_generations"], larger["population_generations"])

    def test_seed_change_executes(self):
        self.assertNotEqual(path_matrix(persons=4, seed=17, artifact_limit=8)["parameters"]["seed"], path_matrix(persons=4, seed=41, artifact_limit=8)["parameters"]["seed"])

    def test_text_length_variants_execute(self):
        self.assertEqual(path_matrix(persons=4, seed=41, sentence_count=3, artifact_limit=8)["parameters"]["sentence_count"], 3)
        self.assertEqual(path_matrix(persons=4, seed=41, sentence_count=9, artifact_limit=8)["parameters"]["sentence_count"], 9)

    def test_strength_variants_execute(self):
        self.assertEqual(path_matrix(persons=4, seed=41, strength=.50, artifact_limit=8)["parameters"]["strength"], .50)

    def test_stochastic_mode_is_reproducible_for_fixed_seed(self):
        left = path_matrix(persons=4, seed=101, stochastic=True, strength=.75, artifact_limit=8)
        right = path_matrix(persons=4, seed=101, stochastic=True, strength=.75, artifact_limit=8)
        self.assertEqual(left, right)

    def test_all_policies_execute(self):
        for policy in POLICIES:
            self.assertEqual(path_matrix(persons=4, seed=41, policy=policy, artifact_limit=8)["parameters"]["policy"], policy)

    def test_canonical_full_reproduces_v04_reference(self):
        result = path_matrix(persons=12, seed=41, artifact_limit=None, artifact_seed=7000)
        self.assertAlmostEqual(result["person_top1"]["minimum"], 0.2569444444444444)
        self.assertAlmostEqual(result["person_top1"]["maximum"], 0.4444444444444444)
        self.assertAlmostEqual(result["person_top1"]["spread"], 0.1875)
        self.assertEqual(result["best_path"]["path"], ["summarize", "model_edit", "translate", "paraphrase"])
        self.assertEqual(result["worst_path"]["path"], ["paraphrase", "translate", "model_edit", "summarize"])

    def test_commuting_control_is_invariant(self):
        self.assertTrue(_commuting_control(self.artifacts)["control_pass"])

    def test_artifact_sampling_is_recorded(self):
        result = path_matrix(persons=4, seed=41, artifact_limit=8)
        self.assertEqual(result["evaluated_artifacts"], 8)

    def test_claim_remains_bounded_to_matrix(self):
        result = path_matrix(persons=4, seed=41, artifact_limit=8)
        self.assertIn("material_path_dependence", result)
        self.assertIn("random_person_baseline", result)

if __name__ == "__main__":
    unittest.main()
