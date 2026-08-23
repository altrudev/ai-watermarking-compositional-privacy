import unittest
from unittest.mock import patch

from lab import detector_oracle_v09 as core
from lab import detector_oracle_v09_evidence as ev


class DetectorOracleSecondAuditRepairTests(unittest.TestCase):
    def test_calibration_vector_length_mismatch_is_retained(self):
        with patch.object(core, "calibration_templates", side_effect=ValueError("vector length mismatch")):
            summary, records = ev.condition_evidence("S1", "D3", "QF", 4, "A0", "E0")
        self.assertEqual(summary["status"], "INVALID")
        self.assertEqual(summary["invalid_reason"], "OBSERVATION_TEMPLATE_LENGTH_MISMATCH")
        self.assertEqual(summary["evidence_count"], len(records))

    def test_d6_parity_checks_nonfirst_informative_query(self):
        original = core.disclose

        def corrupted(a, z, disclosure, query_index):
            value = original(a, z, disclosure, query_index)
            if disclosure == "D6" and query_index == 2 and value != "RATE_LIMITED":
                return "HIGH" if value != "HIGH" else "LOW"
            return value

        with patch.object(core, "disclose", side_effect=corrupted):
            self.assertFalse(ev.disclosure_parity_control())

    def test_adaptive_invalidity_has_its_own_denominator(self):
        comparisons = []
        adaptive_families = []
        for d in core.DISCLOSURES[1:]:
            for p in ("QA_REMOVE", "QA_SPOOF"):
                for budget in core.BUDGETS:
                    for state in core.CORE_STATES:
                        for evidence in core.CORE_EVIDENCE:
                            adaptive_families.append((d, p, budget, state, evidence))

        invalid_cut = int(len(adaptive_families) * 0.21) + 1
        invalid_set = set(adaptive_families[:invalid_cut])
        passing_family = adaptive_families[-1]

        for family in adaptive_families:
            d, p, budget, state, evidence = family
            for scenario in core.SCENARIOS:
                comparisons.append({
                    "status": "EVALUATED",
                    "invalid_reason": None,
                    "comparison_type": "DETECTOR_VS_D0",
                    "scenario": scenario,
                    "tested": [d, p, budget, state, evidence],
                    "baseline": ["D0", "QF", budget, state, evidence],
                    "information_gain_delta": 0.0,
                    "accuracy_delta": 0.0,
                    "candidate_size_reduction": 0,
                    "utility_ok": True,
                    "scenario_material_pass": False,
                })
                adaptive_invalid = family in invalid_set
                adaptive_pass = family == passing_family
                comparisons.append({
                    "status": "INVALID" if adaptive_invalid else "EVALUATED",
                    "invalid_reason": "MISSING_OR_INVALID_MATCHED_CONDITION" if adaptive_invalid else None,
                    "comparison_type": "ADAPTIVE_VS_QF",
                    "scenario": scenario,
                    "tested": [d, p, budget, state, evidence],
                    "baseline": [d, "QF", budget, state, evidence],
                    "information_gain_delta": 0.2 if adaptive_pass else 0.0,
                    "accuracy_delta": 0.0,
                    "candidate_size_reduction": 0,
                    "utility_ok": True,
                    "scenario_material_pass": False,
                })

        labels = ev._replication_labels(comparisons, [])
        self.assertGreater(labels["adaptive_invalid_family_ratio"], 0.20)
        self.assertFalse(labels["adaptive"])
        self.assertTrue(labels["unknown_controls_complete"])


if __name__ == "__main__":
    unittest.main()
