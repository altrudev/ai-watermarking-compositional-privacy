import tempfile
import unittest
from unittest.mock import patch

from lab import detector_oracle_v09_execution as ex


class DetectorOracleExecutionGateTests(unittest.TestCase):
    def test_dirty_worktree_blocks_identity(self):
        with patch.object(ex, "_git", side_effect=["abc123", " M lab/detector_oracle_v09.py"]):
            with self.assertRaisesRegex(ex.ExecutionGateError, "WORKTREE_NOT_CLEAN"):
                ex.exact_tree_identity()

    def test_expected_head_mismatch_fails_closed(self):
        with patch.object(ex, "_git", return_value="actual-head"):
            with self.assertRaisesRegex(ex.ExecutionGateError, "EXPECTED_HEAD_MISMATCH"):
                ex.exact_tree_identity("approved-head")

    def test_execute_requires_expected_head(self):
        with tempfile.TemporaryDirectory() as td:
            result = ex.execute(td, None)
        self.assertFalse(result["canonical"])
        self.assertEqual(result["reason"], "EXPECTED_HEAD_REQUIRED")

    def test_finalize_requires_reference_and_canonical_replay(self):
        ref = {
            "summary": {
                "classification": "PENDING_EXACT_EXECUTION_GATE",
                "candidate_classification_before_execution_gate": "DETECTOR_MEDIATED_INFERENCE_OBSERVED",
                "summary_sha256": "old",
            },
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        identity = {"head": "abc", "expected_head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "output_sha256": "c"}
        regression_result = {"passed": True, "test_count": 100, "output_sha256": "t"}
        replay_result = {"passed": True, "first_complete_manifest_sha256": "r"}
        out = ex.finalize_reference(ref, identity, compile_result, regression_result, replay_result, True)
        self.assertEqual(out["summary"]["exact_execution_gate"], "PASS")
        self.assertEqual(out["summary"]["complete_replay_control"], "PASS")
        self.assertEqual(out["summary"]["classification"], "DETECTOR_MEDIATED_INFERENCE_OBSERVED")

        out = ex.finalize_reference(ref, identity, compile_result, regression_result, replay_result, False)
        self.assertEqual(out["summary"]["exact_execution_gate"], "FAIL")
        self.assertEqual(out["summary"]["complete_replay_control"], "FAIL")
        self.assertEqual(out["summary"]["classification"], "CONTROL_FAILED")

    def test_canonical_bundle_replay_covers_finalized_bundle(self):
        ref = {
            "summary": {
                "classification": "DETECTOR_MEDIATED_INFERENCE_OBSERVED",
                "exact_execution_gate": "PASS",
                "execution_identity": {"head": "abc", "expected_head": "abc"},
            },
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        record = {"status": "PASS", "canonical": True, "expected_head": "abc"}
        replay = ex.canonical_bundle_replay(ref, record)
        self.assertTrue(replay["passed"])
        self.assertTrue(all(replay["equal_files"].values()))
        self.assertEqual(replay["first_manifest_sha256"], replay["second_manifest_sha256"])

    def test_compile_failure_cannot_write_canonical_bundle(self):
        identity = {"head": "abc", "expected_head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": False, "returncode": 1, "output_sha256": "x"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result):
                result = ex.execute(td, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "COMPILE_FAILED")
            self.assertTrue((ex.Path(td) / "execution-gate.json").exists())
            self.assertFalse((ex.Path(td) / "summary.json").exists())

    def test_regression_failure_cannot_reach_replay(self):
        identity = {"head": "abc", "expected_head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": False, "returncode": 1, "test_count": 1, "output_sha256": "t"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate") as replay:
                result = ex.execute(td, "abc")
            replay.assert_not_called()
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "REGRESSION_FAILED")

    def test_tree_drift_after_reference_replay_blocks_finalization(self):
        before = {"head": "abc", "expected_head": "abc", "git_blobs": {"x": "1"}, "file_sha256": {"x": "a"}}
        after = {"head": "abc", "expected_head": "abc", "git_blobs": {"x": "2"}, "file_sha256": {"x": "b"}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 10, "output_sha256": "t"}
        replay_result = {"passed": True, "first_complete_manifest_sha256": "r", "second_complete_manifest_sha256": "r", "equal_files": {}}
        ref = {
            "summary": {"classification": "PENDING_EXACT_EXECUTION_GATE", "candidate_classification_before_execution_gate": "NO_PREDECLARED_EFFECT_ESTABLISHED"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", side_effect=[before, after]), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)):
                result = ex.execute(td, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "EXECUTION_TREE_CHANGED_AFTER_REFERENCE_REPLAY")
            self.assertFalse((ex.Path(td) / "summary.json").exists())

    def test_reference_replay_failure_blocks_before_canonical_replay(self):
        identity = {"head": "abc", "expected_head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 100, "output_sha256": "t"}
        replay_result = {"passed": False, "first_complete_manifest_sha256": "a", "second_complete_manifest_sha256": "b", "equal_files": {}}
        ref = {
            "summary": {"classification": "PENDING_EXACT_EXECUTION_GATE", "candidate_classification_before_execution_gate": "DETECTOR_MEDIATED_INFERENCE_OBSERVED"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)), patch.object(ex, "canonical_bundle_replay") as canonical:
                result = ex.execute(td, "abc")
            canonical.assert_not_called()
            self.assertEqual(result["reason"], "REFERENCE_REPLAY_FAILED")
            self.assertFalse(result["canonical"])


if __name__ == "__main__":
    unittest.main()
