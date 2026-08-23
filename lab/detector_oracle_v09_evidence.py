from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import median
import hashlib
import json

from lab import detector_oracle_v09 as core

EVIDENCE_AMENDMENT = "3b0bfb712f41a3112fbb1d3c3019ceff89f63713"
EVIDENCE_AUDIT_PASS = "59374595c41e4c3732d5eb5b1a117c9623884075"
MITIGATION_STATUS = "NOT_EVALUABLE_UNDER_V0.9"
EXPLORATORY_STATUS = "EXPLORATORY_SENSITIVITY_MATRIX_NOT_EXECUTED"

INVALID_REASON = {
    "posterior underflow": "POSTERIOR_NORMALIZATION_UNDERFLOW",
    "evidence underflow": "EVIDENCE_NORMALIZATION_UNDERFLOW",
    "template length mismatch": "OBSERVATION_TEMPLATE_LENGTH_MISMATCH",
}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=list)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_records(records):
    rows = sorted(records, key=lambda r: (
        str(r.get("scenario", "")), str(r.get("artifact_id", "")),
        str(r.get("disclosure", "")), str(r.get("policy", "")),
        int(r.get("budget", 0)), str(r.get("state", "")), str(r.get("evidence", "")),
    ))
    return sha256_text("\n".join(canonical_json(r) for r in rows) + ("\n" if rows else ""))


def _posterior_from_run(a, run, disclosure, policy, budget, state, evidence):
    templates = core.calibration_templates(a.scenario, disclosure, policy, budget, state)
    detector = core.detector_posterior(run.observation, templates)
    return core.combine_evidence(detector, a, evidence)


def artifact_evidence(a, disclosure, policy, budget, state, evidence, unknown=False):
    run = core.run_policy(a, disclosure, policy, budget)
    posterior = _posterior_from_run(a, run, disclosure, policy, budget, state, evidence)
    ranked = sorted(posterior.items(), key=lambda kv: (-kv[1], kv[0]))
    ent = core.entropy_bits(posterior)
    accepted, accepted_class, top_score, margin = core.open_set_accept(posterior)
    record = {
        "scenario": a.scenario,
        "true_k": a.k,
        "artifact_id": a.artifact_id,
        "state": state,
        "disclosure": disclosure,
        "policy": policy,
        "budget": budget,
        "evidence": evidence,
        "starting_score": core.hidden_score(a),
        "final_score": run.final_score,
        "detector_calls": run.detector_calls,
        "response_sha256": core.stable_hash(list(run.responses)),
        "path": list(run.path),
        "utility": run.utility,
        "posterior": {k: posterior[k] for k in core.REPRESENTED},
        "predicted": ranked[0][0],
        "correct": bool(a.k in core.REPRESENTED and ranked[0][0] == a.k),
        "entropy": ent,
        "information_gain": 2.0 - ent,
        "candidate_size": sum(v >= 0.10 for v in posterior.values()) or 4,
        "unknown": bool(unknown),
    }
    if unknown:
        record.update({
            "open_set_accepted": bool(accepted),
            "accepted_class": accepted_class if accepted else None,
            "top_posterior": top_score,
            "top_margin": margin,
        })
    return record


def _invalid_reason(exc):
    message = str(exc)
    for text, code in INVALID_REASON.items():
        if text in message:
            return code
    return None


