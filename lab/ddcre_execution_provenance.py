from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile


class ProvenanceError(RuntimeError):
    pass


SIGNED_SCHEMA = "ddcre-signed-evidence/1"
PROVENANCE_SCHEMA = "ddcre-execution-provenance/1"
EXPECTED_KEY_FINGERPRINT = "sha256:dde78eb3e3f31f4767a1edce1dc47ad15094d4fb22b0174436d7a4f4355a11d8"
EXPECTED_REPOSITORY = "ai_watermarking_compositional_privacy"
EXPECTED_SOURCE_REPOSITORY = "https://github.com/altrudev/ai-watermarking-compositional-privacy.git"
EXPECTED_AUTHORIZED_REF = "refs/heads/agent/detector-oracle-v0.9-exact-byte-hardening"
EXPECTED_PROFILE = "watermarking.detector_oracle_hardening"
EXPECTED_ENTRYPOINT = "lab.detector_oracle_v09_execution:execute"
EXPECTED_ACTION = "research.detector_oracle_v09.execute_canonical"
EXPECTED_AUTHORITY = "BOUNDED_CANONICAL_RESEARCH_EXECUTE"
EXPECTED_PREEXECUTION_GATES = {
    "complete_regression": "PASS",
    "ddc_verification": "PASS",
    "source_identity_stable": "PASS",
}
PROVENANCE_PATH = Path("/run/ddcre/execution-provenance.json")
PUBLIC_KEY_PATH = Path("/run/ddcre/result-signing.pub")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")


def _canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _safe_env() -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": "/tmp/home",
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    }


def _fingerprint(public_key: Path) -> str:
    proc = subprocess.run(
        ["/usr/bin/openssl", "pkey", "-pubin", "-in", str(public_key), "-outform", "DER"],
        capture_output=True,
        timeout=10,
        env=_safe_env(),
    )
    if proc.returncode != 0:
        raise ProvenanceError("DDCRE_PROVENANCE_PUBLIC_KEY_READ_FAILED")
    return "sha256:" + hashlib.sha256(proc.stdout).hexdigest()


def _verify_envelope(document: object, public_key: Path) -> dict:
    if not isinstance(document, dict):
        raise ProvenanceError("DDCRE_PROVENANCE_ENVELOPE_NOT_OBJECT")
    if set(document) != {"schema", "algorithm", "key_fingerprint", "payload", "signature_b64"}:
        raise ProvenanceError("DDCRE_PROVENANCE_ENVELOPE_FIELDS_INVALID")
    if document.get("schema") != SIGNED_SCHEMA or document.get("algorithm") != "ed25519":
        raise ProvenanceError("DDCRE_PROVENANCE_ENVELOPE_INVALID")
    actual_fingerprint = _fingerprint(public_key)
    if actual_fingerprint != EXPECTED_KEY_FINGERPRINT:
        raise ProvenanceError("DDCRE_PROVENANCE_LOCAL_KEY_FINGERPRINT_MISMATCH")
    if document.get("key_fingerprint") != EXPECTED_KEY_FINGERPRINT:
        raise ProvenanceError("DDCRE_PROVENANCE_SIGNER_FINGERPRINT_MISMATCH")
    payload = document.get("payload")
    if not isinstance(payload, dict):
        raise ProvenanceError("DDCRE_PROVENANCE_PAYLOAD_NOT_OBJECT")
    try:
        signature = base64.b64decode(document.get("signature_b64", ""), validate=True)
    except Exception as exc:
        raise ProvenanceError("DDCRE_PROVENANCE_SIGNATURE_ENCODING_INVALID") from exc
    with tempfile.TemporaryDirectory(prefix="v09-ddcre-provenance-") as td:
        root = Path(td)
        payload_path = root / "payload"
        signature_path = root / "signature"
        payload_path.write_bytes(_canonical_bytes(payload))
        signature_path.write_bytes(signature)
        proc = subprocess.run(
            [
                "/usr/bin/openssl", "pkeyutl", "-verify", "-rawin", "-pubin",
                "-inkey", str(public_key), "-sigfile", str(signature_path), "-in", str(payload_path),
            ],
            capture_output=True,
            timeout=10,
            env=_safe_env(),
        )
    if proc.returncode != 0:
        raise ProvenanceError("DDCRE_PROVENANCE_SIGNATURE_INVALID")
    return payload


def _git(repo: Path, args: list[str], *, binary: bool = False):
    proc = subprocess.run(
        [
            "/usr/bin/git",
            "-c", f"safe.directory={repo}",
            "-c", "core.fsmonitor=false",
            "-c", "core.hooksPath=/dev/null",
            "-c", "core.excludesFile=/dev/null",
            "-C", str(repo),
            *args,
        ],
        capture_output=True,
        text=not binary,
        timeout=60,
        env=_safe_env(),
    )
    if proc.returncode != 0:
        raise ProvenanceError("DDCRE_PROVENANCE_GIT_IDENTITY_FAILED")
    return proc.stdout if binary else proc.stdout.strip()


