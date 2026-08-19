import unittest

from lab.textual_attack import Adversary, POLICIES, calibrate_adaptive_policy, evaluate, privacy_utility_frontier
from lab.textual_benchmark import run_reference_benchmark
from lab.textual_model import (
    assert_synthetic_only, generate_text_population, lexical_normalize, make_artifacts,
    transform_artifact, utility,
)


class TextualBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.population = generate_text_population(persons=18, seed=73)
        self.artifacts = make_artifacts(self.population)

    def test_population_is_deterministic_and_synthetic_only(self):
        self.assertEqual(self.population, generate_text_population(persons=18, seed=73))
        assert_synthetic_only(self.population)
        self.assertTrue(all(row.person_id.startswith("syn-") for row in self.population))

    def test_population_contains_actual_text(self):
        self.assertTrue(all(len(row.text.split()) > 20 for row in self.population))
        self.assertTrue(any("sig" in row.text.lower() for row in self.population))

    def test_no_real_identity_loader_exists(self):
        import lab.textual_model as mod
        forbidden = {"load_real_people", "load_provider_logs", "load_social_profiles"}
        self.assertTrue(forbidden.isdisjoint(set(dir(mod))))

    def test_baseline_combined_attack_runs(self):
        result = evaluate(self.population, self.artifacts, POLICIES[Adversary.COLLABORATING])
        self.assertEqual(result.samples, len(self.artifacts))
        self.assertTrue(0.0 <= result.person_top1 <= 1.0)

    def test_lexical_normalization_removes_signature_words_at_full_strength(self):
        normalized = lexical_normalize("Sig01 clear sig02 useful sig03.", 1.0)
        for token in ("sig01", "sig02", "sig03"):
            self.assertNotIn(token, normalized.lower())

    def test_composite_transform_strips_provenance_and_delays_time(self):
        original = self.artifacts[0]
        transformed = transform_artifact(original, 1.0)
        self.assertIsNone(transformed.watermark_family)
        self.assertIsNone(transformed.provider_hint)
        self.assertGreater(transformed.published_minute, original.published_minute)
        self.assertNotEqual(transformed.text, original.text)

    def test_utility_is_measured_after_transformation(self):
        result = utility(self.artifacts[0], transform_artifact(self.artifacts[0], 0.75))
        self.assertTrue(0.0 <= result.semantic_retention <= 1.0)
        self.assertTrue(0.0 <= result.content_retention <= 1.0)

    def test_adaptive_policy_reweights_remaining_signals(self):
        transformed = [transform_artifact(item, 1.0) for item in self.artifacts]
        policy, scores = calibrate_adaptive_policy(self.population, transformed[:20])
        total = policy.semantic + policy.style + policy.lexical + policy.watermark + policy.provider + policy.time
        self.assertAlmostEqual(total, 1.0)
        self.assertEqual(set(scores), {"semantic", "style", "lexical", "watermark", "provider", "time"})

    def test_frontier_has_declared_strengths_and_metrics(self):
        points = privacy_utility_frontier(self.population, self.artifacts, strengths=(0.0, 0.5, 1.0))
        self.assertEqual([point.strength for point in points], [0.0, 0.5, 1.0])
        self.assertTrue(all(0.0 <= point.person_top1 <= 1.0 for point in points))

    def test_reference_report_preserves_nonclaims(self):
        report = run_reference_benchmark(seed=73)
        joined = " ".join(report["boundaries"]).lower()
        self.assertIn("synthetic", joined)
        self.assertIn("no real provider detector", joined)
        self.assertIn("failed re-identification is not proven anonymity", joined)
        self.assertIn(report["claim"], {"SUPPORTED_FOR_DECLARED_TEST", "NOT_SUPPORTED"})


if __name__ == "__main__":
    unittest.main()