def condition_evidence(scenario, disclosure, policy, budget, state, evidence, unknown=False):
    classes = core.UNKNOWN if unknown else core.REPRESENTED
    records = []
    try:
        for k in classes:
            for a in core.artifacts_for(scenario, k, range(8, 12), state):
                records.append(artifact_evidence(a, disclosure, policy, budget, state, evidence, unknown=unknown))
    except (ArithmeticError, ValueError) as exc:
        reason = _invalid_reason(exc)
        if reason is None:
            raise
        return {
            "status": "INVALID",
            "invalid_reason": reason,
            "scenario": scenario,
            "disclosure": disclosure,
            "policy": policy,
            "budget": budget,
            "state": state,
            "evidence": evidence,
            "unknown": bool(unknown),
            "evidence_count": len(records),
            "evidence_sha256": sha256_records(records),
        }, records

    summary = {
        "status": "EVALUATED",
        "invalid_reason": None,
        "scenario": scenario,
        "disclosure": disclosure,
        "policy": policy,
        "budget": budget,
        "state": state,
        "evidence": evidence,
        "unknown": bool(unknown),
        "evidence_count": len(records),
        "evidence_sha256": sha256_records(records),
        "median_utility": median(r["utility"] for r in records),
        "median_information_gain": median(r["information_gain"] for r in records),
        "median_candidate_size": median(r["candidate_size"] for r in records),
        "median_final_score": median(r["final_score"] for r in records),
    }
    if unknown:
        accepted = sum(bool(r["open_set_accepted"]) for r in records)
        summary.update({
            "accepted": accepted,
            "false_attribution_rate": accepted / len(records) if records else 0.0,
        })
    else:
        summary.update({
            "accuracy": sum(bool(r["correct"]) for r in records) / len(records) if records else 0.0,
        })
    return summary, records


def _represented_condition_specs():
    for scenario in core.SCENARIOS:
        for state in core.CORE_STATES:
            for evidence in core.CORE_EVIDENCE:
                for budget in core.BUDGETS:
                    yield scenario, "D0", "QF", budget, state, evidence
                    for disclosure in core.DISCLOSURES[1:]:
                        for policy in core.POLICIES:
                            yield scenario, disclosure, policy, budget, state, evidence


def _unknown_condition_specs():
    for scenario in core.SCENARIOS:
        for state in ("A0", "A4"):
            for evidence in core.CORE_EVIDENCE:
                for budget in core.BUDGETS:
                    yield scenario, "D0", "QF", budget, state, evidence
                    for disclosure in core.DISCLOSURES[1:]:
                        for policy in core.POLICIES:
                            yield scenario, disclosure, policy, budget, state, evidence


def represented_matrix():
    summaries, records = [], []
    for spec in _represented_condition_specs():
        summary, rows = condition_evidence(*spec, unknown=False)
        summaries.append(summary)
        records.extend(rows)
    return summaries, records


def unknown_matrix():
    summaries, records = [], []
    for spec in _unknown_condition_specs():
        summary, rows = condition_evidence(*spec, unknown=True)
        summaries.append(summary)
        records.extend(rows)
    return summaries, records


def _condition_index(summaries):
    return {(r["scenario"], r["disclosure"], r["policy"], r["budget"], r["state"], r["evidence"]): r for r in summaries}


def _comparison_record(test, baseline, comparison_type):
    if test["status"] != "EVALUATED" or baseline["status"] != "EVALUATED":
        return {
            "status": "INVALID",
            "invalid_reason": "MISSING_OR_INVALID_MATCHED_CONDITION",
            "comparison_type": comparison_type,
            "scenario": test["scenario"],
            "tested": [test["disclosure"], test["policy"], test["budget"], test["state"], test["evidence"]],
            "baseline": [baseline["disclosure"], baseline["policy"], baseline["budget"], baseline["state"], baseline["evidence"]],
        }
    info_delta = test["median_information_gain"] - baseline["median_information_gain"]
    accuracy_delta = test.get("accuracy", 0.0) - baseline.get("accuracy", 0.0)
    candidate_reduction = baseline["median_candidate_size"] - test["median_candidate_size"]
    return {
        "status": "EVALUATED",
        "invalid_reason": None,
        "comparison_type": comparison_type,
        "scenario": test["scenario"],
        "tested": [test["disclosure"], test["policy"], test["budget"], test["state"], test["evidence"]],
        "baseline": [baseline["disclosure"], baseline["policy"], baseline["budget"], baseline["state"], baseline["evidence"]],
        "information_gain_delta": info_delta,
        "accuracy_delta": accuracy_delta,
        "candidate_size_reduction": candidate_reduction,
        "utility_ok": bool(test["median_utility"] >= 0.80),
        "scenario_material_pass": bool(test["median_utility"] >= 0.80 and (info_delta >= 0.20 or accuracy_delta >= 0.10)),
    }