def _directory_identity(path: Path) -> dict[str, int]:
    try:
        st = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise ProvenanceError("DDCRE_PROVENANCE_DIRECTORY_IDENTITY_UNAVAILABLE") from exc
    if not stat.S_ISDIR(st.st_mode):
        raise ProvenanceError("DDCRE_PROVENANCE_DIRECTORY_IDENTITY_TARGET_INVALID")
    return {"device": int(st.st_dev), "inode": int(st.st_ino)}


def _source_manifest(repo: Path) -> dict[str, object]:
    if _git(repo, ["status", "--porcelain=v1", "--untracked-files=all"]):
        raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_WORKTREE_DIRTY")
    head = _git(repo, ["rev-parse", "--verify", "HEAD"])
    tree_sha = _git(repo, ["rev-parse", "HEAD^{tree}"])
    raw_tree = _git(repo, ["ls-tree", "-r", "-z", "--full-tree", "HEAD"], binary=True)
    records: list[dict[str, str]] = []
    for raw in raw_tree.split(b"\0"):
        if not raw:
            continue
        try:
            meta, raw_path = raw.split(b"\t", 1)
            mode_b, type_b, blob_b = meta.split(b" ", 2)
            mode = mode_b.decode("ascii")
            object_type = type_b.decode("ascii")
            blob = blob_b.decode("ascii")
            rel = raw_path.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_TREE_ENTRY_INVALID") from exc
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_TREE_OBJECT_TYPE_NOT_ALLOWED")
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts or not rel_path.parts:
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_TREE_PATH_INVALID")
        path = repo / rel_path
        try:
            st = os.lstat(path)
        except FileNotFoundError as exc:
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_FILE_MISSING") from exc
        if not stat.S_ISREG(st.st_mode):
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_FILE_TYPE_INVALID")
        if (mode == "100755") != bool(st.st_mode & 0o111):
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_FILE_MODE_MISMATCH")
        data = path.read_bytes()
        actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if actual_blob != blob:
            raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_FILE_GIT_BLOB_MISMATCH")
        records.append({
            "path": rel,
            "mode": mode,
            "git_blob": blob,
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {
        "head": head,
        "tree_sha": tree_sha,
        "source_manifest_sha256": "sha256:" + hashlib.sha256(canonical).hexdigest(),
        "tracked_files": len(records),
    }


def _expiry(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ProvenanceError("DDCRE_PROVENANCE_EXPIRY_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProvenanceError("DDCRE_PROVENANCE_EXPIRY_INVALID") from exc
    if parsed.tzinfo is None:
        raise ProvenanceError("DDCRE_PROVENANCE_EXPIRY_UNZONED")
    return parsed.astimezone(timezone.utc)


def verify_authorized_execution(expected_head: str, output_dir: str | Path) -> dict[str, object]:
    if not isinstance(expected_head, str) or not SHA40.fullmatch(expected_head):
        raise ProvenanceError("DDCRE_PROVENANCE_EXPECTED_HEAD_INVALID")
    if not PROVENANCE_PATH.is_file() or not PUBLIC_KEY_PATH.is_file():
        raise ProvenanceError("DDCRE_PROVENANCE_MATERIAL_MISSING")

    raw = PROVENANCE_PATH.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ProvenanceError("DDCRE_PROVENANCE_DOCUMENT_INVALID") from exc
    payload = _verify_envelope(document, PUBLIC_KEY_PATH)

    required = {
        "schema", "issuer", "executor_version", "job_id", "request_digest", "job_expires_at",
        "action", "authority_class", "repository", "source_repository", "authorized_ref",
        "revision", "tree_sha", "source_manifest_sha256", "tracked_files",
        "source_directory_identity", "output_parent_identity", "profile", "entrypoint",
        "preexecution_gates", "complete_regression_sha256", "ddc_verification_sha256",
    }
    if set(payload) != required:
        raise ProvenanceError("DDCRE_PROVENANCE_PAYLOAD_FIELDS_INVALID")
    if payload.get("schema") != PROVENANCE_SCHEMA or payload.get("issuer") != "DDC Remote Executor":
        raise ProvenanceError("DDCRE_PROVENANCE_SCHEMA_INVALID")
    if payload.get("action") != EXPECTED_ACTION or payload.get("authority_class") != EXPECTED_AUTHORITY:
        raise ProvenanceError("DDCRE_PROVENANCE_AUTHORITY_INVALID")
    if payload.get("repository") != EXPECTED_REPOSITORY or payload.get("source_repository") != EXPECTED_SOURCE_REPOSITORY:
        raise ProvenanceError("DDCRE_PROVENANCE_REPOSITORY_INVALID")
    if payload.get("authorized_ref") != EXPECTED_AUTHORIZED_REF or payload.get("profile") != EXPECTED_PROFILE:
        raise ProvenanceError("DDCRE_PROVENANCE_POLICY_INVALID")
    if payload.get("entrypoint") != EXPECTED_ENTRYPOINT:
        raise ProvenanceError("DDCRE_PROVENANCE_ENTRYPOINT_INVALID")
    if payload.get("revision") != expected_head:
        raise ProvenanceError("DDCRE_PROVENANCE_REVISION_MISMATCH")
    if not isinstance(payload.get("tree_sha"), str) or not SHA40.fullmatch(payload["tree_sha"]):
        raise ProvenanceError("DDCRE_PROVENANCE_TREE_INVALID")
    if not isinstance(payload.get("request_digest"), str) or not SHA256.fullmatch(payload["request_digest"]):
        raise ProvenanceError("DDCRE_PROVENANCE_REQUEST_DIGEST_INVALID")
    if not isinstance(payload.get("source_manifest_sha256"), str) or not SHA256.fullmatch(payload["source_manifest_sha256"]):
        raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_MANIFEST_INVALID")
    if not isinstance(payload.get("tracked_files"), int) or payload["tracked_files"] <= 0:
        raise ProvenanceError("DDCRE_PROVENANCE_TRACKED_FILES_INVALID")
    if payload.get("preexecution_gates") != EXPECTED_PREEXECUTION_GATES:
        raise ProvenanceError("DDCRE_PROVENANCE_PREEXECUTION_GATES_INVALID")
    regression_digest = payload.get("complete_regression_sha256")
    if not isinstance(regression_digest, str) or not SHA256.fullmatch(regression_digest):
        raise ProvenanceError("DDCRE_PROVENANCE_REGRESSION_DIGEST_INVALID")
    ddc_digest = payload.get("ddc_verification_sha256")
    if not isinstance(ddc_digest, str) or not SHA256.fullmatch(ddc_digest):
        raise ProvenanceError("DDCRE_PROVENANCE_DDC_DIGEST_INVALID")
    if _expiry(payload.get("job_expires_at")) <= datetime.now(timezone.utc):
        raise ProvenanceError("DDCRE_PROVENANCE_EXPIRED")

    repo = Path.cwd().resolve()
    manifest = _source_manifest(repo)
    if manifest["head"] != expected_head:
        raise ProvenanceError("DDCRE_PROVENANCE_HEAD_MISMATCH")
    if manifest["tree_sha"] != payload["tree_sha"]:
        raise ProvenanceError("DDCRE_PROVENANCE_TREE_MISMATCH")
    if manifest["source_manifest_sha256"] != payload["source_manifest_sha256"]:
        raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_MANIFEST_MISMATCH")
    if manifest["tracked_files"] != payload["tracked_files"]:
        raise ProvenanceError("DDCRE_PROVENANCE_TRACKED_FILE_COUNT_MISMATCH")
    if payload.get("source_directory_identity") != _directory_identity(repo):
        raise ProvenanceError("DDCRE_PROVENANCE_SOURCE_DIRECTORY_IDENTITY_MISMATCH")

    output = Path(output_dir).expanduser()
    parent = output.parent.resolve()
    if payload.get("output_parent_identity") != _directory_identity(parent):
        raise ProvenanceError("DDCRE_PROVENANCE_OUTPUT_PARENT_IDENTITY_MISMATCH")

    return {
        "status": "PASS",
        "preimport_verified_by_ddcre_launcher": True,
        "independently_verified_by_v09_runner": True,
        "schema": payload["schema"],
        "job_id": payload["job_id"],
        "request_digest": payload["request_digest"],
        "job_expires_at": payload["job_expires_at"],
        "revision": payload["revision"],
        "tree_sha": payload["tree_sha"],
        "source_manifest_sha256": payload["source_manifest_sha256"],
        "tracked_files": payload["tracked_files"],
        "source_directory_identity": payload["source_directory_identity"],
        "output_parent_identity": payload["output_parent_identity"],
        "preexecution_gates": payload["preexecution_gates"],
        "complete_regression_sha256": regression_digest,
        "ddc_verification_sha256": ddc_digest,
        "key_fingerprint": EXPECTED_KEY_FINGERPRINT,
        "provenance_document_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "authority_class": payload["authority_class"],
        "action": payload["action"],
    }
