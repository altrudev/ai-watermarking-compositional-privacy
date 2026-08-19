import unittest

from lab.text_unlinkability_lab import (
    TextAdversary,
    TextEvidencePolicy,
    TEXT_POLICIES,
    assert_synthetic_text_only,
    correlation_gain,
    delay_text_publication,
    evaluate_text,
    generate_text_population,
    lexical_vector,
    make_text_artifacts,
    normalize_text_style,
    paraphrase_surface,
    person_style_profiles,
    semantic_vector,
    strip_text_provenance,
    style_vector,
    text_composite_transform,
    text_utility,
    run_text_reference_experiment,
)


class TextUnlinkabilityLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = generate_text_population(persons=18, seed=29)
        cls.artifacts = make_text_artifacts(cls.population, seed=4400)
        cls.policy = TEXT_POLICIES[TextAdversary.COLLABORATING]

    def test_population_deterministic_and_synthetic(self):
        again = generate_text_population(persons=18, seed=29)
        self.assertEqual(self.population, again)
        assert_synthetic_text_only(self.population)

    def test_actual_text_is_generated(self):
        self.assertTrue(all(len(row.text) > 100 for row in self.population))
        self.assertTrue(any("\n\n" in row.text for row in self.population))

    def test_features_are_derived_from_text(self):
        row = self.population[0]
        self.assertGreater(sum(lexical_vector(row.text)), 0)
        self.assertGreater(sum(semantic_vector(row.text)), 0)
        self.assertEqual(len(style_vector(row.text)), 16)
        profiles = person_style_profiles(self.population)
        self.assertIn(row.person_id, profiles)

    def test_combined_evidence_beats_individual_signals(self):
        combined = evaluate_text(self.population, self.artifacts, self.policy)
        singles = [
            evaluate_text(self.population, self.artifacts, TextEvidencePolicy(lexical=1)),
            evaluate_text(self.population, self.artifacts, TextEvidencePolicy(semantic=1)),
            evaluate_text(self.population, self.artifacts, TextEvidencePolicy(style=1)),
            evaluate_text(self.population, self.artifacts, TextEvidencePolicy(watermark=1)),
            evaluate_text(self.population, self.artifacts, TextEvidencePolicy(time=1)),
        ]
        self.assertGreater(correlation_gain(combined, singles), 0.10)

    def test_provenance_removal_is_not_unlinkability(self):
        baseline = evaluate_text(self.population, self.artifacts, self.policy)
        stripped = evaluate_text(
            self.population, [strip_text_provenance(a) for a in self.artifacts], self.policy
        )
        self.assertLess(stripped.person_top1, baseline.person_top1)
        self.assertGreater(stripped.person_top1, 0.15)

    def test_surface_paraphrase_changes_lexical_but_preserves_semantic_features(self):
        original = self.population[0].text
        changed = paraphrase_surface(original)
        self.assertNotEqual(original, changed)
        lexical_similarity = sum(a*b for a,b in zip(lexical_vector(original), lexical_vector(changed)))
        semantic_similarity = sum(a*b for a,b in zip(semantic_vector(original), semantic_vector(changed)))
        self.assertLess(lexical_similarity, semantic_similarity)
        self.assertGreater(semantic_similarity, 0.90)

    def test_style_normalization_changes_measurable_style(self):
        original = self.artifacts[0].text
        normalized = normalize_text_style(original)
        self.assertNotEqual(original, normalized)
        self.assertNotEqual(style_vector(original), style_vector(normalized))

    def test_timing_remains_distinct_channel(self):
        time_only = TextEvidencePolicy(time=1)
        baseline = evaluate_text(self.population, self.artifacts, time_only)
        delayed = evaluate_text(
            self.population, [delay_text_publication(a, 360) for a in self.artifacts], time_only
        )
        self.assertLess(delayed.generation_top1, baseline.generation_top1)
        self.assertLess(delayed.person_top1, baseline.person_top1)

    def test_composite_reduces_attribution(self):
        baseline = evaluate_text(self.population, self.artifacts, self.policy)
        transformed = [text_composite_transform(a) for a in self.artifacts]
        residual = evaluate_text(self.population, transformed, self.policy)
        self.assertLess(residual.person_top1, baseline.person_top1)
        self.assertLess(residual.generation_top1, baseline.generation_top1)

    def test_utility_is_measured(self):
        transformed = text_composite_transform(self.artifacts[0])
        u = text_utility(self.artifacts[0], transformed)
        self.assertGreaterEqual(u.topic_retention, 0)
        self.assertLessEqual(u.topic_retention, 1)
        self.assertGreaterEqual(u.content_word_retention, 0)
        self.assertLessEqual(u.content_word_retention, 1)
        self.assertGreaterEqual(u.length_ratio, 0)
        self.assertLessEqual(u.length_ratio, 1)

    def test_report_states_limits(self):
        report = run_text_reference_experiment(persons=12, seed=29)
        self.assertEqual(report["research_scope"], "synthetic-text-only")
        self.assertTrue(report["limitations"])
        self.assertIn("surface_paraphrase", report["transformed"])
        self.assertIn("correlation_gain_person_top1", report)

    def test_no_real_identity_loader_exists(self):
        import inspect
        import lab.text_unlinkability_lab as text_lab
        source = inspect.getsource(text_lab)
        self.assertNotIn("requests.", source)
        self.assertNotIn("pandas.read", source)
        self.assertNotIn("csv.reader", source)


if __name__ == "__main__":
    unittest.main()