def matched_comparisons(represented_summaries):
    idx = _condition_index(represented_summaries)
    rows = []
    for test in represented_summaries:
        if test["disclosure"] == "D0":
            continue
        key = (test["scenario"], "D0", "QF", test["budget"], test["state"], test["evidence"])
        baseline = idx[key]
        rows.append(_comparison_record(test, baseline, "DETECTOR_VS_D0"))
        if test["policy"] in {"QA_REMOVE", "QA_SPOOF"}:
            qf = idx[(test["scenario"], test["disclosure"], "QF", test["budget"], test["state"], test["evidence"])]
            rows.append(_comparison_record(test, qf, "ADAPTIVE_VS_QF"))
    return rows


def m5_records():
    rows = []
    for scenario in core.SCENARIOS:
        for disclosure in core.DISCLOSURES[1:]:
            for budget in core.BUDGETS:
                for state in core.CORE_STATES:
                    per_artifact = []
                    for k in core.REPRESENTED:
                        for a in core.artifacts_for(scenario, k, range(8, 12), state):
                            qf = core.run_policy(a, disclosure, "QF", budget)
                            rm = core.run_policy(a, disclosure, "QA_REMOVE", budget)
                            sp = core.run_policy(a, disclosure, "QA_SPOOF", budget)
                            per_artifact.append({
                                "artifact_id": a.artifact_id,
                                "removal_advantage": qf.final_score - rm.final_score,
                                "spoof_advantage": sp.final_score - qf.final_score,
                            })
                    rows.append({
                        "scenario": scenario,
                        "disclosure": disclosure,
                        "budget": budget,
                        "state": state,
                        "artifact_count": len(per_artifact),
                        "artifact_values_sha256": sha256_records(per_artifact),
                        "median_removal_advantage": median(r["removal_advantage"] for r in per_artifact),
                        "median_spoof_advantage": median(r["spoof_advantage"] for r in per_artifact),
                        "artifact_values": per_artifact,
                    })
    return rows


def _replication_labels(comparisons, represented_summaries, unknown_summaries):
    by_family = defaultdict(set)
    binary = defaultdict(set)
    adaptive = defaultdict(set)
    invalid_family_scenarios = defaultdict(set)

    for row in comparisons:
        tested = row["tested"]
        d, p, budget, state, evidence = tested
        if row["comparison_type"] == "DETECTOR_VS_D0":
            family = (d, p, budget, state, evidence)
            if row["status"] != "EVALUATED":
                invalid_family_scenarios[family].add(row["scenario"])
                continue
            if row["scenario_material_pass"]:
                by_family[family].add(row["scenario"])
            if d == "D1" and p == "QF" and budget == 16 and row["scenario_material_pass"]:
                binary[(state, evidence)].add(row["scenario"])
        elif row["comparison_type"] == "ADAPTIVE_VS_QF":
            family = (d, p, budget, state, evidence)
            if row["status"] != "EVALUATED":
                continue
            if row["utility_ok"] and (row["information_gain_delta"] >= 0.10 or row["accuracy_delta"] >= 0.10):
                adaptive[family].add(row["scenario"])

    all_families = set()
    for d in core.DISCLOSURES[1:]:
        for p in core.POLICIES:
            for budget in core.BUDGETS:
                for state in core.CORE_STATES:
                    for evidence in core.CORE_EVIDENCE:
                        all_families.add((d, p, budget, state, evidence))

    invalid_families = []
    for family in all_families:
        comparable = 3 - len(invalid_family_scenarios.get(family, set()))
        if comparable < 2:
            invalid_families.append(family)
    invalid_ratio = len(invalid_families) / len(all_families) if all_families else 0.0

    material_families = sorted([list(k) for k, v in by_family.items() if len(v) >= 2])
    binary_families = sorted([list(k) for k, v in binary.items() if len(v) >= 2])
    adaptive_families = sorted([list(k) for k, v in adaptive.items() if len(v) >= 2])
    false_attr = any(r.get("status") == "EVALUATED" and int(r.get("accepted", 0)) > 0 for r in unknown_summaries)

    matrix_valid = invalid_ratio <= 0.20
    return {
        "material": bool(material_families) and matrix_valid,
        "binary": bool(binary_families) and matrix_valid,
        "adaptive": bool(adaptive_families) and matrix_valid,
        "mitigation": False,
        "mitigation_status": MITIGATION_STATUS,
        "false_attr": false_attr,
        "material_families": material_families,
        "binary_families": binary_families,
        "adaptive_families": adaptive_families,
        "invalid_families": [list(x) for x in sorted(invalid_families)],
        "invalid_family_ratio": invalid_ratio,
    }


