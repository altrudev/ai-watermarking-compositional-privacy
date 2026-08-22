import unittest

from lab.open_set_attribution_v08 import Evaluator, POLICIES, prepare, records, calibrate
from lab.open_set_reference_v08 import _five_number, build_cell, evidence_holdout, narrowing_differentials


class T(unittest.TestCase):
    def test_five_number(self):
        self.assertEqual(
            _five_number([5, 1, 3, 2, 4]),
            {"min": 1, "q25": 2, "median": 3, "q75": 4, "max": 5, "count": 5},
        )
        self.assertIsNone(_five_number([]))

    def test_infeasible_holdout_preserves_forced_choice_evidence(self):
        scenario = prepare("S1")
        evaluator = Evaluator(scenario["candidate_population"])
        truth = scenario["truth"]
        known = records(
            evaluator,
            scenario["known_hold"],
            truth,
            "known_hold",
            "published_derivative",
            "global",
            "canonical_combined",
        )
        unknown = records(
            evaluator,
            scenario["u_test"],
            truth,
            "u_test",
            "published_derivative",
            "global",
            "canonical_combined",
        )
        result = evidence_holdout(known, unknown, {"status": "CALIBRATION_INFEASIBLE"})
        self.assertEqual(result["status"], "CALIBRATION_INFEASIBLE")
        self.assertIn("forced_choice_known", result)
        self.assertIn("forced_choice_unknown", result)
        self.assertIn("score_separation", result)
        self.assertGreater(result["forced_choice_unknown"]["candidate_survival_rate"], 0)

    def test_feasible_or_infeasible_cell_preserves_evidence(self):
        result = build_cell(prepare("S1"), "published_derivative", "canonical_combined", "global")
        self.assertIn("forced_choice_known", result["holdout"])
        self.assertIn("forced_choice_unknown", result["holdout"])
        self.assertIn("score_separation", result["holdout"])
        self.assertIn(result["calibration"]["status"], {"FEASIBLE", "CALIBRATION_INFEASIBLE"})

    def test_scenario_cell_shape_and_narrowing_differentials(self):
        scenario = prepare("S1")
        cells = []
        for state in ("published_derivative", "provenance_removed", "post_transform_chain"):
            for policy in POLICIES:
                for mode in ("global", "provider_model_narrowed", "provider_model_time_narrowed"):
                    cells.append(build_cell(scenario, state, policy, mode))
        self.assertEqual(len(cells), 36)
        diff = narrowing_differentials(cells)
        self.assertEqual(len(diff), 24)
        self.assertTrue(all(row["mode"] != "global" for row in diff))


if __name__ == "__main__":
    unittest.main()
