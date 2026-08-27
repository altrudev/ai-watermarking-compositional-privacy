import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from lab import detector_oracle_v09_execution as ex


def _run_git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class _Chdir:
    def __init__(self, path):
        self.path = str(path)
        self.previous = None

    def __enter__(self):
        self.previous = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.previous)


def _make_repo(td):
    root = Path(td)
    (root / "lab").mkdir()
    (root / "tests").mkdir()
    (root / "lab" / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "tests" / "test_a.py").write_text(
        "import unittest\n\nclass A(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n",
        encoding="utf-8",
    )
    _run_git(root, "init", "-q")
    _run_git(root, "config", "user.email", "ddc@example.invalid")
    _run_git(root, "config", "user.name", "DDC Test")
    _run_git(root, "add", ".")
    _run_git(root, "commit", "-q", "-m", "approved")
    return root, _run_git(root, "rev-parse", "HEAD")


class DetectorOracleExecutionGateTests(unittest.TestCase):
    def test_dirty_worktree_blocks_identity(self):
        with patch.object(ex, "_git", side_effect=[str(Path.cwd()), "abc123", " M lab/detector_oracle_v09.py"]):
            with self.assertRaisesRegex(ex.ExecutionGateError, "WORKTREE_NOT_CLEAN"):
                ex.exact_tree_identity()

    def test_expected_head_mismatch_fails_closed(self):
        with patch.object(ex, "_git", side_effect=[str(Path.cwd()), "actual-head"]):
            with self.assertRaisesRegex(ex.ExecutionGateError, "EXPECTED_HEAD_MISMATCH"):
                ex.exact_tree_identity("approved-head")

    def test_assume_unchanged_cannot_hide_executed_source_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = _make_repo(td)
            _run_git(root, "update-index", "--assume-unchanged", "lab/a.py")
            (root / "lab" / "a.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.assertEqual(_run_git(root, "status", "--porcelain"), "")
            with _Chdir(root):
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTED_INDEX_FLAGS_NOT_CLEAN"):
                    ex.exact_tree_identity(head)

    def test_skip_worktree_cannot_hide_executed_source_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = _make_repo(td)
            _run_git(root, "update-index", "--skip-worktree", "lab/a.py")
            (root / "lab" / "a.py").write_text("VALUE = 3\n", encoding="utf-8")
            self.assertEqual(_run_git(root, "status", "--porcelain"), "")
            with _Chdir(root):
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTED_INDEX_FLAGS_NOT_CLEAN"):
                    ex.exact_tree_identity(head)

    def test_ignored_untracked_python_source_cannot_join_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = _make_repo(td)
            (root / ".git" / "info" / "exclude").write_text("tests/test_injected.py\n", encoding="utf-8")
            (root / "tests" / "test_injected.py").write_text(
                "import unittest\n\nclass Injected(unittest.TestCase):\n    def test_injected(self):\n        self.assertTrue(True)\n",
                encoding="utf-8",
            )
            self.assertEqual(_run_git(root, "status", "--porcelain"), "")
            with _Chdir(root):
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTED_SOURCE_SET_MISMATCH"):
                    ex.exact_tree_identity(head)

    def test_head_blob_mismatch_blocks_even_when_status_and_index_look_clean(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lab").mkdir()
            (root / "tests").mkdir()
            (root / "lab" / "a.py").write_text("VALUE = 9\n", encoding="utf-8")
            calls = iter([
                str(root),
                "approved-head",
                "",
                "100644 blob expected-blob\tlab/a.py\0",
                "H lab/a.py",
                "actual-blob",
            ])
            with _Chdir(root), patch.object(ex, "_git", side_effect=lambda _args: next(calls)):
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTED_BLOB_MISMATCH"):
                    ex.exact_tree_identity("approved-head")

    def test_compile_gate_does_not_write_pycache_into_worktree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lab").mkdir()
            (root / "tests").mkdir()
            (root / "lab" / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "tests" / "test_a.py").write_text("VALUE = 1\n", encoding="utf-8")
            with _Chdir(root):
                result = ex.compile_gate()
            self.assertTrue(result["passed"])
            self.assertFalse(any(root.rglob("__pycache__")))

    def test_execute_requires_expected_head(self):
        with tempfile.TemporaryDirectory() as td:
            result = ex.execute(td, None)
        self.assertFalse(result["canonical"])
        self.assertEqual(result["reason"], "EXPECTED_HEAD_REQUIRED")

    def test_nonisolated_runtime_blocks_before_identity(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": False, "no_user_site": False, "no_site": False, "passed": False}), patch.object(ex, "exact_tree_identity") as identity:
                result = ex.execute(td, "abc")
            identity.assert_not_called()
        self.assertFalse(result["canonical"])
        self.assertEqual(result["reason"], "PYTHON_RUNTIME_NOT_ISOLATED")

    def test_output_inside_worktree_is_rejected_before_compile(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "evidence"
            identity = {"head": "abc", "expected_head": "abc", "repo_root": str(root), "git_blobs": {}, "file_sha256": {}}
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate") as compile_gate:
                result = ex.execute(output, "abc")
            compile_gate.assert_not_called()
            self.assertEqual(result["reason"], "OUTPUT_DIRECTORY_INSIDE_WORKTREE")
            self.assertFalse(output.exists())

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
        identity = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": False, "returncode": 1, "output_sha256": "x"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result):
                result = ex.execute(td, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "COMPILE_FAILED")
            self.assertTrue((ex.Path(td) / "execution-gate.json").exists())
            self.assertFalse((ex.Path(td) / "summary.json").exists())

    def test_regression_failure_cannot_reach_replay(self):
        identity = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": False, "returncode": 1, "test_count": 1, "output_sha256": "t"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate") as replay:
                result = ex.execute(td, "abc")
            replay.assert_not_called()
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "REGRESSION_FAILED")

    def test_tree_drift_after_reference_replay_blocks_finalization(self):
        before = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {"x": "1"}, "file_sha256": {"x": "a"}}
        after = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {"x": "2"}, "file_sha256": {"x": "b"}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 10, "output_sha256": "t"}
        replay_result = {"passed": True, "first_complete_manifest_sha256": "r", "second_complete_manifest_sha256": "r", "equal_files": {}}
        ref = {
            "summary": {"classification": "PENDING_EXACT_EXECUTION_GATE", "candidate_classification_before_execution_gate": "NO_PREDECLARED_EFFECT_ESTABLISHED"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}), patch.object(ex, "exact_tree_identity", side_effect=[before, after]), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)):
                result = ex.execute(td, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "EXECUTION_TREE_CHANGED_AFTER_REFERENCE_REPLAY")
            self.assertFalse((ex.Path(td) / "summary.json").exists())

    def test_reference_replay_failure_blocks_before_canonical_replay(self):
        identity = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 100, "output_sha256": "t"}
        replay_result = {"passed": False, "first_complete_manifest_sha256": "a", "second_complete_manifest_sha256": "b", "equal_files": {}}
        ref = {
            "summary": {"classification": "PENDING_EXACT_EXECUTION_GATE", "candidate_classification_before_execution_gate": "DETECTOR_MEDIATED_INFERENCE_OBSERVED"},
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "runtime_isolation", return_value={"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)), patch.object(ex, "canonical_bundle_replay") as canonical:
                result = ex.execute(td, "abc")
            canonical.assert_not_called()
            self.assertEqual(result["reason"], "REFERENCE_REPLAY_FAILED")
            self.assertFalse(result["canonical"])


if __name__ == "__main__":
    unittest.main()