def disclosure_parity_control():
    for scenario in core.SCENARIOS:
        for k in core.REPRESENTED + core.UNKNOWN:
            a = core.make_artifact(scenario, k, 0, 4, "A0")
            s = core.hidden_score(a)
            if core.disclose(a, a.z, "D1", 1) != ("DETECTED" if s >= 0.65 else "NOT_DETECTED"):
                return False
            if core.disclose(a, a.z, "D2", 1) != core._band(s):
                return False
            if core.disclose(a, a.z, "D3", 1) != round(s, 3):
                return False
            d4 = core.disclose(a, a.z, "D4", 1)
            if d4[0] != round(s, 3):
                return False
            d5 = core.disclose(a, a.z, "D5", 1)
            if d5[0] != round(s, 3) or d5[1] != core._distance_band(s):
                return False
            d6 = core.disclose(a, a.z, "D6", 1)
            n = core.map_hash(f"{a.scenario}|{a.artifact_id}|1|D6", -0.08, 0.08)
            if d6 != core._band(min(1.0, max(0.0, s+n))):
                return False
    return True


def build_reference():
    represented_summaries, represented_records = represented_matrix()
    unknown_summaries, unknown_records = unknown_matrix()
    comparisons = matched_comparisons(represented_summaries)
    m5 = m5_records()
    base_controls = core.controls()
    c3_full = disclosure_parity_control()
    labels = _replication_labels(comparisons, represented_summaries, unknown_summaries)
    control_pass = bool(base_controls["all_pass"] and c3_full)
    classification = core.classify_summary(
        control_pass,
        labels["material"], labels["binary"], labels["adaptive"], False, labels["false_attr"],
    )
    summary = {
        "protocol_lineage": {
            "base": core.PROTOCOL_BASE,
            "audit_fail": core.PROTOCOL_AUDIT_FAIL,
            "amendment_091": core.PROTOCOL_AMENDMENT_091,
            "amendment_092": core.PROTOCOL_AMENDMENT_092,
            "mapping_093": core.PROTOCOL_MAPPING_093,
            "audit_pass": core.PROTOCOL_AUDIT_PASS,
            "evidence_amendment_094": EVIDENCE_AMENDMENT,
            "evidence_audit_pass": EVIDENCE_AUDIT_PASS,
        },
        "controls": {**base_controls, "C3_FULL_DISCLOSURE_PARITY": c3_full},
        "complete_replay_control": "PENDING_SECOND_IDENTICAL_RUN",
        "represented_condition_count": len(represented_summaries),
        "unknown_condition_count": len(unknown_summaries),
        "represented_evidence_count": len(represented_records),
        "unknown_evidence_count": len(unknown_records),
        "comparison_count": len(comparisons),
        "m5_condition_count": len(m5),
        "labels": labels,
        "classification": classification,
        "mitigation_status": MITIGATION_STATUS,
        "exploratory_status": EXPLORATORY_STATUS,
        "represented_summaries": represented_summaries,
        "unknown_summaries": unknown_summaries,
    }
    hashes = {
        "represented_evidence_sha256": sha256_records(represented_records),
        "unknown_evidence_sha256": sha256_records(unknown_records),
        "comparisons_sha256": sha256_records(comparisons),
        "m5_sha256": sha256_records(m5),
    }
    summary["component_hashes"] = hashes
    summary["summary_sha256"] = sha256_text(canonical_json(summary))
    return {
        "summary": summary,
        "represented_evidence": represented_records,
        "unknown_evidence": unknown_records,
        "comparisons": comparisons,
        "m5": m5,
    }


