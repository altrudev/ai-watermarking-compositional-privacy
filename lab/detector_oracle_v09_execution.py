from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

from lab import detector_oracle_v09_evidence as ev


class ExecutionGateError(RuntimeError):
    pass


def _run(args):
    p = subprocess.run(args, text=True, capture_output=True)
    return {
        "args": list(args),
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
        "output_sha256": hashlib.sha256((p.stdout + p.stderr).encode("utf-8")).hexdigest(),
    }


def _git(args):
    r = _run(["git", *args])
    if r["returncode"] != 0:
        raise ExecutionGateError("GIT_COMMAND_FAILED")
    return r["stdout"].strip()


def _git_blob_sha(path):
    r = _run(["git", "hash-object", "--no-filters", str(path)])
    if r["returncode"] != 0:
        raise ExecutionGateError("GIT_HASH_OBJECT_FAILED")
    return r["stdout"].strip()


def _tree_sha(entries):
    body = bytearray()
    for name, mode, sha in sorted(entries, key=lambda x: x[0].encode("utf-8")):
        body.extend(f"{mode} {name}".encode("utf-8"))
        body.append(0)
        body.extend(bytes.fromhex(sha))
    header = f"tree {len(body)}".encode("ascii") + b"\0"
    return hashlib.sha1(header + body).hexdigest()


