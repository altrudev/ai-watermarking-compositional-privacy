import tempfile
import unittest
from unittest.mock import patch

from lab import detector_oracle_v09_execution as ex


class DetectorOracleExecutionGateTests(unittest.TestCase):
    def test_dirty_worktree_blocks_identity(self):
        with patch.object(ex, "_git", side_effect=["abc123", " M lab/detector_oracle_v09.py"]):
            with self.assertRaisesRegex(ex.ExecutionGateError, "WORKTREE_NOT_CLEAN"):
                ex.exact_tree_identity()

    def test_finalize_requires_all_runtime_gates(self):
        ref = {
            "summary": {"classification": "DETECTOR_MEDIATED_INFERENCE_OBSERVED", "summary_sha256": "old"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        identity = {"head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "output_sha256": "c"}
        regression_result = {"passed": True, "test_count": 100, "output_sha256": "t"}
        replay_result = {"passed": True, "first_complete_manifest_sha256": "r"}
        out = ex.finalize_reference(ref, identity, compile_result, regression_result, replay_result)
        self.assertEqual(out["summary"]["exact_execution_gate"], "PASS")
        self.assertEqual(out["summary"]["complete_replay_control"], "PASS")
        self.assertEqual(out["summary"]["classification"], "DETECTOR_MEDIATED_INFERENCE_OBSERVED")

        replay_result["passed"] = False
        out = ex.finalize_reference(ref, identity, compile_result, regression_result, replay_result)
        self.assertEqual(out["summary"]["exact_execution_gate"], "FAIL")
        self.assertEqual(out["summary"]["classification"], "CONTROL_FAILED")

    def test_compile_failure_cannot_write_canonical_bundle(self):
        identity = {"head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": False, "returncode": 1, "output_sha256": "x"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result):
                result = ex.execute(td)
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "COMPILE_FAILED")
            self.assertTrue((ex.Path(td) / "execution-gate.json").exists())
            self.assertFalse((ex.Path(td) / "summary.json").exists())

    def test_regression_failure_cannot_reach_replay(self):
        identity = {"head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": False, "returncode": 1, "test_count": 1, "output_sha256": "t"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate") as replay:
                result = ex.execute(td)
            replay.assert_not_called()
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "REGRESSION_FAILED")

    def test_replay_failure_forces_control_failed(self):
        ref = {
            "summary": {"classification": "DETECTOR_MEDIATED_INFERENCE_OBSERVED", "summary_sha256": "old"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        identity = {"head": "abc", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 100, "output_sha256": "t"}
        replay_result = {"passed": False, "first_complete_manifest_sha256": "a", "second_complete_manifest_sha256": "b", "equal_files": {}}
        final = ex.finalize_reference(ref, identity, compile_result, regression_result, replay_result)
        self.assertEqual(final["summary"]["classification"], "CONTROL_FAILED")
        self.assertEqual(final["summary"]["exact_execution_gate"], "FAIL")


if __name__ == "__main__":
    unittest.main()
