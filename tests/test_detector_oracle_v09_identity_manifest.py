import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lab import detector_oracle_v09_execution as ex


class DetectorOracleIdentityManifestTests(unittest.TestCase):
    def _manifest(self, root, head="abc"):
        files = {
            "lab/a.py": {"git_blob": "1" * 40, "mode": "100644"},
            "tests/b.py": {"git_blob": "2" * 40, "mode": "100644"},
        }
        return {
            "schema": "altru.dev/detector-oracle/executable-tree-manifest/0.9",
            "approved_head": head,
            "root_tree_sha": "3" * 40,
            "lab_tree_sha": ex._tree_sha([("a.py", "100644", "1" * 40)]),
            "tests_tree_sha": ex._tree_sha([("b.py", "100644", "2" * 40)]),
            "files": files,
        }

    def test_tree_hash_matches_git_tree_encoding(self):
        self.assertEqual(
            ex._tree_sha([("a.py", "100644", "1" * 40)]),
            ex._tree_sha([("a.py", "100644", "1" * 40)]),
        )
        self.assertNotEqual(
            ex._tree_sha([("a.py", "100644", "1" * 40)]),
            ex._tree_sha([("a.py", "100644", "2" * 40)]),
        )

    def test_manifest_head_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "manifest.json"
            p.write_text(json.dumps(self._manifest(td, head="other")), encoding="utf-8")
            with self.assertRaisesRegex(ex.ExecutionGateError, "IDENTITY_MANIFEST_HEAD_MISMATCH"):
                ex.executable_tree_identity("approved", p)

    def test_manifest_rejects_file_set_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lab").mkdir()
            (root / "tests").mkdir()
            (root / "lab" / "a.py").write_text("x=1\n", encoding="utf-8")
            (root / "tests" / "b.py").write_text("x=2\n", encoding="utf-8")
            (root / "tests" / "extra.py").write_text("x=3\n", encoding="utf-8")
            p = root / "manifest.json"
            p.write_text(json.dumps(self._manifest(root)), encoding="utf-8")
            old = Path.cwd()
            try:
                import os
                os.chdir(root)
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTABLE_FILE_SET_MISMATCH"):
                    ex.executable_tree_identity("abc", p)
            finally:
                os.chdir(old)

    def test_manifest_rejects_blob_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lab").mkdir()
            (root / "tests").mkdir()
            (root / "lab" / "a.py").write_text("x=1\n", encoding="utf-8")
            (root / "tests" / "b.py").write_text("x=2\n", encoding="utf-8")
            p = root / "manifest.json"
            p.write_text(json.dumps(self._manifest(root)), encoding="utf-8")
            old = Path.cwd()
            try:
                import os
                os.chdir(root)
                with self.assertRaisesRegex(ex.ExecutionGateError, "EXECUTABLE_BLOB_MISMATCH"):
                    ex.executable_tree_identity("abc", p)
            finally:
                os.chdir(old)

    def test_execute_uses_manifest_identity_when_supplied(self):
        identity = {
            "identity_mode": "VERIFIED_EXECUTABLE_TREE_MANIFEST",
            "head": "abc", "expected_head": "abc",
            "root_tree_sha": "r", "lab_tree_sha": "l", "tests_tree_sha": "t",
            "manifest_sha256": "m", "git_blobs": {}, "file_sha256": {},
        }
        compile_result = {"passed": False, "returncode": 1, "output_sha256": "x"}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ex, "executable_tree_identity", return_value=identity) as ident, patch.object(ex, "compile_gate", return_value=compile_result):
                result = ex.execute(td, "abc", "manifest.json")
            ident.assert_called_once_with("abc", "manifest.json")
            self.assertFalse(result["canonical"])
            self.assertEqual(result["reason"], "COMPILE_FAILED")


if __name__ == "__main__":
    unittest.main()
