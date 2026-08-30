from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

from lab import detector_oracle_v09_evidence as ev


class ExecutionGateError(RuntimeError):
    pass


EXECUTED_ROOTS = ("lab", "tests")


def _run(args, env=None):
    p = subprocess.run(args, text=True, capture_output=True, env=env)
    return {
        "args": list(args),
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
        "output_sha256": hashlib.sha256((p.stdout + p.stderr).encode("utf-8")).hexdigest(),
    }


def _git_binary():
    for candidate in ("/usr/bin/git", "/bin/git"):
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return str(Path(candidate).resolve())
    found = shutil.which("git")
    if not found:
        raise ExecutionGateError("GIT_NOT_FOUND")
    return str(Path(found).resolve())


def _git_env():
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("GIT_"):
            env.pop(key, None)
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "LC_ALL": "C",
    })
    return env


def _git(args):
    r = _run([
        _git_binary(),
        "-c", "core.fsmonitor=false",
        "-c", "core.hooksPath=/dev/null",
        "-c", "core.excludesFile=/dev/null",
        *args,
    ], env=_git_env())
    if r["returncode"] != 0:
        raise ExecutionGateError("GIT_COMMAND_FAILED")
    return r["stdout"].strip()


def runtime_isolation():
    result = {
        "ignore_environment": bool(sys.flags.ignore_environment),
        "no_user_site": bool(sys.flags.no_user_site),
        "no_site": bool(sys.flags.no_site),
    }
    result["passed"] = all(result.values())
    return result


def _head_python_blobs():
    raw = _git(["ls-tree", "-r", "-z", "HEAD", "--", *EXECUTED_ROOTS])
    blobs = {}
    modes = {}
    for row in raw.split("\0"):
        if not row:
            continue
        meta, path = row.split("\t", 1)
        mode, kind, sha = meta.split(" ", 2)
        if kind != "blob" or not path.endswith(".py"):
            continue
        if mode not in {"100644", "100755"}:
            raise ExecutionGateError(f"UNSUPPORTED_EXECUTED_FILE_MODE:{path}")
        blobs[path] = sha
        modes[path] = mode
    if not blobs:
        raise ExecutionGateError("NO_TRACKED_PYTHON_FILES")
    return blobs, modes


def _actual_python_paths():
    paths = set()
    for root_name in EXECUTED_ROOTS:
        root = Path(root_name)
        if not root.is_dir():
            raise ExecutionGateError(f"EXECUTED_ROOT_MISSING:{root_name}")
        for path in root.rglob("*.py"):
            if path.is_file() or path.is_symlink():
                paths.add(path.as_posix())
    return paths


def _index_flags():
    flags = {}
    raw = _git(["ls-files", "-v", "--", *EXECUTED_ROOTS])
    for line in raw.splitlines():
        if len(line) < 3:
            continue
        tag = line[0]
        path = line[2:]
        if path.endswith(".py"):
            flags[path] = tag
    return flags


