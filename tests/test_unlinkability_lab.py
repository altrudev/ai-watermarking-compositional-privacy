import unittest

from lab.unlinkability_lab import (
    Adversary,
    Basis,
    EvidencePolicy,
    POLICIES,
    assert_synthetic_only,
    centroid,
    composite_privacy_transform,
    correlation_gain,
    delay_publication,
    evaluate,
    evaluate_unlinkability_claim,
    generate_population,
    make_artifacts,
    normalize_style,
    remove_provenance_marker,
    run_reference_experiment,
    semantic_generalize,
    utility,
)


class UnlinkabilityLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = generate_population(
            persons=30,
            accounts_per_person=2,
            sessions_per_account=3,
            generations_per_session=2,
            seed=17,
        )
        cls.artifacts = make_artifacts(cls.population, seed=9000)
        cls.semantic_center = centroid(row.generation_semantic for row in cls.population)
        cls.style_center = centroid(row.generation_style for row in cls.population)
        cls.collaborating = POLICIES[Adversary.COLLABORATING]

    def test_population_is_deterministic(self):
        again = generate_population(
            persons=30,
            accounts_per_person=2,
            sessions_per_account=3,
            generations_per_session=2,
            seed=17,
        )
        self.assertEqual(self.population, again)

    def test_population_is_synthetic_only(self):
        assert_synthetic_only(self.population)
        self.assertTrue(all(row.person_id.startswith("syn-") for row in self.population))

    def test_baseline_combined_evidence_resolves_many_origins(self):
        result = evaluate(self.population, self.artifacts, self.collaborating)
        self.assertGreater(result.person_top1, 0.45)
        self.assertGreater(result.generation_top5, 0.80)

    def test_single_signals_are_weaker_than_combination(self):
        combined = evaluate(self.population, self.artifacts, self.collaborating)
        singles = [
            evaluate(self.population, self.artifacts, EvidencePolicy(semantic=1.0, basis=Basis.GENERATION)),
            evaluate(self.population, self.artifacts, EvidencePolicy(style=1.0, basis=Basis.PERSON)),
            evaluate(self.population, self.artifacts, EvidencePolicy(watermark=1.0, basis=Basis.PERSON)),
            evaluate(self.population, self.artifacts, EvidencePolicy(time=1.0, basis=Basis.GENERATION)),
        ]
        self.assertGreater(correlation_gain(combined, singles), 0.15)

    def test_watermark_removal_is_not_unlinkability(self):
        baseline = evaluate(self.population, self.artifacts, self.collaborating)
        stripped = [remove_provenance_marker(a) for a in self.artifacts]
        residual = evaluate(self.population, stripped, self.collaborating)
        self.assertLess(residual.person_top1, baseline.person_top1)
        self.assertGreater(residual.person_top1, 0.15)

    def test_timing_is_a_distinct_linkage_channel(self):
        delayed = [delay_publication(a, 360) for a in self.artifacts]
        baseline = evaluate(self.population, self.artifacts, self.collaborating)
        residual = evaluate(self.population, delayed, self.collaborating)
        self.assertLess(residual.generation_top1, baseline.generation_top1)

    def test_semantic_and_style_transformations_change_linkability(self):
        semantic = [semantic_generalize(a, self.semantic_center) for a in self.artifacts]
        styled = [normalize_style(a, self.style_center) for a in self.artifacts]
        baseline = evaluate(self.population, self.artifacts, self.collaborating)
        self.assertLess(evaluate(self.population, semantic, self.collaborating).person_top1, baseline.person_top1)
        self.assertLess(evaluate(self.population, styled, self.collaborating).person_top1, baseline.person_top1)

    def test_composite_transform_collapses_reference_attribution(self):
        transformed = [
            composite_privacy_transform(a, self.semantic_center, self.style_center)
            for a in self.artifacts
        ]
        result = evaluate(self.population, transformed, self.collaborating)
        self.assertLess(result.person_top1, 0.10)
        self.assertLess(result.generation_top1, 0.10)
        self.assertGreater(result.mean_generation_rank, 20)

    def test_transform_utility_is_measured_not_assumed(self):
        transformed = composite_privacy_transform(
            self.artifacts[0], self.semantic_center, self.style_center
        )
        result = utility(self.artifacts[0], transformed)
        self.assertGreaterEqual(result.semantic_retention, 0.0)
        self.assertLessEqual(result.semantic_retention, 1.0)
        self.assertGreaterEqual(result.style_retention, 0.0)
        self.assertLessEqual(result.style_retention, 1.0)

    def test_claim_is_adversary_relative_and_not_universal_anonymity(self):
        transformed = [
            composite_privacy_transform(a, self.semantic_center, self.style_center)
            for a in self.artifacts
        ]
        result = evaluate(self.population, transformed, self.collaborating)
        claim = evaluate_unlinkability_claim(
            Adversary.COLLABORATING,
            result,
            min_mean_anonymity_set=2.0,
        )
        self.assertEqual(claim.status, "supported_for_declared_test")
        self.assertIn("not proof of anonymity", claim.reason)
        self.assertEqual(claim.adversary, Adversary.COLLABORATING.value)

    def test_untransformed_artifact_cannot_receive_unlinkability_claim(self):
        baseline = evaluate(self.population, self.artifacts, self.collaborating)
        claim = evaluate_unlinkability_claim(Adversary.COLLABORATING, baseline)
        self.assertEqual(claim.status, "not_supported")

    def test_reference_report_is_explicit_about_simulation_limits(self):
        report = run_reference_experiment(persons=20, seed=17)
        self.assertEqual(report["research_scope"], "synthetic-only")
        self.assertTrue(report["limitations"])
        self.assertIn("correlation_gain_person_top1", report)
        self.assertIn("composite", report["transformed"])


if __name__ == "__main__":
    unittest.main()
