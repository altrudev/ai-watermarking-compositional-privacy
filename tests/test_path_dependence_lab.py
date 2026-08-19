import unittest

from lab.path_dependence_lab import (
    CachedEvaluator,
    PATH_TRANSFORMS,
    TRANSFORM_NAMES,
    UTILITY_MATCH_TOLERANCE,
    all_orders,
    apply_order,
    run_experiment,
    utility_matched,
    validate_order,
)
from lab.transformation_chain_lab import evaluate, generate_population, make_artifacts


class PathDependenceUnitTests(unittest.TestCase):
    def test_all_120_orders_are_unique_and_use_same_transform_set(self):
        orders = all_orders()
        self.assertEqual(len(orders), 120)
        self.assertEqual(len(set(orders)), 120)
        expected = set(TRANSFORM_NAMES)
        self.assertTrue(all(set(order) == expected and len(order) == len(expected) for order in orders))

    def test_invalid_paths_fail_closed(self):
        with self.assertRaises(ValueError):
            validate_order(TRANSFORM_NAMES[:-1])
        with self.assertRaises(ValueError):
            validate_order((TRANSFORM_NAMES[0],) * len(TRANSFORM_NAMES))

    def test_declared_transform_set_excludes_neutral_v03_edit(self):
        self.assertNotIn("edit", PATH_TRANSFORMS)
        self.assertEqual(set(PATH_TRANSFORMS), {"paraphrase", "summarize", "translate", "model_edit", "multi_model_edit"})

    def test_cached_evaluator_preserves_v03_scoring_semantics(self):
        population = generate_population(persons=4, seed=41)
        original = make_artifacts(population)
        final = apply_order(original, all_orders()[0])
        cached = CachedEvaluator(population).evaluate(final)
        canonical = evaluate(population, final)
        self.assertAlmostEqual(cached["person_top1"], canonical.person_top1)
        self.assertAlmostEqual(cached["generation_top1"], canonical.generation_top1)
        self.assertAlmostEqual(cached["generation_top5"], canonical.generation_top5)
        self.assertAlmostEqual(cached["mean_generation_rank"], canonical.mean_generation_rank)
        self.assertAlmostEqual(cached["mean_anonymity_set"], canonical.mean_anonymity_set)

    def test_subset_experiment_is_deterministic(self):
        orders = all_orders()[:3]
        first = run_experiment(persons=4, seed=41, orders=orders)
        second = run_experiment(persons=4, seed=41, orders=orders)
        self.assertEqual(first["all_final_results"], second["all_final_results"])


class PathDependenceReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_experiment(persons=8, seed=41)

    def test_reference_run_evaluates_every_order(self):
        self.assertEqual(self.result["population"], {"persons": 8, "generations": 96})
        self.assertEqual(self.result["orders_evaluated"], 120)
        self.assertEqual(len(self.result["all_final_results"]), 120)

    def test_reference_run_supports_declared_path_dependence(self):
        self.assertAlmostEqual(self.result["order_sensitivity"], 1 / 6)
        self.assertAlmostEqual(self.result["order_sensitivity_pp"], 100 / 6)
        self.assertEqual(self.result["final_claim"]["status"], "supported_for_declared_test")

    def test_minimum_and_maximum_paths_are_materially_different(self):
        low = self.result["minimum_final_attribution"]
        high = self.result["maximum_final_attribution"]
        self.assertAlmostEqual(low["metrics"]["person_top1"], 1 / 3)
        self.assertAlmostEqual(high["metrics"]["person_top1"], 1 / 2)
        self.assertEqual(set(low["order"]), set(high["order"]))

    def test_similar_utility_paths_still_show_same_attribution_gap(self):
        contrast = self.result["matched_utility_contrast"]
        self.assertIsNotNone(contrast)
        self.assertAlmostEqual(contrast["person_top1_delta"], 1 / 6)
        low = contrast["lower_attribution_order"]
        high = contrast["higher_attribution_order"]
        self.assertTrue(utility_matched(low, high))
        for key, tolerance in UTILITY_MATCH_TOLERANCE.items():
            self.assertLessEqual(abs(low["utility"][key] - high["utility"][key]), tolerance)

    def test_path_traces_end_at_the_reported_final_metrics(self):
        low_trace = self.result["minimum_path_trace"]["stages"]
        high_trace = self.result["maximum_path_trace"]["stages"]
        self.assertEqual(len(low_trace), 5)
        self.assertEqual(len(high_trace), 5)
        self.assertEqual(low_trace[-1]["metrics"], self.result["minimum_final_attribution"]["metrics"])
        self.assertEqual(high_trace[-1]["metrics"], self.result["maximum_final_attribution"]["metrics"])

    def test_claim_boundary_remains_synthetic_and_non_universal(self):
        self.assertEqual(self.result["research_scope"], "synthetic-only")
        boundary = self.result["final_claim"]["boundary"].lower()
        self.assertIn("synthetic", boundary)
        self.assertIn("not proof", boundary)
        limitations = " ".join(self.result["limitations"]).lower()
        self.assertIn("not a universal privacy law", limitations)
        self.assertIn("not proof of anonymity", limitations)


if __name__ == "__main__":
    unittest.main()