def exact_tree_identity(expected_head=None):
    repo_root = Path(_git(["rev-parse", "--show-toplevel"])).resolve()
    if repo_root != Path.cwd().resolve():
        raise ExecutionGateError("REPOSITORY_ROOT_MISMATCH")

    head = _git(["rev-parse", "--verify", "HEAD"])
    if expected_head is not None and head != expected_head:
        raise ExecutionGateError("EXPECTED_HEAD_MISMATCH")

    status = _git(["status", "--porcelain=v1", "--untracked-files=all"])
    if status:
        raise ExecutionGateError("WORKTREE_NOT_CLEAN")

    expected_blobs, modes = _head_python_blobs()
    actual_paths = _actual_python_paths()
    expected_paths = set(expected_blobs)
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        detail = ev.canonical_json({"missing": missing, "extra": extra})
        raise ExecutionGateError("EXECUTED_SOURCE_SET_MISMATCH:" + detail)

    flags = _index_flags()
    abnormal_flags = {path: flags.get(path) for path in sorted(expected_paths) if flags.get(path) != "H"}
    if abnormal_flags:
        raise ExecutionGateError("EXECUTED_INDEX_FLAGS_NOT_CLEAN:" + ev.canonical_json(abnormal_flags))

    actual_blobs = {}
    file_sha256 = {}
    for path in sorted(expected_paths):
        actual_blob = _git(["hash-object", "--no-filters", "--", path])
        expected_blob = expected_blobs[path]
        if actual_blob != expected_blob:
            raise ExecutionGateError(f"EXECUTED_BLOB_MISMATCH:{path}")
        actual_blobs[path] = actual_blob
        file_sha256[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()

    return {
        "head": head,
        "expected_head": expected_head,
        "head_tree": _git(["rev-parse", "HEAD^{tree}"]),
        "repo_root": str(repo_root),
        "git_executable": _git_binary(),
        "git_version": _git(["--version"]),
        "git_blobs": actual_blobs,
        "head_git_blobs": expected_blobs,
        "file_modes": modes,
        "index_flags": flags,
        "file_sha256": file_sha256,
    }


def _controlled_python_env(pycache_prefix):
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env.update({
        "PYTHONHASHSEED": "0",
        "PYTHONPYCACHEPREFIX": str(pycache_prefix),
    })
    return env


def compile_gate():
    files = sorted(str(p) for root in EXECUTED_ROOTS for p in Path(root).rglob("*.py") if p.is_file())
    if not files:
        raise ExecutionGateError("NO_PYTHON_FILES")
    with tempfile.TemporaryDirectory(prefix="v09-compile-cache-") as cache:
        result = _run(
            [sys.executable, "-S", "-s", "-m", "py_compile", *files],
            env=_controlled_python_env(cache),
        )
    result["runtime_controls"] = {
        "pythonpath_inherited": False,
        "site_import_disabled": True,
        "user_site_disabled": True,
        "pycache_outside_worktree": True,
        "pythonhashseed": "0",
    }
    result["passed"] = result["returncode"] == 0
    return result


def regression_gate():
    with tempfile.TemporaryDirectory(prefix="v09-regression-cache-") as cache:
        result = _run(
            [sys.executable, "-S", "-s", "-m", "unittest", "discover", "-s", "tests", "-v"],
            env=_controlled_python_env(cache),
        )
    combined = result["stdout"] + result["stderr"]
    m = re.search(r"Ran\s+(\d+)\s+tests?", combined)
    result["runtime_controls"] = {
        "pythonpath_inherited": False,
        "site_import_disabled": True,
        "user_site_disabled": True,
        "pycache_outside_worktree": True,
        "pythonhashseed": "0",
    }
    result["test_count"] = int(m.group(1)) if m else None
    result["passed"] = bool(
        result["returncode"] == 0
        and result["test_count"] is not None
        and result["test_count"] > 0
        and re.search(r"\bOK\b", combined)
    )
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


def _write_jsonl(path, records):
    rows = sorted(records, key=ev.canonical_json)
    Path(path).write_text("\n".join(ev.canonical_json(r) for r in rows) + ("\n" if rows else ""), encoding="utf-8")


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
        "head": identity["head"],
        "expected_head": identity.get("expected_head"),
        "head_tree": identity.get("head_tree"),
        "repo_root": identity.get("repo_root"),
        "git_executable": identity.get("git_executable"),
        "git_version": identity.get("git_version"),
        "git_blobs": identity["git_blobs"],
        "head_git_blobs": identity.get("head_git_blobs", {}),
        "file_modes": identity.get("file_modes", {}),
        "index_flags": identity.get("index_flags", {}),
        "file_sha256": identity["file_sha256"],
        "runtime_isolation": identity.get("runtime_isolation"),
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


def _write_new_bytes(path, data):
    target = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _output_target_is_fresh(output_dir):
    out = Path(output_dir).expanduser()
    if out.exists() or out.is_symlink():
        return False
    return out.parent.resolve().is_dir()


def verify_written_bundle(output_dir, expected_payloads):
    out = Path(output_dir).expanduser()
    expected_names = set(expected_payloads)
    result = {
        "passed": False,
        "control": "WRITTEN_BUNDLE_BYTE_IDENTITY",
        "output_dir": str(out),
        "expected_files": sorted(expected_names),
        "actual_files": [],
        "file_equal": {},
        "file_sha256": {},
    }
    if out.is_symlink() or not out.is_dir():
        return result
    actual_names = {path.name for path in out.iterdir()}
    result["actual_files"] = sorted(actual_names)
    if actual_names != expected_names:
        return result
    for name in sorted(expected_names):
        path = out / name
        if path.is_symlink() or not path.is_file():
            result["file_equal"][name] = False
            continue
        data = path.read_bytes()
        result["file_sha256"][name] = hashlib.sha256(data).hexdigest()
        result["file_equal"][name] = data == expected_payloads[name]
    result["passed"] = bool(result["file_equal"] and all(result["file_equal"].values()))
    return result


def _discard_output_dir(output_dir):
    out = Path(output_dir).expanduser()
    try:
        if out.is_symlink():
            out.unlink()
        elif out.exists():
            shutil.rmtree(out)
        return not (out.exists() or out.is_symlink())
    except OSError:
        return False


def write_final_bundle(output_dir, reference, execution_record, payloads=None):
    out = Path(output_dir).expanduser()
    out.mkdir(mode=0o700, parents=False, exist_ok=False)
    payloads = final_bundle_bytes(reference, execution_record) if payloads is None else payloads
    for name, data in payloads.items():
        _write_new_bytes(out / name, data)
    manifest_sha256 = hashlib.sha256(payloads["manifest.json"]).hexdigest()
    return {
        "output_dir": str(out),
        "manifest_sha256": manifest_sha256,
        "canonical": bool(reference["summary"]["exact_execution_gate"] == "PASS"),
        "classification": reference["summary"]["classification"],
    }


def _blocked(output_dir, reason, persist=True, **evidence):
    blocked = {"status": "BLOCKED", "reason": reason, "canonical": False, **evidence}
    if persist:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        _write_json(Path(output_dir) / "execution-gate.json", blocked)
    return blocked


def _output_is_outside_worktree(output_dir, repo_root):
    root = Path(repo_root).resolve()
    out = Path(output_dir).expanduser().resolve()
    return bool(out != root and root not in out.parents)


def execute(output_dir, expected_head):
    if not expected_head:
        return _blocked(output_dir, "EXPECTED_HEAD_REQUIRED")

    runtime = runtime_isolation()
    if not runtime["passed"]:
        return _blocked(
            output_dir,
            "PYTHON_RUNTIME_NOT_ISOLATED",
            runtime_isolation=runtime,
            required_python_flags=["-E", "-s", "-S"],
        )

    try:
        identity_before = exact_tree_identity(expected_head)
    except ExecutionGateError as exc:
        return _blocked(output_dir, str(exc), expected_head=expected_head)
    identity_before["runtime_isolation"] = runtime

    if not _output_is_outside_worktree(output_dir, identity_before["repo_root"]):
        return _blocked(
            output_dir,
            "OUTPUT_DIRECTORY_INSIDE_WORKTREE",
            persist=False,
            expected_head=expected_head,
            repo_root=identity_before["repo_root"],
            requested_output_dir=str(Path(output_dir).expanduser()),
        )

    if not _output_target_is_fresh(output_dir):
        return _blocked(
            output_dir,
            "OUTPUT_TARGET_NOT_FRESH",
            persist=False,
            expected_head=expected_head,
            requested_output_dir=str(Path(output_dir).expanduser()),
        )

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
        identity_after_reference = exact_tree_identity(expected_head)
    except ExecutionGateError as exc:
        return _blocked(
            output_dir, "EXECUTION_TREE_NOT_CLEAN_AFTER_REFERENCE_REPLAY",
            underlying_reason=str(exc), expected_head=expected_head, identity_before=identity_before,
            compile=compile_result, regression=regression_result, reference_replay=reference_replay_result,
        )
    identity_after_reference["runtime_isolation"] = runtime
    if identity_after_reference != identity_before:
        return _blocked(
            output_dir, "EXECUTION_TREE_CHANGED_AFTER_REFERENCE_REPLAY",
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
        "runtime_isolation": runtime,
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
        identity_after = exact_tree_identity(expected_head)
    except ExecutionGateError as exc:
        return _blocked(
            output_dir, "EXECUTION_TREE_NOT_CLEAN_AFTER_CANONICAL_REPLAY",
            underlying_reason=str(exc), expected_head=expected_head, identity_before=identity_before,
            compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result, canonical_bundle_replay=canonical_replay_result,
        )
    identity_after["runtime_isolation"] = runtime
    if identity_after != identity_before:
        return _blocked(
            output_dir, "EXECUTION_TREE_CHANGED",
            expected_head=expected_head, identity_before=identity_before, identity_after=identity_after,
            compile=compile_result, regression=regression_result,
            reference_replay=reference_replay_result, canonical_bundle_replay=canonical_replay_result,
        )

    final = finalize_reference(
        candidate_reference, identity_before, compile_result, regression_result,
        reference_replay_result, canonical_replay_result["passed"],
    )
    expected_payloads = final_bundle_bytes(final, execution_record)
    try:
        result = write_final_bundle(output_dir, final, execution_record, payloads=expected_payloads)
    except OSError as exc:
        discarded = _discard_output_dir(output_dir)
        return _blocked(
            output_dir, "FINAL_WRITE_FAILED", persist=False, expected_head=expected_head,
            write_error=f"{type(exc).__name__}:{exc}", output_discarded=discarded,
            canonical_bundle_replay=canonical_replay_result,
        )

    written = verify_written_bundle(output_dir, expected_payloads)
    replay_hash_match = bool(
        written["passed"]
        and all(
            written["file_sha256"].get(name) == canonical_replay_result["first_file_sha256"].get(name)
            for name in expected_payloads
        )
    )
    written["canonical_replay_sha256_match"] = replay_hash_match
    written["passed"] = bool(written["passed"] and replay_hash_match)
    if not written["passed"]:
        discarded = _discard_output_dir(output_dir)
        return _blocked(
            output_dir, "FINAL_WRITE_DIVERGED_FROM_CANONICAL_REPLAY", persist=False,
            expected_head=expected_head, written_bundle_verification=written,
            output_discarded=discarded, canonical_bundle_replay=canonical_replay_result,
        )

    try:
        identity_after_write = exact_tree_identity(expected_head)
    except ExecutionGateError as exc:
        discarded = _discard_output_dir(output_dir)
        return _blocked(
            output_dir, "EXECUTION_TREE_NOT_CLEAN_AFTER_FINAL_WRITE", persist=False,
            underlying_reason=str(exc), expected_head=expected_head, identity_before=identity_before,
            written_bundle_verification=written, output_discarded=discarded,
            canonical_bundle_replay=canonical_replay_result,
        )
    identity_after_write["runtime_isolation"] = runtime
    if identity_after_write != identity_before:
        discarded = _discard_output_dir(output_dir)
        return _blocked(
            output_dir, "EXECUTION_TREE_CHANGED_AFTER_FINAL_WRITE", persist=False,
            expected_head=expected_head, identity_before=identity_before, identity_after=identity_after_write,
            written_bundle_verification=written, output_discarded=discarded,
            canonical_bundle_replay=canonical_replay_result,
        )

    result["canonical_bundle_replay"] = canonical_replay_result
    result["written_bundle_verification"] = written
    result["identity_after_write"] = identity_after_write
    result["status"] = "PASS" if result["canonical"] else "BLOCKED"
    return result


def main():
    parser = argparse.ArgumentParser(description="Run the exact-head DDC gate and v0.9 detector-oracle synthetic reference.")
    parser.add_argument("--output", required=True, help="Fresh, non-existing directory for execution evidence; its parent must exist and it must resolve outside the Git worktree.")
    parser.add_argument("--expected-head", required=True, help="Exact DDC-approved implementation commit SHA. Execution fails closed on any other HEAD.")
    args = parser.parse_args()
    result = execute(args.output, args.expected_head)
    print(ev.canonical_json(result))
    return 0 if result.get("canonical") else 2


if __name__ == "__main__":
    raise SystemExit(main())
