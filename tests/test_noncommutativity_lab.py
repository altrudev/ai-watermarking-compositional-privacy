import unittest
from dataclasses import asdict

from lab.noncommutativity_lab import (
    CachedEvaluator,
    TRANSFORM_NAMES,
    _apply,
    _pearson,
    commuting_control,
    full_path_prediction,
    pairwise_mechanisms,
)
from lab.transformation_chain_lab import WEIGHTS, evaluate, generate_population, make_artifacts


class NonCommutativityLabTests(unittest.TestCase):
    def setUp(self):
        self.population = generate_population(6, 41)
        self.artifacts = make_artifacts(self.population, seed=7000)[:18]
        self.evaluator = CachedEvaluator(self.population)

    def test_declared_transform_set_is_fixed(self):
        self.assertEqual(
            TRANSFORM_NAMES,
            ("paraphrase", "summarize", "translate", "model_edit"),
        )

    def test_cached_evaluator_matches_canonical_scorer(self):
        transformed = _apply(self.artifacts, ("summarize", "model_edit"))
        self.assertEqual(
            asdict(self.evaluator.evaluate(transformed, WEIGHTS)),
            asdict(evaluate(self.population, transformed, WEIGHTS)),
        )

    def test_pairwise_matrix_contains_all_six_pairs(self):
        result = pairwise_mechanisms(self.evaluator, self.artifacts)
        self.assertEqual(len(result["pairs"]), 6)
        self.assertEqual(len(result["directional_person_effects"]), 6)

    def test_pairwise_records_state_and_channel_differences(self):
        result = pairwise_mechanisms(self.evaluator, self.artifacts)
        for row in result["pairs"].values():
            self.assertIn("text_difference_fraction", row)
            self.assertIn("feature_divergence", row)
            self.assertIn("single_channel_person_top1_difference", row)
            self.assertIn(row["largest_changed_channel"], {"lexical", "semantic", "style", "watermark", "time"})

    def test_full_path_predictor_evaluates_all_orders(self):
        pairwise = pairwise_mechanisms(self.evaluator, self.artifacts)
        result = full_path_prediction(
            self.evaluator,
            self.artifacts,
            pairwise["directional_person_effects"],
        )
        self.assertEqual(result["path_count"], 24)
        self.assertTrue(-1.0 <= result["pearson_r"] <= 1.0)

    def test_commuting_negative_control_is_invariant(self):
        result = commuting_control(self.evaluator, self.artifacts)
        self.assertTrue(result["control_pass"])
        self.assertTrue(result["final_text_identical"])
        self.assertTrue(result["final_metadata_identical"])
        self.assertEqual(result["person_top1_difference"], 0.0)
        self.assertEqual(result["generation_top1_difference"], 0.0)

    def test_pearson_rejects_constant_predictor_as_nonpredictive(self):
        self.assertEqual(_pearson([1.0, 1.0, 1.0], [0.0, 0.5, 1.0]), 0.0)


if __name__ == "__main__":
    unittest.main()
