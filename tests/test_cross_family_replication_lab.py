import unittest

from lab.cross_family_replication_lab import (
    FAMILIES,
    POLICIES,
    SCENARIOS,
    SCENARIO_TRANSFERS,
    _holdout_class,
    _transfer_class,
    commuting_control,
    pairwise_effects,
    partition_artifacts,
    predict_paths,
    prepare_scenario,
    run_reference_matrix,
    scorer_parity,
)


HISTORICAL_V06_TRANSFORMS = {"paraphrase", "summarize", "translate", "model_edit"}
ALLOWED_CLAIMS = {
    "MECHANISM_REPLICATED_WITH_TRANSFER_FOR_DECLARED_MATRIX",
    "CONTEXT_DEPENDENT_REPLICATION",
    "MECHANISM_NOT_REPLICATED",
    "CONTROL_FAILED",
}


class CrossFamilyReplicationTests(unittest.TestCase):
    def test_protocol_matrix_is_frozen(self):
        self.assertEqual(len(FAMILIES), 2)
        self.assertEqual(len(POLICIES), 5)
        self.assertEqual(len(SCENARIOS), 6)
        self.assertEqual(SCENARIO_TRANSFERS, (("S1", "S2"), ("S3", "S4"), ("S5", "S6")))
        self.assertEqual(POLICIES["canonical_combined"], (0.30, 0.20, 0.10, 0.10, 0.05, 0.25))
        self.assertEqual(SCENARIOS["S1"], {"persons": 8, "seed": 41, "artifact_seed": 7000})
        self.assertEqual(SCENARIOS["S6"], {"persons": 16, "seed": 101, "artifact_seed": 9001})

    def test_transform_families_are_new_and_four_wide(self):
        for transforms in FAMILIES.values():
            self.assertEqual(len(transforms), 4)
            self.assertTrue(HISTORICAL_V06_TRANSFORMS.isdisjoint(set(transforms)))

    def test_transforms_are_deterministic_nonempty_and_preserve_identity_metadata(self):
        population, _calibration, holdout, _evaluator = prepare_scenario("S1")
        self.assertTrue(all(row.person_id.startswith("syn-") for row in population))
        artifact = holdout[0]
        for transforms in FAMILIES.values():
            for transform in transforms.values():
                left = transform(artifact)
                right = transform(artifact)
                self.assertEqual(left, right)
                self.assertTrue(left.text.strip())
                self.assertEqual(left.target_generation_id, artifact.target_generation_id)
                self.assertEqual(left.provider_hint, artifact.provider_hint)
                self.assertEqual(left.watermark_family, artifact.watermark_family)
                self.assertEqual(left.published_minute, artifact.published_minute)

    def test_partition_is_deterministic_disjoint_and_complete(self):
        population, calibration, holdout, _evaluator = prepare_scenario("S1")
        artifacts = calibration + holdout
        left_cal, left_hold = partition_artifacts(artifacts)
        right_cal, right_hold = partition_artifacts(artifacts)
        self.assertEqual(left_cal, right_cal)
        self.assertEqual(left_hold, right_hold)
        cal_ids = {row.target_generation_id for row in left_cal}
        hold_ids = {row.target_generation_id for row in left_hold}
        self.assertTrue(cal_ids.isdisjoint(hold_ids))
        self.assertEqual(len(cal_ids | hold_ids), len(population))

    def test_cached_scorer_matches_canonical_scorer(self):
        population, _calibration, holdout, evaluator = prepare_scenario("S1")
        self.assertTrue(scorer_parity(population, holdout, evaluator))

    def test_commuting_control_passes_for_all_policies(self):
        _population, _calibration, holdout, evaluator = prepare_scenario("S1")
        for weights in POLICIES.values():
            result = commuting_control(evaluator, holdout, weights)
            self.assertTrue(result["control_pass"])
            self.assertEqual(result["person_top1_difference"], 0.0)
            self.assertEqual(result["generation_top1_difference"], 0.0)

    def test_pairwise_effects_are_calibration_only_and_predict_holdout_paths(self):
        _population, calibration, holdout, evaluator = prepare_scenario("S1")
        transforms = FAMILIES["structural_normalization"]
        weights = POLICIES["canonical_combined"]
        pair = pairwise_effects(evaluator, calibration, transforms, weights)
        self.assertEqual(len(pair["effects"]), 6)
        prediction = predict_paths(evaluator, holdout, transforms, weights, pair["effects"])
        self.assertEqual(prediction["path_count"], 24)
        self.assertEqual(len(prediction["paths"]), 24)
        self.assertTrue(-1.0 <= prediction["pearson_r"] <= 1.0)

    def test_threshold_classifiers_match_predeclared_protocol(self):
        self.assertEqual(_holdout_class(0.70), "predictive")
        self.assertEqual(_holdout_class(0.69), "partial")
        self.assertEqual(_holdout_class(0.29), "not_predictive")
        self.assertEqual(_transfer_class(0.50), "transfer_supported")
        self.assertEqual(_transfer_class(0.49), "weak_context_dependent_transfer")
        self.assertEqual(_transfer_class(0.19), "transfer_not_supported")

    def test_no_real_identity_loader_is_exposed(self):
        import lab.cross_family_replication_lab as module

        forbidden = {
            "load_real_people",
            "load_provider_logs",
            "load_private_conversations",
            "load_social_profiles",
            "load_external_identity_corpus",
        }
        self.assertTrue(forbidden.isdisjoint(set(dir(module))))

    def test_full_reference_matrix_has_declared_shape_and_bounded_claim(self):
        result = run_reference_matrix()
        self.assertEqual(result["protocol_commit"], "786ebb3d097d999e15f72cbfce536e59566206a1")
        self.assertEqual(len(result["holdout_cells"]), 60)
        self.assertEqual(len(result["transfer_cells"]), 30)
        self.assertEqual(result["aggregate"]["holdout_cell_count"], 60)
        self.assertEqual(result["aggregate"]["transfer_cell_count"], 30)
        self.assertIn(result["claim"]["status"], ALLOWED_CLAIMS)
        self.assertEqual(result["research_scope"], "synthetic-only")


if __name__ == "__main__":
    unittest.main()
