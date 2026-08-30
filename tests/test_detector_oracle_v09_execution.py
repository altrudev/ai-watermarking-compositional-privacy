import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
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


def _runtime_pass():
    return {"ignore_environment": True, "no_user_site": True, "no_site": True, "passed": True}


def _identity(repo_root="/definitely-not-output", blob="1", file_hash="a"):
    return {
        "head": "abc",
        "expected_head": "abc",
        "repo_root": repo_root,
        "git_blobs": {"x": blob},
        "file_sha256": {"x": file_hash},
    }


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

    def test_compile_gate_recurses_into_nested_python(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lab").mkdir()
            (root / "tests" / "nested").mkdir(parents=True)
            (root / "lab" / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "tests" / "nested" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
            with _Chdir(root):
                result = ex.compile_gate()
            self.assertFalse(result["passed"])
            self.assertFalse(any(root.rglob("__pycache__")))

    def test_regression_gate_rejects_zero_discovered_tests(self):
        fake = {
            "args": [],
            "returncode": 0,
            "stdout": "",
            "stderr": "----------------------------------------------------------------------\nRan 0 tests in 0.000s\n\nOK\n",
            "output_sha256": "x",
        }
        with patch.object(ex, "_run", return_value=fake):
            result = ex.regression_gate()
        self.assertEqual(result["test_count"], 0)
        self.assertFalse(result["passed"])

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
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate") as compile_gate:
                result = ex.execute(output, "abc")
            compile_gate.assert_not_called()
            self.assertEqual(result["reason"], "OUTPUT_DIRECTORY_INSIDE_WORKTREE")
            self.assertFalse(output.exists())

    def test_output_target_must_be_fresh_before_compile(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "evidence"
            output.mkdir()
            identity = _identity()
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate") as compile_gate:
                result = ex.execute(output, "abc")
            compile_gate.assert_not_called()
            self.assertEqual(result["reason"], "OUTPUT_TARGET_NOT_FRESH")
            self.assertTrue(output.exists())

    def test_verify_written_bundle_detects_disk_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "bundle"
            out.mkdir()
            (out / "a.bin").write_bytes(b"changed")
            verification = ex.verify_written_bundle(out, {"a.bin": b"expected"})
        self.assertFalse(verification["passed"])
        self.assertFalse(verification["file_equal"]["a.bin"])

    def test_verify_written_bundle_rejects_symlink_member(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "bundle"
            out.mkdir()
            target = Path(td) / "target.bin"
            target.write_bytes(b"expected")
            (out / "a.bin").symlink_to(target)
            verification = ex.verify_written_bundle(out, {"a.bin": b"expected"})
        self.assertFalse(verification["passed"])
        self.assertFalse(verification["file_equal"]["a.bin"])

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
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result):
                result = ex.execute(output, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "COMPILE_FAILED")
            self.assertTrue((output / "execution-gate.json").exists())
            self.assertFalse((output / "summary.json").exists())

    def test_regression_failure_cannot_reach_replay(self):
        identity = {"head": "abc", "expected_head": "abc", "repo_root": "/definitely-not-output", "git_blobs": {}, "file_sha256": {}}
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": False, "returncode": 1, "test_count": 1, "output_sha256": "t"}
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate") as replay:
                result = ex.execute(output, "abc")
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
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", side_effect=[before, after]), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)):
                result = ex.execute(output, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "EXECUTION_TREE_CHANGED_AFTER_REFERENCE_REPLAY")
            self.assertFalse((output / "summary.json").exists())

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
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", return_value=identity), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)), patch.object(ex, "canonical_bundle_replay") as canonical:
                result = ex.execute(output, "abc")
            canonical.assert_not_called()
            self.assertEqual(result["reason"], "REFERENCE_REPLAY_FAILED")
            self.assertFalse(result["canonical"])

    def test_tree_drift_after_final_write_blocks_and_discards_bundle(self):
        before = _identity()
        drifted = _identity(blob="2", file_hash="b")
        compile_result = {"passed": True, "returncode": 0, "output_sha256": "c"}
        regression_result = {"passed": True, "returncode": 0, "test_count": 10, "output_sha256": "t"}
        replay_result = {
            "passed": True,
            "first_complete_manifest_sha256": "r",
            "second_complete_manifest_sha256": "r",
            "equal_files": {},
        }
        ref = {
            "summary": {
                "classification": "PENDING_EXACT_EXECUTION_GATE",
                "candidate_classification_before_execution_gate": "NO_PREDECLARED_EFFECT_ESTABLISHED",
            },
            "represented_evidence": [], "unknown_evidence": [], "comparisons": [], "m5": [],
        }
        identities = [dict(before), dict(before), dict(before), dict(drifted)]
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "evidence"
            with patch.object(ex, "runtime_isolation", return_value=_runtime_pass()), patch.object(ex, "exact_tree_identity", side_effect=identities), patch.object(ex, "compile_gate", return_value=compile_result), patch.object(ex, "regression_gate", return_value=regression_result), patch.object(ex, "replay_gate", return_value=(replay_result, ref)):
                result = ex.execute(output, "abc")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "EXECUTION_TREE_CHANGED_AFTER_FINAL_WRITE")
            self.assertTrue(result["output_discarded"])
            self.assertFalse(output.exists())

    def test_full_v01_v09_regression_closure(self):
        if os.environ.get("DDC_V09_FULL_REGRESSION_CHILD") == "1":
            self.skipTest("nested full-regression closure guard")

        expected_core_modules = {
            "test_cross_family_replication_diagnostics.py",
            "test_cross_family_replication_lab.py",
            "test_detector_oracle_v09.py",
            "test_detector_oracle_v09_ddc_repairs.py",
            "test_detector_oracle_v09_evidence.py",
            "test_detector_oracle_v09_execution.py",
            "test_detector_oracle_v09_publication_races.py",
            "test_noncommutativity_lab.py",
            "test_open_set_attribution_v08.py",
            "test_path_dependence_lab.py",
            "test_robustness_lab.py",
            "test_text_unlinkability_lab.py",
            "test_transformation_chain_lab.py",
            "test_unlinkability_lab.py",
        }
        actual_modules = sorted(p.name for p in Path("tests").glob("test_*.py") if p.is_file())
        self.assertTrue(expected_core_modules.issubset(set(actual_modules)))

        with tempfile.TemporaryDirectory(prefix="v09-full-regression-cache-") as cache:
            env = ex._controlled_python_env(cache)
            env["DDC_V09_FULL_REGRESSION_CHILD"] = "1"
            proc = subprocess.run(
                [sys.executable, "-E", "-s", "-S", "-m", "unittest", "discover", "-s", "tests", "-v"],
                text=True,
                capture_output=True,
                env=env,
                timeout=180,
            )
        combined = proc.stdout + proc.stderr
        match = re.search(r"Ran\s+(\d+)\s+tests?", combined)
        self.assertIsNotNone(match, combined[-8000:])
        test_count = int(match.group(1))
        self.assertGreater(test_count, 0)
        self.assertEqual(proc.returncode, 0, combined[-8000:])
        self.assertRegex(combined, r"\bOK\b")

        module_manifest = json.dumps(actual_modules, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        module_sha256 = hashlib.sha256(module_manifest).hexdigest()
        output_sha256 = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        print(f"DDC_FULL_REGRESSION_TESTS={test_count}")
        print(f"DDC_FULL_REGRESSION_MODULES={len(actual_modules)}")
        print(f"DDC_FULL_REGRESSION_MODULES_SHA256={module_sha256}")
        print(f"DDC_FULL_REGRESSION_OUTPUT_SHA256={output_sha256}")


if __name__ == "__main__":
    unittest.main()
