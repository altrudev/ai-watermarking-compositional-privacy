from __future__ import annotations

from statistics import median

from lab.open_set_attribution_v08 import (
    MODES,
    POLICIES,
    SCENARIOS,
    STATES,
    TRANSFERS,
    Evaluator,
    calibrate,
    classify,
    controls,
    holdout,
    parity,
    prepare,
    records,
    stable_hash,
    transfer_summary,
)


def _five_number(values):
    rows = sorted(v for v in values if v is not None)
    if not rows:
        return None
    n = len(rows)

    def pick(frac):
        return rows[round((n - 1) * frac)]

    return {
        "min": rows[0],
        "q25": pick(0.25),
        "median": median(rows),
        "q75": pick(0.75),
        "max": rows[-1],
        "count": n,
    }


def _candidate_counts(rows):
    result = {}
    for row in rows:
        key = str(row["candidate_count"])
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def _forced_choice(rows, known):
    with_candidate = [row for row in rows if row["candidate_count"] > 0]
    result = {
        "candidate_survival_rate": len(with_candidate) / len(rows) if rows else 0.0,
        "candidate_count_distribution": _candidate_counts(rows),
        "top1_score": _five_number([row["top1_score"] for row in rows]),
        "top1_margin": _five_number([row["margin"] for row in rows]),
    }
    if known:
        result.update(
            {
                "person_top1": sum(row["predicted_person_correct"] for row in rows) / len(rows) if rows else 0.0,
                "generation_top1": sum(row["predicted_generation_correct"] for row in rows) / len(rows) if rows else 0.0,
            }
        )
    else:
        result["unknown_forced_choice_attribution_rate"] = result["candidate_survival_rate"]
    return result


def evidence_holdout(known_rows, unknown_rows, calibration):
    evidence = {
        "forced_choice_known": _forced_choice(known_rows, True),
        "forced_choice_unknown": _forced_choice(unknown_rows, False),
        "score_separation": {
            "known_top1": _five_number([row["top1_score"] for row in known_rows]),
            "unknown_top1": _five_number([row["top1_score"] for row in unknown_rows]),
            "known_margin": _five_number([row["margin"] for row in known_rows]),
            "unknown_margin": _five_number([row["margin"] for row in unknown_rows]),
        },
    }
    if calibration["status"] != "FEASIBLE":
        return {
            "status": "CALIBRATION_INFEASIBLE",
            "ufir": None,
            "kcar": None,
            "kwar": None,
            "krr": None,
            "precision": None,
            "hs_ufir": None,
            "uper": None,
            "false_events": [],
            "high_score_false_events": [],
            "wrong_known_events": [],
            **evidence,
        }
    result = holdout(known_rows, unknown_rows, calibration)
    result.update(evidence)
    return result


def build_cell(scenario, state, policy, mode):
    evaluator = Evaluator(scenario["candidate_population"])
    truth = scenario["truth"]
    known_cal = records(evaluator, scenario["known_cal"], truth, "known_cal", state, mode, policy)
    unknown_cal = records(evaluator, scenario["u_cal"], truth, "u_cal", state, mode, policy)
    calibration = calibrate(known_cal, unknown_cal)
    known_hold = records(evaluator, scenario["known_hold"], truth, "known_hold", state, mode, policy)
    unknown_hold = records(evaluator, scenario["u_test"], truth, "u_test", state, mode, policy)
    return {
        "scenario": scenario["scenario"],
        "state": state,
        "policy": policy,
        "mode": mode,
        "calibration": calibration,
        "holdout": evidence_holdout(known_hold, unknown_hold, calibration),
    }


def narrowing_differentials(cells):
    index = {(row["scenario"], row["state"], row["policy"], row["mode"]): row for row in cells}
    rows = []
    for scenario in SCENARIOS:
        for state in STATES:
            for policy in POLICIES:
                base = index[(scenario, state, policy, "global")]
                for mode in MODES:
                    if mode == "global":
                        continue
                    current = index[(scenario, state, policy, mode)]
                    b = base["holdout"]
                    c = current["holdout"]
                    row = {
                        "scenario": scenario,
                        "state": state,
                        "policy": policy,
                        "mode": mode,
                        "base_status": b["status"],
                        "mode_status": c["status"],
                    }
                    if b["status"] == "EVALUATED" and c["status"] == "EVALUATED":
                        row.update(
                            {
                                "ufir_delta": c["ufir"] - b["ufir"],
                                "kcar_delta": c["kcar"] - b["kcar"],
                                "kwar_delta": c["kwar"] - b["kwar"],
                                "precision_delta": c["precision"] - b["precision"],
                                "true_person_filter_exclusion_delta": c["true_person_filter_exclusion_rate"] - b["true_person_filter_exclusion_rate"],
                            }
                        )
                    else:
                        row["comparison"] = "NOT_COMPARABLE_CALIBRATION_INFEASIBLE"
                    rows.append(row)
    return rows