def exact_tree_identity(expected_head=None):
    head = _git(["rev-parse", "HEAD"])
    if expected_head is not None and head != expected_head:
        raise ExecutionGateError("EXPECTED_HEAD_MISMATCH")
    status = _git(["status", "--porcelain"])
    if status:
        raise ExecutionGateError("WORKTREE_NOT_CLEAN")
    paths = (
        "lab/detector_oracle_v09.py",
        "lab/detector_oracle_v09_evidence.py",
        "lab/detector_oracle_v09_execution.py",
        "tests/test_detector_oracle_v09.py",
        "tests/test_detector_oracle_v09_evidence.py",
        "tests/test_detector_oracle_v09_execution.py",
        "tests/test_detector_oracle_v09_ddc_repairs.py",
    )
    blobs = {}
    file_sha256 = {}
    for path in paths:
        blobs[path] = _git(["hash-object", path])
        file_sha256[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {
        "identity_mode": "CLEAN_GIT_WORKTREE",
        "head": head,
        "expected_head": expected_head,
        "git_blobs": blobs,
        "file_sha256": file_sha256,
    }


def executable_tree_identity(expected_head, manifest_path):
    if not expected_head:
        raise ExecutionGateError("EXPECTED_HEAD_REQUIRED")
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("schema") != "altru.dev/detector-oracle/executable-tree-manifest/0.9":
        raise ExecutionGateError("IDENTITY_MANIFEST_SCHEMA_MISMATCH")
    if manifest.get("approved_head") != expected_head:
        raise ExecutionGateError("IDENTITY_MANIFEST_HEAD_MISMATCH")

    expected_files = manifest.get("files")
    if not isinstance(expected_files, dict) or not expected_files:
        raise ExecutionGateError("IDENTITY_MANIFEST_FILES_MISSING")
    actual_paths = sorted(
        str(p).replace("\\", "/")
        for root in ("lab", "tests")
        for p in Path(root).glob("*.py")
    )
    if actual_paths != sorted(expected_files):
        raise ExecutionGateError("EXECUTABLE_FILE_SET_MISMATCH")

    blobs = {}
    file_sha256 = {}
    for path in actual_paths:
        if not Path(path).is_file():
            raise ExecutionGateError("EXECUTABLE_FILE_MISSING")
        blob = _git_blob_sha(path)
        expected_blob = expected_files[path].get("git_blob")
        if blob != expected_blob:
            raise ExecutionGateError("EXECUTABLE_BLOB_MISMATCH")
        blobs[path] = blob
        file_sha256[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()

    observed_trees = {}
    for root, key in (("lab", "lab_tree_sha"), ("tests", "tests_tree_sha")):
        entries = []
        for path in actual_paths:
            p = Path(path)
            if p.parent.as_posix() != root:
                continue
            entries.append((p.name, expected_files[path].get("mode", "100644"), blobs[path]))
        observed = _tree_sha(entries)
        expected = manifest.get(key)
        if observed != expected:
            raise ExecutionGateError("EXECUTABLE_SUBTREE_MISMATCH")
        observed_trees[root] = observed

    return {
        "identity_mode": "VERIFIED_EXECUTABLE_TREE_MANIFEST",
        "head": expected_head,
        "expected_head": expected_head,
        "root_tree_sha": manifest.get("root_tree_sha"),
        "lab_tree_sha": observed_trees["lab"],
        "tests_tree_sha": observed_trees["tests"],
        "manifest_sha256": hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),
        "git_blobs": blobs,
        "file_sha256": file_sha256,
    }


def compile_gate():
    files = sorted(str(p) for root in ("lab", "tests") for p in Path(root).glob("*.py"))
    if not files:
        raise ExecutionGateError("NO_PYTHON_FILES")
    result = _run([sys.executable, "-m", "py_compile", *files])
    result["passed"] = result["returncode"] == 0
    return result


def regression_gate():
    result = _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    combined = result["stdout"] + result["stderr"]
    m = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    result["test_count"] = int(m.group(1)) if m else None
    result["passed"] = bool(result["returncode"] == 0 and re.search(r"\bOK\b", combined))
    return result


def replay_gate():
    first_ref = ev.build_reference()
    second_ref = ev.build_reference()
    first = ev.bundle_bytes(first_ref)
    second = ev.bundle_bytes(second_ref)
    files = ("summary.json", "represented-evidence.jsonl", "unknown-evidence.jsonl", "comparisons.jsonl", "m5.jsonl", "manifest.json")
    equal_files = {name: first[name] == second[name] for name in files}
    passed = all(equal_files.values()) and first["complete_manifest_sha256"] == second["complete_manifest_sha256"]
    return {
        "passed": passed,
        "control": "REFERENCE_REPLAY",
        "equal_files": equal_files,
        "first_complete_manifest_sha256": first["complete_manifest_sha256"],
        "second_complete_manifest_sha256": second["complete_manifest_sha256"],
        "first_file_sha256": {name: hashlib.sha256(first[name]).hexdigest() for name in files},
        "second_file_sha256": {name: hashlib.sha256(second[name]).hexdigest() for name in files},
    }, first_ref


def _write_json(path, value):
    Path(path).write_text(ev.canonical_json(value) + "\n", encoding="utf-8")


def finalize_reference(reference, identity, compile_result, regression_result, reference_replay_result, canonical_bundle_replay_passed):
    final = deepcopy(reference)
    summary = final["summary"]
    candidate = summary.get("candidate_classification_before_execution_gate")
    gates_pass = bool(
        compile_result["passed"]
        and regression_result["passed"]
        and reference_replay_result["passed"]
        and canonical_bundle_replay_passed
    )
    replay_status = "PASS" if canonical_bundle_replay_passed else "FAIL"
    summary["reference_replay_control"] = "PASS" if reference_replay_result["passed"] else "FAIL"
    summary["complete_replay_control"] = replay_status
    summary.setdefault("controls", {})["C8_COMPLETE_REPLAY"] = replay_status
    summary["exact_execution_gate"] = "PASS" if gates_pass else "FAIL"
    summary["classification"] = candidate if gates_pass else "CONTROL_FAILED"
    summary["execution_identity"] = {
        **identity,
        "python_version": sys.version,
        "python_executable": sys.executable,
    }
    summary["execution_proof"] = {
        "compile_passed": compile_result["passed"],
        "regression_passed": regression_result["passed"],
        "test_count": regression_result["test_count"],
        "test_output_sha256": regression_result["output_sha256"],
        "reference_replay_passed": reference_replay_result["passed"],
        "reference_replay_manifest_sha256": reference_replay_result["first_complete_manifest_sha256"],
        "canonical_bundle_replay_passed": canonical_bundle_replay_passed,
    }
    summary.pop("summary_sha256", None)
    summary["summary_sha256"] = ev.sha256_text(ev.canonical_json(summary))
    return final


def final_bundle_bytes(reference, execution_record):
    payloads = {
        "summary.json": (ev.canonical_json(reference["summary"]) + "\n").encode("utf-8"),
        "represented-evidence.jsonl": ev._jsonl_bytes(reference["represented_evidence"]),
        "unknown-evidence.jsonl": ev._jsonl_bytes(reference["unknown_evidence"]),
        "comparisons.jsonl": ev._jsonl_bytes(reference["comparisons"]),
        "m5.jsonl": ev._jsonl_bytes(reference["m5"]),
        "execution-record.json": (ev.canonical_json(execution_record) + "\n").encode("utf-8"),
    }
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    manifest = {
        "files": hashes,
        "canonical": bool(reference["summary"]["exact_execution_gate"] == "PASS"),
        "classification": reference["summary"]["classification"],
        "head": reference["summary"]["execution_identity"]["head"],
        "expected_head": reference["summary"]["execution_identity"].get("expected_head"),
        "identity_mode": reference["summary"]["execution_identity"].get("identity_mode"),
    }
    payloads["manifest.json"] = (ev.canonical_json(manifest) + "\n").encode("utf-8")
    return payloads


def canonical_bundle_replay(reference, execution_record):
    first = final_bundle_bytes(reference, execution_record)
    second = final_bundle_bytes(deepcopy(reference), deepcopy(execution_record))
    files = tuple(sorted(first))
    equal_files = {name: first[name] == second[name] for name in files}
    passed = all(equal_files.values())
    return {
        "passed": passed,
        "control": "CANONICAL_BUNDLE_REPLAY",
        "equal_files": equal_files,
        "first_file_sha256": {name: hashlib.sha256(first[name]).hexdigest() for name in files},
        "second_file_sha256": {name: hashlib.sha256(second[name]).hexdigest() for name in files},
        "first_manifest_sha256": hashlib.sha256(first["manifest.json"]).hexdigest(),
        "second_manifest_sha256": hashlib.sha256(second["manifest.json"]).hexdigest(),
    }


def write_final_bundle(output_dir, reference, execution_record):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    payloads = final_bundle_bytes(reference, execution_record)
    for name, data in payloads.items():
        (out / name).write_bytes(data)
    manifest_sha256 = hashlib.sha256(payloads["manifest.json"]).hexdigest()
    return {
        "output_dir": str(out),
        "manifest_sha256": manifest_sha256,
        "canonical": bool(reference["summary"]["exact_execution_gate"] == "PASS"),
        "classification": reference["summary"]["classification"],
    }


def _blocked(output_dir, reason, **evidence):
    blocked = {"status": "BLOCKED", "reason": reason, "canonical": False, **evidence}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    _write_json(Path(output_dir) / "execution-gate.json", blocked)
    return blocked


def execute(output_dir, expected_head, identity_manifest=None):
    if not expected_head:
        return _blocked(output_dir, "EXPECTED_HEAD_REQUIRED")

    def identity_check():
        if identity_manifest:
            return executable_tree_identity(expected_head, identity_manifest)
        return exact_tree_identity(expected_head)

    try:
        identity_before = identity_check()
    except ExecutionGateError as exc:
        return _blocked(output_dir, str(exc), expected_head=expected_head)

    compile_result = compile_gate()
    if not compile_result["passed"]:
        return _blocked(output_dir, "COMPILE_FAILED", expected_head=expected_head, identity=identity_before, compile=compile_result)

    regression_result = regression_gate()
    if not regression_result["passed"]:
        return _blocked(output_dir, "REGRESSION_FAILED", expected_head=expected_head, identity=identity_before, compile=compile_result, regression=regression_result)

    reference_replay_result, candidate_reference = replay_gate()
    if not reference_replay_result["passed"]:
        return _blocked(
            output_dir, "REFERENCE_REPLAY_FAILED", expected_head=expected_head,
            identity=identity_before, compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result,
        )

    try:
        identity_after_reference = identity_check()
    except ExecutionGateError as exc:
        return _blocked(
            output_dir, "EXECUTION_IDENTITY_CHANGED_AFTER_REFERENCE_REPLAY",
            underlying_reason=str(exc), expected_head=expected_head, identity_before=identity_before,
            compile=compile_result, regression=regression_result, reference_replay=reference_replay_result,
        )
    if identity_after_reference != identity_before:
        return _blocked(
            output_dir, "EXECUTION_IDENTITY_CHANGED_AFTER_REFERENCE_REPLAY",
            expected_head=expected_head, identity_before=identity_before, identity_after=identity_after_reference,
            compile=compile_result, regression=regression_result, reference_replay=reference_replay_result,
        )

    provisional_final = finalize_reference(
        candidate_reference, identity_before, compile_result, regression_result,
        reference_replay_result, True,
    )
    execution_record = {
        "status": "PASS",
        "canonical": True,
        "expected_head": expected_head,
        "identity_before": identity_before,
        "identity_after_reference_replay": identity_after_reference,
        "python_version": sys.version,
        "compile": compile_result,
        "regression": regression_result,
        "reference_replay": reference_replay_result,
        "mitigation_status": ev.MITIGATION_STATUS,
        "exploratory_status": ev.EXPLORATORY_STATUS,
    }
    canonical_replay_result = canonical_bundle_replay(provisional_final, execution_record)
    if not canonical_replay_result["passed"]:
        return _blocked(
            output_dir, "CANONICAL_BUNDLE_REPLAY_FAILED", expected_head=expected_head,
            identity=identity_before, compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result, canonical_bundle_replay=canonical_replay_result,
        )

    try:
        identity_after = identity_check()
    except ExecutionGateError as exc:
        return _blocked(
            output_dir, "EXECUTION_IDENTITY_CHANGED_AFTER_CANONICAL_REPLAY",
            underlying_reason=str(exc), expected_head=expected_head, identity_before=identity_before,
            compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result, canonical_bundle_replay=canonical_replay_result,
        )
    if identity_after != identity_before:
        return _blocked(
            output_dir, "EXECUTION_IDENTITY_CHANGED",
            expected_head=expected_head, identity_before=identity_before, identity_after=identity_after,
            compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result, canonical_bundle_replay=canonical_replay_result,
        )

    final = finalize_reference(
        candidate_reference, identity_before, compile_result, regression_result,
        reference_replay_result, canonical_replay_result["passed"],
    )
    result = write_final_bundle(output_dir, final, execution_record)
    final_payloads = final_bundle_bytes(final, execution_record)
    if any(hashlib.sha256(final_payloads[name]).hexdigest() != canonical_replay_result["first_file_sha256"][name] for name in final_payloads):
        return _blocked(
            output_dir, "FINAL_WRITE_DIVERGED_FROM_CANONICAL_REPLAY", expected_head=expected_head,
            canonical_bundle_replay=canonical_replay_result,
        )
    result["canonical_bundle_replay"] = canonical_replay_result
    result["status"] = "PASS" if result["canonical"] else "BLOCKED"
    return result


def main():
    parser = argparse.ArgumentParser(description="Run the DDC gate and v0.9 detector-oracle synthetic reference.")
    parser.add_argument("--output", required=True, help="Directory for execution evidence. Prefer a path outside the executable tree.")
    parser.add_argument("--expected-head", required=True, help="Exact DDC-approved implementation commit SHA.")
    parser.add_argument("--identity-manifest", help="Optional DDC-approved executable-tree manifest for environments that cannot materialize a full Git checkout.")
    args = parser.parse_args()
    result = execute(args.output, args.expected_head, args.identity_manifest)
    print(ev.canonical_json(result))
    return 0 if result.get("canonical") else 2


if __name__ == "__main__":
    raise SystemExit(main())
