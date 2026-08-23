from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
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


def exact_tree_identity():
    head = _git(["rev-parse", "HEAD"])
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
    )
    blobs = {}
    file_sha256 = {}
    for path in paths:
        blobs[path] = _git(["hash-object", path])
        file_sha256[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {"head": head, "git_blobs": blobs, "file_sha256": file_sha256}


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
        "equal_files": equal_files,
        "first_complete_manifest_sha256": first["complete_manifest_sha256"],
        "second_complete_manifest_sha256": second["complete_manifest_sha256"],
        "first_file_sha256": {name: hashlib.sha256(first[name]).hexdigest() for name in files},
        "second_file_sha256": {name: hashlib.sha256(second[name]).hexdigest() for name in files},
    }, first_ref


def _write_json(path, value):
    Path(path).write_text(ev.canonical_json(value) + "\n", encoding="utf-8")


def _write_jsonl(path, records):
    rows = sorted(records, key=ev.canonical_json)
    Path(path).write_text("\n".join(ev.canonical_json(r) for r in rows) + ("\n" if rows else ""), encoding="utf-8")


def finalize_reference(reference, identity, compile_result, regression_result, replay_result):
    final = deepcopy(reference)
    summary = final["summary"]
    candidate = summary.get("candidate_classification_before_execution_gate")
    gates_pass = bool(compile_result["passed"] and regression_result["passed"] and replay_result["passed"])
    summary["complete_replay_control"] = "PASS" if replay_result["passed"] else "FAIL"
    summary["exact_execution_gate"] = "PASS" if gates_pass else "FAIL"
    summary["classification"] = candidate if gates_pass else "CONTROL_FAILED"
    summary["execution_identity"] = {
        "head": identity["head"],
        "git_blobs": identity["git_blobs"],
        "file_sha256": identity["file_sha256"],
        "python_version": sys.version,
        "python_executable": sys.executable,
    }
    summary["execution_proof"] = {
        "compile_passed": compile_result["passed"],
        "regression_passed": regression_result["passed"],
        "test_count": regression_result["test_count"],
        "test_output_sha256": regression_result["output_sha256"],
        "replay_passed": replay_result["passed"],
        "replay_manifest_sha256": replay_result["first_complete_manifest_sha256"],
    }
    summary.pop("summary_sha256", None)
    summary["summary_sha256"] = ev.sha256_text(ev.canonical_json(summary))
    return final


def write_final_bundle(output_dir, reference, execution_record):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _write_json(out / "summary.json", reference["summary"])
    _write_jsonl(out / "represented-evidence.jsonl", reference["represented_evidence"])
    _write_jsonl(out / "unknown-evidence.jsonl", reference["unknown_evidence"])
    _write_jsonl(out / "comparisons.jsonl", reference["comparisons"])
    _write_jsonl(out / "m5.jsonl", reference["m5"])
    _write_json(out / "execution-record.json", execution_record)

    filenames = (
        "summary.json", "represented-evidence.jsonl", "unknown-evidence.jsonl",
        "comparisons.jsonl", "m5.jsonl", "execution-record.json",
    )
    hashes = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in filenames}
    manifest = {
        "files": hashes,
        "canonical": bool(reference["summary"]["exact_execution_gate"] == "PASS"),
        "classification": reference["summary"]["classification"],
        "head": reference["summary"]["execution_identity"]["head"],
    }
    manifest_bytes = (ev.canonical_json(manifest) + "\n").encode("utf-8")
    (out / "manifest.json").write_bytes(manifest_bytes)
    return {
        "output_dir": str(out),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "canonical": manifest["canonical"],
        "classification": manifest["classification"],
    }


def _blocked(output_dir, reason, **evidence):
    blocked = {"status": "BLOCKED", "reason": reason, "canonical": False, **evidence}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    _write_json(Path(output_dir) / "execution-gate.json", blocked)
    return blocked


def execute(output_dir):
    try:
        identity_before = exact_tree_identity()
    except ExecutionGateError as exc:
        return _blocked(output_dir, str(exc))

    compile_result = compile_gate()
    if not compile_result["passed"]:
        return _blocked(output_dir, "COMPILE_FAILED", identity=identity_before, compile=compile_result)

    regression_result = regression_gate()
    if not regression_result["passed"]:
        return _blocked(output_dir, "REGRESSION_FAILED", identity=identity_before, compile=compile_result, regression=regression_result)

    replay_result, candidate_reference = replay_gate()

    try:
        identity_after = exact_tree_identity()
    except ExecutionGateError as exc:
        return _blocked(
            output_dir, "EXECUTION_TREE_NOT_CLEAN_AFTER_RUN",
            underlying_reason=str(exc), identity_before=identity_before,
            compile=compile_result, regression=regression_result, replay=replay_result,
        )
    if identity_after != identity_before:
        return _blocked(
            output_dir, "EXECUTION_TREE_CHANGED",
            identity_before=identity_before, identity_after=identity_after,
            compile=compile_result, regression=regression_result, replay=replay_result,
        )

    execution_record = {
        "status": "PASS" if replay_result["passed"] else "BLOCKED",
        "canonical": bool(replay_result["passed"]),
        "identity_before": identity_before,
        "identity_after": identity_after,
        "python_version": sys.version,
        "compile": compile_result,
        "regression": regression_result,
        "replay": replay_result,
        "mitigation_status": ev.MITIGATION_STATUS,
        "exploratory_status": ev.EXPLORATORY_STATUS,
    }
    final = finalize_reference(candidate_reference, identity_before, compile_result, regression_result, replay_result)
    result = write_final_bundle(output_dir, final, execution_record)
    result["status"] = "PASS" if result["canonical"] else "BLOCKED"
    return result


def main():
    parser = argparse.ArgumentParser(description="Run the exact-head DDC gate and v0.9 detector-oracle synthetic reference.")
    parser.add_argument("--output", required=True, help="Directory for execution evidence. Prefer a path outside the Git worktree.")
    args = parser.parse_args()
    result = execute(args.output)
    print(ev.canonical_json(result))
    return 0 if result.get("canonical") else 2


if __name__ == "__main__":
    raise SystemExit(main())
