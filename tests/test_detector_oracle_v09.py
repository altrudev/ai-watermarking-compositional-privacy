import unittest
from dataclasses import replace
from lab.detector_oracle_v09 import *


class DetectorOracleV09Tests(unittest.TestCase):
    def test_protocol_lineage(self):
        self.assertEqual(PROTOCOL_BASE, "da81f93f7e275d2e87358c8e359a5dd529c7d98d")
        self.assertEqual(PROTOCOL_AUDIT_PASS, "ecee93170bfa4f8099e6eb9d1c844ef85f27a19a")
        self.assertEqual(REPRESENTED, ("K1", "K2", "K3", "K4"))
        self.assertEqual(BUDGETS, (4, 16))

    def test_hash_mapping(self):
        self.assertEqual(hash_unit("x"), hash_unit("x"))
        self.assertGreaterEqual(hash_unit("x"), 0)
        self.assertLessEqual(hash_unit("x"), 1)
        self.assertGreaterEqual(map_hash("x", -.2, .2), -.2)
        self.assertLessEqual(map_hash("x", -.2, .2), .2)

    def test_population_mapping(self):
        self.assertEqual(sum(instance_count("S1", k) for k in REPRESENTED), 8)
        self.assertEqual(sum(instance_count("S2", k) for k in REPRESENTED), 16)
        self.assertEqual(sum(instance_count("S3", k) for k in REPRESENTED), 24)
        self.assertEqual(sum(instance_count("S3", k) for k in UNKNOWN), 12)
        a = make_artifact("S1", "K1", 0, 8, "A0")
        self.assertEqual(a.artifact_id, "syn-S1-K1-scope-00-artifact-08")

    def test_detector_disclosures_same_hidden_score(self):
        a = make_artifact("S1", "K2", 0, 8, "A0")
        s = hidden_score(a)
        self.assertEqual(disclose(a, a.z, "D1", 1), "DETECTED" if s >= .65 else "NOT_DETECTED")
        self.assertEqual(disclose(a, a.z, "D3", 1), round(s, 3))
        self.assertEqual(len(flatten_response("D4", disclose(a, a.z, "D4", 1))), 6)
        self.assertEqual(len(flatten_response("D5", disclose(a, a.z, "D5", 1))), 3)

    def test_d6_rate_limit_and_replay(self):
        a = make_artifact("S1", "K3", 0, 8, "A0")
        x = [disclose(a, a.z, "D6", i) for i in range(1, 17)]
        y = [disclose(a, a.z, "D6", i) for i in range(1, 17)]
        self.assertEqual(x, y)
        self.assertTrue(all(v != "RATE_LIMITED" for v in x[:8]))
        self.assertTrue(all(v == "RATE_LIMITED" for v in x[8:]))

    def test_query_budget_exact(self):
        a = make_artifact("S1", "K1", 0, 8, "A0")
        for d in DISCLOSURES[1:]:
            for p in POLICIES:
                for b in BUDGETS:
                    r = run_policy(a, d, p, b)
                    self.assertEqual((len(r.path), r.detector_calls), (b, b))
        r = run_policy(a, "D0", "QF", 16)
        self.assertEqual((len(r.path), r.detector_calls), (16, 0))
        with self.assertRaises(ValueError):
            run_policy(a, "D0", "QA_REMOVE", 4)

    def test_qf_ignores_feedback(self):
        a = make_artifact("S1", "K1", 0, 8, "A0")
        paths = {run_policy(a, d, "QF", 16).path for d in DISCLOSURES}
        self.assertEqual(len(paths), 1)
        self.assertEqual(next(iter(paths))[:6], ("P1", "P2", "P3", "P4", "P5", "P1"))

    def test_utility_independent_of_disclosure(self):
        a = make_artifact("S1", "K2", 0, 8, "A1")
        values = {run_policy(a, d, "QF", 16).utility for d in DISCLOSURES}
        self.assertEqual(values, {.97-.008*16})

    def test_templates_shape(self):
        for d, p in (("D0", "QF"), ("D1", "QF"), ("D4", "QA_REMOVE"), ("D5", "QA_SPOOF")):
            templates = calibration_templates("S1", d, p, 4, "A0")
            self.assertEqual(tuple(k for k, _ in templates), REPRESENTED)
            self.assertEqual(len({len(v) for _, v in templates}), 1)

    def test_d0_uniform_posterior(self):
        a = make_artifact("S1", "K3", 0, 8, "A0")
        m = inference_metrics(a, "D0", "QF", 4, "A0", "E0")
        self.assertEqual(m["posterior"], {k: .25 for k in REPRESENTED})
        self.assertAlmostEqual(m["information_gain"], 0.0)

    def test_unknown_e3_has_no_truth_bonus(self):
        a = make_artifact("S1", "K5", 0, 8, "A0")
        p = e3_prior(a)
        self.assertAlmostEqual(sum(p.values()), 1.0)
        self.assertNotIn(a.k, p)

    def test_open_set_threshold(self):
        self.assertTrue(open_set_accept({"K1": .70, "K2": .10, "K3": .10, "K4": .10})[0])
        self.assertFalse(open_set_accept({"K1": .40, "K2": .30, "K3": .20, "K4": .10})[0])

    def test_controls(self):
        c = controls()
        self.assertTrue(c["all_pass"], c)
        self.assertEqual(len([k for k in c if k.startswith("C")]), 12)

    def test_truth_custody_label_not_detector_input(self):
        a = make_artifact("S1", "K2", 0, 8, "A0")
        b = replace(a, truth_tag="other")
        self.assertEqual(hidden_score(a), hidden_score(b))
        for d in ("D1", "D2", "D3", "D4", "D5"):
            self.assertEqual(disclose(a, a.z, d, 1), disclose(b, b.z, d, 1))

    def test_classification_precedence(self):
        self.assertEqual(classify_summary(False, True, True, True, True, True), "CONTROL_FAILED")
        self.assertEqual(classify_summary(True, True, False, False, False, False), "DETECTOR_MEDIATED_INFERENCE_OBSERVED")
        self.assertEqual(classify_summary(True, False, False, False, False, True), "FALSE_ATTRIBUTION_ONLY_OBSERVED")
        self.assertEqual(classify_summary(True, False, False, False, False, False), "NO_PREDECLARED_EFFECT_ESTABLISHED")

    def test_family_replication_requires_same_family(self):
        selected = []
        for sc, d in (("S1", "D1"), ("S2", "D2")):
            for disc in ("D0", d):
                selected.append({
                    "scenario": sc, "disclosure": disc, "policy": "QF", "budget": 16,
                    "state": "A0", "evidence": "E0",
                    "median_information_gain": 0.0 if disc == "D0" else .3,
                    "accuracy": .25 if disc == "D0" else .5,
                    "median_utility": .9,
                })
        details = family_labels(selected, [])
        self.assertFalse(details["material"])

    def test_selected_condition_replay(self):
        a = condition_summary("S1", "D4", "QA_REMOVE", 4, "A0", "E3")
        b = condition_summary("S1", "D4", "QA_REMOVE", 4, "A0", "E3")
        self.assertEqual(a, b)
        self.assertEqual(stable_hash(a), stable_hash(b))


if __name__ == "__main__":
    unittest.main()
