import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lab import detector_oracle_v09_execution as ex


def _runtime_pass():
    return {"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}


def _identity(blob="1", file_hash="a"):
    return {
        "head": "abc",
        "expected_head": "abc",
        "repo_root": "/definitely-not-output",
        "git_blobs": {"x": blob},
        "file_sha256": {"x": file_hash},
    }


def _gate_inputs():
    compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
    regression_result = {"passed": True, "returncode": 0, "test_count": 10, "output_sha256": "t"}
    replay_result = {
        "passed": True,
        "first_complete_manifest_sha256": "r",
        "second_complete_manifest_sha256": "r",
        "equal_files": {},
    }
    reference = {
        "summary": {
            "classification": "PENDING_EXACT_EXECUTION_GATE",
            "candidate_classification_before_execution_gate": "NO_PREDECLARED_EFFECT_ESTABLISHED",
        },
        "represented_evidence": [],
        "unknown_evidence": [],
        "comparisons": [],
        "m5": [],
    }
    return compile_result, regression_result, replay_result, reference


class DetectorOraclePublicationRaceTests(unittest.TestCase):
    def test_final_write_race_does_not_delete_unowned_target(self):
        before = _identity()
        compile_result, regression_result, replay_result, reference = _gate_inputs()

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "evidence"

            def raced_write(output_dir, _reference, _record, payloads=None):
                raced = Path(output_dir)
                raced.mkdir()
                (raced / "sentinel.txt").write_text("unowned\n", encoding="utf-8")
                raise FileExistsError("simulated output race")

            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), \
                    patch.object(ex, "exact_tree_identity", side_effect=[dict(before), dict(before), dict(before)]), \
                    patch.object(ex, "compile_gate", return_value=compile_result), \
                    patch.object(ex, "regression_gate", return_value=regression_result), \
                    patch.object(ex, "replay_gate", return_value=(replay_result, reference)), \
                    patch.object(ex, "write_final_bundle", side_effect=raced_write):
                result = ex.execute(output, "abc")

            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "FINAL_WRITE_FAILED")
            self.assertTrue(result["output_path_present_after_failure"])
            self.assertEqual((output / "sentinel.txt").read_text(encoding="utf-8"), "unowned\n")

    def test_verification_exception_discards_owned_bundle_only(self):
        before = _identity()
        compile_result, regression_result, replay_result, reference = _gate_inputs()

        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), \
                    patch.object(ex, "exact_tree_identity", side_effect=[dict(before), dict(before), dict(before)]), \
                    patch.object(ex, "compile_gate", return_value=compile_result), \
                    patch.object(ex, "regression_gate", return_value=regression_result), \
                    patch.object(ex, "replay_gate", return_value=(replay_result, reference)), \
                    patch.object(ex, "verify_written_bundle", side_effect=OSError("simulated readback failure")):
                result = ex.execute(output, "abc")

            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "FINAL_WRITE_VERIFICATION_FAILED")
            self.assertTrue(result["output_discarded"])
            self.assertFalse(output.exists())

    def test_persisted_block_record_agrees_with_returned_persistence_state(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "blocked"
            result = ex._blocked(output, "TEST_BLOCK")
            record = json.loads((output / "execution-gate.json").read_text(encoding="utf-8"))

        self.assertTrue(result["evidence_persisted"])
        self.assertTrue(record["evidence_persisted"])
        self.assertEqual(record["reason"], "TEST_BLOCK")
        self.assertFalse(record["canonical"])


if __name__ == "__main__":
    unittest.main()
