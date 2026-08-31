from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock

from lab import ddcre_execution_provenance as prov
from lab import detector_oracle_v09_execution as execution


class DDCREExecutionProvenanceTests(unittest.TestCase):
    def _keypair(self, root: Path) -> tuple[Path, Path, str]:
        private_key = root / "private.pem"
        public_key = root / "public.pem"
        subprocess.run(
            ["/usr/bin/openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["/usr/bin/openssl", "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)],
            check=True,
            capture_output=True,
        )
        der = subprocess.run(
            ["/usr/bin/openssl", "pkey", "-pubin", "-in", str(public_key), "-outform", "DER"],
            check=True,
            capture_output=True,
        ).stdout
        return private_key, public_key, "sha256:" + hashlib.sha256(der).hexdigest()

    def _repo(self, root: Path) -> tuple[Path, str]:
        repo = root / "repo"
        subprocess.run(["/usr/bin/git", "init", "--quiet", str(repo)], check=True, capture_output=True)
        subprocess.run(["/usr/bin/git", "-C", str(repo), "config", "user.name", "v09 provenance test"], check=True)
        subprocess.run(["/usr/bin/git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
        (repo / "tracked.txt").write_text("exact bytes\n", encoding="utf-8")
        subprocess.run(["/usr/bin/git", "-C", str(repo), "add", "tracked.txt"], check=True)
        subprocess.run(["/usr/bin/git", "-C", str(repo), "commit", "--quiet", "-m", "fixture"], check=True)
        head = subprocess.run(
            ["/usr/bin/git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return repo, head

    def _sign(self, payload: dict, private_key: Path, fingerprint: str, root: Path) -> dict:
        raw = prov._canonical_bytes(payload)
        payload_path = root / "payload"
        signature_path = root / "signature"
        payload_path.write_bytes(raw)
        subprocess.run(
            [
                "/usr/bin/openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private_key),
                "-in", str(payload_path), "-out", str(signature_path),
            ],
            check=True,
            capture_output=True,
        )
        return {
            "schema": prov.SIGNED_SCHEMA,
            "algorithm": "ed25519",
            "key_fingerprint": fingerprint,
            "payload": payload,
            "signature_b64": base64.b64encode(signature_path.read_bytes()).decode("ascii"),
        }

    def _payload(self, repo: Path, head: str, output_parent: Path) -> dict:
        manifest = prov._source_manifest(repo)
        return {
            "schema": prov.PROVENANCE_SCHEMA,
            "issuer": "DDC Remote Executor",
            "executor_version": "0.6.1",
            "job_id": "a" * 32,
            "request_digest": "sha256:" + "b" * 64,
            "job_expires_at": (datetime.now(timezone.utc) + timedelta(minutes=20)).isoformat(),
            "action": prov.EXPECTED_ACTION,
            "authority_class": prov.EXPECTED_AUTHORITY,
            "repository": prov.EXPECTED_REPOSITORY,
            "source_repository": prov.EXPECTED_SOURCE_REPOSITORY,
            "authorized_ref": prov.EXPECTED_AUTHORIZED_REF,
            "revision": head,
            "tree_sha": manifest["tree_sha"],
            "source_manifest_sha256": manifest["source_manifest_sha256"],
            "tracked_files": manifest["tracked_files"],
            "source_directory_identity": prov._directory_identity(repo),
            "output_parent_identity": prov._directory_identity(output_parent),
            "profile": prov.EXPECTED_PROFILE,
            "entrypoint": prov.EXPECTED_ENTRYPOINT,
        }

    def test_valid_signed_exact_bound_provenance_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = self._repo(root)
            output_parent = root / "evidence"
            output_parent.mkdir()
            private_key, public_key, fingerprint = self._keypair(root)
            payload = self._payload(repo, head, output_parent)
            document = self._sign(payload, private_key, fingerprint, root)
            provenance_path = root / "provenance.json"
            provenance_path.write_text(json.dumps(document), encoding="utf-8")
            previous = Path.cwd()
            os.chdir(repo)
            try:
                with mock.patch.object(prov, "PROVENANCE_PATH", provenance_path), mock.patch.object(
                    prov, "PUBLIC_KEY_PATH", public_key
                ), mock.patch.object(prov, "EXPECTED_KEY_FINGERPRINT", fingerprint):
                    result = prov.verify_authorized_execution(head, output_parent / "bundle")
            finally:
                os.chdir(previous)
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(result["independently_verified_by_v09_runner"])
            self.assertEqual(result["revision"], head)

    def test_tampered_payload_fails_signature(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo, head = self._repo(root)
            output_parent = root / "evidence"
            output_parent.mkdir()
            private_key, public_key, fingerprint = self._keypair(root)
            payload = self._payload(repo, head, output_parent)
            document = self._sign(payload, private_key, fingerprint, root)
            document["payload"]["request_digest"] = "sha256:" + "c" * 64
            provenance_path = root / "provenance.json"
            provenance_path.write_text(json.dumps(document), encoding="utf-8")
            previous = Path.cwd()
            os.chdir(repo)
            try:
                with mock.patch.object(prov, "PROVENANCE_PATH", provenance_path), mock.patch.object(
                    prov, "PUBLIC_KEY_PATH", public_key
                ), mock.patch.object(prov, "EXPECTED_KEY_FINGERPRINT", fingerprint):
                    with self.assertRaisesRegex(prov.ProvenanceError, "SIGNATURE_INVALID"):
                        prov.verify_authorized_execution(head, output_parent / "bundle")
            finally:
                os.chdir(previous)

    def test_spoof_environment_flag_does_not_create_authority(self):
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(os.environ, {"DDCRE_LAUNCHED": "1"}, clear=False):
            missing = Path(td) / "does-not-exist"
            with mock.patch.object(prov, "PROVENANCE_PATH", missing), mock.patch.object(prov, "PUBLIC_KEY_PATH", missing):
                with self.assertRaisesRegex(prov.ProvenanceError, "MATERIAL_MISSING"):
                    prov.verify_authorized_execution("a" * 40, Path(td) / "bundle")

    def test_production_sha_blocks_before_local_tree_gate_without_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "bundle"
            with mock.patch.object(execution, "runtime_isolation", return_value={
                "ignore_environment": True,
                "no_user_site": True,
                "no_site": True,
                "passed": True,
            }), mock.patch.object(
                execution.ddcre_prov,
                "verify_authorized_execution",
                side_effect=prov.ProvenanceError("DDCRE_PROVENANCE_MATERIAL_MISSING"),
            ) as verify, mock.patch.object(execution, "exact_tree_identity") as identity:
                result = execution.execute(output, "a" * 40)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["reason"], "DDCRE_EXECUTION_PROVENANCE_FAILED")
            verify.assert_called_once()
            identity.assert_not_called()


if __name__ == "__main__":
    unittest.main()
