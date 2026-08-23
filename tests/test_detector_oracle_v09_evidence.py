import unittest
from unittest.mock import patch

from lab import detector_oracle_v09 as core
from lab import detector_oracle_v09_evidence as ev


class DetectorOracleEvidenceTests(unittest.TestCase):
    def test_evidence_lineage(self):
        self.assertEqual(ev.EVIDENCE_AMENDMENT, "3b0bfb712f41a3112fbb1d3c3019ceff89f63713")
        self.assertEqual(ev.EVIDENCE_AUDIT_PASS, "59374595c41e4c3732d5eb5b1a117c9623884075")
        self.assertEqual(ev.MITIGATION_STATUS, "NOT_EVALUABLE_UNDER_V0.9")

    def test_artifact_record_contains_required_custody(self):
        a = core.make_artifact("S1", "K2", 0, 8, "A0")
        r = ev.artifact_evidence(a, "D3", "QF", 4, "A0", "E3")
        for key in (
            "artifact_id", "starting_score", "final_score", "detector_calls",
            "response_sha256", "path", "utility", "posterior", "predicted",
            "entropy", "information_gain", "candidate_size",
        ):
            self.assertIn(key, r)
        self.assertEqual(r["detector_calls"], 4)
        self.assertEqual(len(r["path"]), 4)
        self.assertEqual(len(r["response_sha256"]), 64)
        self.assertAlmostEqual(sum(r["posterior"].values()), 1.0)

    def test_unknown_record_retains_open_set_decision(self):
        a = core.make_artifact("S1", "K5", 0, 8, "A4")
        r = ev.artifact_evidence(a, "D4", "QA_SPOOF", 4, "A4", "E0", unknown=True)
        for key in ("open_set_accepted", "accepted_class", "top_posterior", "top_margin"):
            self.assertIn(key, r)
        self.assertTrue(r["unknown"])

    def test_condition_summary_references_evidence_hash(self):
        summary, records = ev.condition_evidence("S1", "D3", "QF", 4, "A0", "E0")
        self.assertEqual(summary["status"], "EVALUATED")
        self.assertEqual(summary["evidence_count"], len(records))
        self.assertEqual(summary["evidence_sha256"], ev.sha256_records(records))
        self.assertGreater(len(records), 0)

    def test_protocol_invalid_cell_is_retained(self):
        with patch.object(core, "detector_posterior", side_effect=ArithmeticError("posterior underflow")):
            summary, records = ev.condition_evidence("S1", "D3", "QF", 4, "A0", "E0")
        self.assertEqual(summary["status"], "INVALID")
        self.assertEqual(summary["invalid_reason"], "POSTERIOR_NORMALIZATION_UNDERFLOW")
        self.assertEqual(summary["evidence_count"], len(records))

    def test_unexpected_value_error_fails_closed(self):
        with patch.object(core, "detector_posterior", side_effect=ValueError("unexpected programming defect")):
            with self.assertRaises(ValueError):
                ev.condition_evidence("S1", "D3", "QF", 4, "A0", "E0")

    def test_matched_comparison_deltas(self):
        d0, _ = ev.condition_evidence("S1", "D0", "QF", 4, "A0", "E0")
        d3, _ = ev.condition_evidence("S1", "D3", "QF", 4, "A0", "E0")
        row = ev._comparison_record(d3, d0, "DETECTOR_VS_D0")
        self.assertEqual(row["status"], "EVALUATED")
        self.assertAlmostEqual(row["information_gain_delta"], d3["median_information_gain"] - d0["median_information_gain"])
        self.assertAlmostEqual(row["candidate_size_reduction"], d0["median_candidate_size"] - d3["median_candidate_size"])

    def test_m5_formula_exact(self):
        a = core.make_artifact("S1", "K1", 0, 8, "A0")
        qf = core.run_policy(a, "D3", "QF", 4)
        rm = core.run_policy(a, "D3", "QA_REMOVE", 4)
        sp = core.run_policy(a, "D3", "QA_SPOOF", 4)
        self.assertAlmostEqual(qf.final_score - rm.final_score, qf.final_score - rm.final_score)
        self.assertAlmostEqual(sp.final_score - qf.final_score, sp.final_score - qf.final_score)
        rows = ev.m5_records()
        hit = next(r for r in rows if r["scenario"] == "S1" and r["disclosure"] == "D3" and r["budget"] == 4 and r["state"] == "A0")
        self.assertIn("median_removal_advantage", hit)
        self.assertIn("median_spoof_advantage", hit)
        self.assertGreater(hit["artifact_count"], 0)

    def test_full_disclosure_parity_control(self):
        self.assertTrue(ev.disclosure_parity_control())

    def test_mitigation_cannot_emit_positive_label(self):
        represented = []
        unknown = []
        for scenario in core.SCENARIOS:
            for disclosure in ("D0", "D6"):
                represented.append({
                    "status": "EVALUATED", "scenario": scenario, "disclosure": disclosure,
                    "policy": "QF", "budget": 16, "state": "A0", "evidence": "E0",
                    "median_information_gain": 0.0, "accuracy": .25,
                    "median_candidate_size": 4, "median_utility": .9,
                })
        comps = ev.matched_comparisons(represented)
        labels = ev._replication_labels(comps, represented, unknown)
        self.assertFalse(labels["mitigation"])
        self.assertEqual(labels["mitigation_status"], "NOT_EVALUABLE_UNDER_V0.9")

    def test_bundle_serialization_is_deterministic_for_same_reference(self):
        summary, records = ev.condition_evidence("S1", "D4", "QA_REMOVE", 4, "A0", "E3")
        ref = {
            "summary": {"condition": summary},
            "represented_evidence": records,
            "unknown_evidence": [],
            "comparisons": [],
            "m5": [],
        }
        a = ev.bundle_bytes(ref)
        b = ev.bundle_bytes(ref)
        self.assertEqual(a["complete_manifest_sha256"], b["complete_manifest_sha256"])
        self.assertEqual(a["summary.json"], b["summary.json"])


if __name__ == "__main__":
    unittest.main()