def reference():
    scenarios = {name: prepare(name) for name in SCENARIOS}
    cells = []
    by_scenario = {name: [] for name in SCENARIOS}
    for name, scenario in scenarios.items():
        for state in STATES:
            for policy in POLICIES:
                for mode in MODES:
                    row = build_cell(scenario, state, policy, mode)
                    cells.append(row)
                    by_scenario[name].append(row)

    transfers = [transfer_summary(source, destination, by_scenario[source]) for source, destination in TRANSFERS]
    control_record = controls()
    parity_record = {
        name: {
            state: {policy: parity(name, state, policy) for policy in POLICIES}
            for state in STATES
        }
        for name in SCENARIOS
    }
    all_parity = all(
        value
        for scenario in parity_record.values()
        for state in scenario.values()
        for value in state.values()
    )
    cohorts = {
        name: {
            "K": sorted(scenarios[name]["K"]),
            "U_cal": sorted(scenarios[name]["Uc"]),
            "U_test": sorted(scenarios[name]["Ut"]),
            "K_sha256": stable_hash(sorted(scenarios[name]["K"])),
            "U_cal_sha256": stable_hash(sorted(scenarios[name]["Uc"])),
            "U_test_sha256": stable_hash(sorted(scenarios[name]["Ut"])),
            "candidate_generation_count": len(scenarios[name]["candidate_population"]),
            "scenario_parameters": dict(SCENARIOS[name]),
        }
        for name in SCENARIOS
    }
    classification = classify(cells, transfers, control_record["all_pass"] and all_parity)
    return {
        "schema": "altru.dev/open-set-false-attribution-reference/0.8",
        "scope": "synthetic-only",
        "cohorts": cohorts,
        "controls": control_record,
        "parity": parity_record,
        "all_parity_pass": all_parity,
        "cells": cells,
        "narrowing_differentials": narrowing_differentials(cells),
        "transfers": transfers,
        "classification": classification,
    }


def summary(report):
    cells = report["cells"]
    feasible = [row for row in cells if row["calibration"]["status"] == "FEASIBLE"]
    evaluated = [row for row in cells if row["holdout"]["status"] == "EVALUATED"]
    return {
        "classification": report["classification"],
        "core_cells": len(cells),
        "calibration_feasible": len(feasible),
        "calibration_infeasible": len(cells) - len(feasible),
        "evaluated_cells": len(evaluated),
        "cells_ufir_ge_10pct": sum(row["holdout"]["ufir"] >= 0.10 for row in evaluated),
        "cells_ufir_ge_20pct": sum(row["holdout"]["ufir"] >= 0.20 for row in evaluated),
        "cells_hs_ufir_ge_5pct": sum(row["holdout"]["hs_ufir"] >= 0.05 for row in evaluated),
        "median_ufir": median([row["holdout"]["ufir"] for row in evaluated]) if evaluated else None,
        "median_kcar": median([row["holdout"]["kcar"] for row in evaluated]) if evaluated else None,
        "median_kwar": median([row["holdout"]["kwar"] for row in evaluated]) if evaluated else None,
        "median_uper": median([row["holdout"]["uper"] for row in evaluated]) if evaluated else None,
        "controls_pass": report["controls"]["all_pass"],
        "parity_pass": report["all_parity_pass"],
        "transfer_summaries": [
            {
                "source": row["source"],
                "destination": row["destination"],
                "unavailable": row["unavailable"],
                "median_ufir": row["median_ufir"],
                "median_kcar": row["median_kcar"],
                "median_kwar": row["median_kwar"],
                "acceptable": row["acceptable"],
            }
            for row in report["transfers"]
        ],
    }