def _jsonl_bytes(records):
    ordered = sorted(records, key=lambda r: canonical_json(r))
    return ("\n".join(canonical_json(r) for r in ordered) + ("\n" if ordered else "")).encode("utf-8")


def bundle_bytes(reference):
    summary_bytes = (canonical_json(reference["summary"]) + "\n").encode("utf-8")
    represented_bytes = _jsonl_bytes(reference["represented_evidence"])
    unknown_bytes = _jsonl_bytes(reference["unknown_evidence"])
    comparison_bytes = _jsonl_bytes(reference["comparisons"])
    m5_bytes = _jsonl_bytes(reference["m5"])
    file_hashes = {
        "summary.json": hashlib.sha256(summary_bytes).hexdigest(),
        "represented-evidence.jsonl": hashlib.sha256(represented_bytes).hexdigest(),
        "unknown-evidence.jsonl": hashlib.sha256(unknown_bytes).hexdigest(),
        "comparisons.jsonl": hashlib.sha256(comparison_bytes).hexdigest(),
        "m5.jsonl": hashlib.sha256(m5_bytes).hexdigest(),
    }
    manifest = {
        "files": file_hashes,
        "mitigation_status": MITIGATION_STATUS,
        "exploratory_status": EXPLORATORY_STATUS,
    }
    manifest_bytes = (canonical_json(manifest) + "\n").encode("utf-8")
    complete_hash = hashlib.sha256(manifest_bytes).hexdigest()
    return {
        "summary.json": summary_bytes,
        "represented-evidence.jsonl": represented_bytes,
        "unknown-evidence.jsonl": unknown_bytes,
        "comparisons.jsonl": comparison_bytes,
        "m5.jsonl": m5_bytes,
        "manifest.json": manifest_bytes,
        "complete_manifest_sha256": complete_hash,
    }


def replay_reference():
    first = bundle_bytes(build_reference())
    second = bundle_bytes(build_reference())
    keys = ("summary.json", "represented-evidence.jsonl", "unknown-evidence.jsonl", "comparisons.jsonl", "m5.jsonl", "manifest.json")
    equal = all(first[k] == second[k] for k in keys)
    return {
        "all_equal": equal,
        "first_complete_manifest_sha256": first["complete_manifest_sha256"],
        "second_complete_manifest_sha256": second["complete_manifest_sha256"],
        "file_sha256": {k: hashlib.sha256(first[k]).hexdigest() for k in keys},
    }


def write_bundle(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    reference = build_reference()
    payloads = bundle_bytes(reference)
    for name in ("summary.json", "represented-evidence.jsonl", "unknown-evidence.jsonl", "comparisons.jsonl", "m5.jsonl", "manifest.json"):
        (directory / name).write_bytes(payloads[name])
    return {
        "directory": str(directory),
        "complete_manifest_sha256": payloads["complete_manifest_sha256"],
        "summary_sha256": reference["summary"]["summary_sha256"],
    }
