from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
from math import exp, log2
from statistics import median
import hashlib
import json

PROTOCOL_BASE = "da81f93f7e275d2e87358c8e359a5dd529c7d98d"
PROTOCOL_AUDIT_FAIL = "3a4dbe99b29b644c665748a8999e9d8813acf7d2"
PROTOCOL_AMENDMENT_091 = "74bb5332031dbfe1ddfdb03fa827130f3be88599"
PROTOCOL_AMENDMENT_092 = "71709514e5e109aa947887a1dccdf5f0b28a98db"
PROTOCOL_MAPPING_093 = "353ec2fc0073c574b6615465ccb02ac863941dd1"
PROTOCOL_AUDIT_PASS = "ecee93170bfa4f8099e6eb9d1c844ef85f27a19a"

REPRESENTED = ("K1", "K2", "K3", "K4")
UNKNOWN = ("K0", "K5", "K6", "K7")
BASE = {
    "K0": -2.40, "K1": 0.60, "K2": 0.70, "K3": 0.75,
    "K4": 0.80, "K5": 0.85, "K6": 0.90, "K7": 0.95,
}
ALPHA = {
    "K0": (0.0, 0.0, 0.0, 0.0, 0.0),
    "K1": (0.45, -0.20, 0.10, 0.05, -0.05),
    "K2": (-0.15, 0.50, -0.10, 0.10, 0.05),
    "K3": (0.10, -0.10, 0.55, -0.20, 0.05),
    "K4": (0.05, 0.10, -0.15, 0.55, -0.10),
    "K5": (-0.10, 0.05, 0.10, -0.15, 0.60),
    "K6": (0.35, 0.35, -0.20, 0.10, 0.10),
    "K7": (0.30, -0.25, 0.30, -0.25, 0.30),
}
STATE_OFFSET = {"A0": 0.0, "A1": -0.25, "A2": -0.45, "A3": -0.65, "A4": 0.40}
BASE_UTILITY = {"A0": 1.00, "A1": 0.97, "A2": 0.95, "A3": 0.92, "A4": 0.96}
EDITS = {
    "P1": (0.18, -0.05, 0.0, 0.0, 0.0),
    "P2": (0.0, 0.18, -0.05, 0.0, 0.0),
    "P3": (0.0, 0.0, 0.18, -0.05, 0.0),
    "P4": (-0.05, 0.0, 0.0, 0.18, 0.0),
    "P5": (0.0, -0.05, 0.0, 0.0, 0.18),
}
SCENARIOS = {
    "S1": {"represented_per_k": 2, "unknown_per_k": 2, "seed": 1901},
    "S2": {"represented_per_k": 4, "unknown_per_k": 2, "seed": 2903},
    "S3": {"represented_per_k": 6, "unknown_per_k": 3, "seed": 3907},
}
DISCLOSURES = tuple(f"D{i}" for i in range(7))
POLICIES = ("QF", "QA_REMOVE", "QA_SPOOF")
BUDGETS = (4, 16)
CORE_STATES = ("A0", "A1", "A4")
CORE_EVIDENCE = ("E0", "E3")


def hash_unit(text):
    d = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big") / ((1 << 64) - 1)


def map_hash(text, lo, hi):
    return lo + hash_unit(text) * (hi - lo)


@dataclass(frozen=True)
class Artifact:
    scenario: str
    k: str
    ordinal: int
    index: int
    state: str
    z: tuple
    eps: float
    artifact_id: str
    truth_tag: str


def scope_id(scenario, k, ordinal):
    return f"syn-{scenario}-{k}-scope-{ordinal:02d}"


def make_artifact(scenario, k, ordinal, index, state="A0"):
    sid = scope_id(scenario, k, ordinal)
    aid = f"{sid}-artifact-{index:02d}"
    z = tuple(map_hash(f"{scenario}|{sid}|{index}|{d}", -0.20, 0.20) for d in range(5))
    eps = map_hash(f"{scenario}|{sid}|{index}|noise", -0.15, 0.15)
    return Artifact(scenario, k, ordinal, index, state, z, eps, aid, f"truth:{aid}")


def instance_count(scenario, k):
    key = "represented_per_k" if k in REPRESENTED else "unknown_per_k"
    return SCENARIOS[scenario][key]


def artifacts_for(scenario, k, indices, state):
    return [make_artifact(scenario, k, o, i, state)
            for o in range(instance_count(scenario, k)) for i in indices]


def apply_edit(z, edit):
    return tuple(a + b for a, b in zip(z, EDITS[edit]))


def hidden_score(a, z=None):
    z = a.z if z is None else z
    logit = BASE[a.k] + sum(x*y for x, y in zip(ALPHA[a.k], z)) + STATE_OFFSET[a.state] + a.eps
    return 1.0 / (1.0 + exp(-logit))


def _band(s):
    return "LOW" if s < 0.45 else "MEDIUM" if s < 0.75 else "HIGH"


def _distance_band(s):
    d = s - 0.65
    return "FAR_BELOW" if d < -0.20 else "NEAR_BELOW" if d < 0 else "NEAR_ABOVE" if d < 0.20 else "FAR_ABOVE"


def disclose(a, z, disclosure, query_index):
    if disclosure == "D0":
        return None
    s = hidden_score(a, z)
    if disclosure == "D1":
        return "DETECTED" if s >= 0.65 else "NOT_DETECTED"
    if disclosure == "D2":
        return _band(s)
    if disclosure == "D3":
        return round(s, 3)
    if disclosure == "D4":
        bins = []
        for alpha, val in zip(ALPHA[a.k], z):
            c = alpha * val
            bins.append("NEG" if c < -0.05 else "POS" if c > 0.05 else "NEUTRAL")
        return round(s, 3), tuple(bins)
    if disclosure == "D5":
        active = sum(abs(alpha*val) > 0.05 for alpha, val in zip(ALPHA[a.k], z))
        return round(s, 3), _distance_band(s), active
    if disclosure == "D6":
        if query_index > 8:
            return "RATE_LIMITED"
        n = map_hash(f"{a.scenario}|{a.artifact_id}|{query_index}|D6", -0.08, 0.08)
        return _band(min(1.0, max(0.0, s+n)))
    raise ValueError(disclosure)


def response_scalar(disclosure, response):
    if disclosure == "D1":
        return 1.0 if response == "DETECTED" else 0.0
    if disclosure in {"D2", "D6"}:
        return {"LOW": 0.0, "MEDIUM": 0.5, "HIGH": 1.0, "RATE_LIMITED": 0.5}[response]
    if disclosure in {"D3", "D4", "D5"}:
        return float(response if disclosure == "D3" else response[0])
    raise ValueError(disclosure)


def flatten_response(disclosure, response):
    if disclosure == "D0":
        return []
    if disclosure in {"D1", "D2", "D3", "D6"}:
        return [response_scalar(disclosure, response)]
    if disclosure == "D4":
        score, bins = response
        bmap = {"NEG": -1.0, "NEUTRAL": 0.0, "POS": 1.0}
        return [float(score)] + [bmap[b] for b in bins]
    if disclosure == "D5":
        score, band, active = response
        dmap = {"FAR_BELOW": -1.5, "NEAR_BELOW": -0.5, "NEAR_ABOVE": 0.5, "FAR_ABOVE": 1.5}
        return [float(score), dmap[band], float(active)/5.0]
    raise ValueError(disclosure)


def _qa_edit(policy, r):
    if r is None:
        return "P1"
    r = min(1.0, max(0.0, r))
    if policy == "QA_REMOVE":
        return "P1" if r < 0.25 else "P2" if r < 0.50 else "P4" if r < 0.75 else "P5"
    if policy == "QA_SPOOF":
        return "P5" if r < 0.25 else "P4" if r < 0.50 else "P2" if r < 0.75 else "P1"
    raise ValueError(policy)


@dataclass(frozen=True)
class PolicyRun:
    observation: tuple
    path: tuple
    responses: tuple
    final_z: tuple
    final_score: float
    utility: float
    detector_calls: int


def run_policy(a, disclosure, policy, budget):
    if budget not in (1, 4, 8, 16):
        raise ValueError("budget")
    if disclosure == "D0" and policy != "QF":
        raise ValueError("D0 only permits QF")
    z, obs, path, responses, prev, calls = a.z, [], [], [], None, 0
    for q in range(1, budget+1):
        edit = f"P{((q-1)%5)+1}" if policy == "QF" else _qa_edit(policy, prev)
        z = apply_edit(z, edit)
        path.append(edit)
        if disclosure != "D0":
            response = disclose(a, z, disclosure, q)
            calls += 1
            responses.append(response)
            obs.extend(flatten_response(disclosure, response))
            prev = response_scalar(disclosure, response)
    utility = max(0.0, BASE_UTILITY[a.state] - 0.008*budget)
    return PolicyRun(tuple(obs), tuple(path), tuple(responses), tuple(z), hidden_score(a, z), utility, calls)


def _mean_vectors(vectors):
    if not vectors:
        return ()
    n = len(vectors[0])
    if any(len(v) != n for v in vectors):
        raise ValueError("vector length mismatch")
    return tuple(sum(v[i] for v in vectors)/len(vectors) for i in range(n))


@lru_cache(maxsize=None)
def calibration_templates(scenario, disclosure, policy, budget, state):
    out = []
    for k in REPRESENTED:
        vectors = [run_policy(a, disclosure, policy, budget).observation
                   for a in artifacts_for(scenario, k, range(0, 4), state)]
        out.append((k, _mean_vectors(vectors)))
    return tuple(out)


def detector_posterior(observation, templates):
    if not observation:
        return {k: 0.25 for k in REPRESENTED}
    distances = {}
    for k, template in templates:
        if len(template) != len(observation):
            raise ValueError("template length mismatch")
        distances[k] = sum((x-y)**2 for x, y in zip(observation, template))/len(observation)
    weights = {k: exp(-d/0.05) for k, d in distances.items()}
    total = sum(weights.values())
    if total == 0:
        raise ArithmeticError("posterior underflow")
    return {k: weights[k]/total for k in REPRESENTED}


def e3_prior(a):
    logs = {}
    for c in REPRESENTED:
        perturb = map_hash(f"E3|{a.artifact_id}|{c}", -0.05, 0.05)
        logs[c] = perturb + (0.12 if a.k in REPRESENTED and c == a.k else 0.0)
    m = max(logs.values())
    weights = {k: exp(v-m) for k, v in logs.items()}
    total = sum(weights.values())
    return {k: weights[k]/total for k in REPRESENTED}


def combine_evidence(detector, a, evidence):
    if evidence == "E0":
        return dict(detector)
    if evidence != "E3":
        raise ValueError(evidence)
    prior = e3_prior(a)
    q = {k: detector[k]*prior[k] for k in REPRESENTED}
    total = sum(q.values())
    if total == 0:
        raise ArithmeticError("evidence underflow")
    return {k: q[k]/total for k in REPRESENTED}


def entropy_bits(p):
    return -sum(v*log2(v) for v in p.values() if v > 0)


def inference_metrics(a, disclosure, policy, budget, state, evidence):
    run = run_policy(a, disclosure, policy, budget)
    templates = calibration_templates(a.scenario, disclosure, policy, budget, state)
    posterior = combine_evidence(detector_posterior(run.observation, templates), a, evidence)
    ranked = sorted(posterior.items(), key=lambda kv: (-kv[1], kv[0]))
    ent = entropy_bits(posterior)
    return {
        "posterior": posterior,
        "predicted": ranked[0][0],
        "correct": a.k in REPRESENTED and ranked[0][0] == a.k,
        "entropy": ent,
        "information_gain": 2.0-ent,
        "candidate_size": sum(v >= 0.10 for v in posterior.values()) or 4,
        "utility": run.utility,
        "detector_calls": run.detector_calls,
        "final_score": run.final_score,
        "path": run.path,
        "responses": run.responses,
    }


def open_set_accept(posterior):
    ranked = sorted(posterior.items(), key=lambda kv: (-kv[1], kv[0]))
    top1, top2 = ranked[0], ranked[1]
    margin = top1[1]-top2[1]
    return top1[1] >= 0.60 and margin >= 0.15, top1[0], top1[1], margin


def condition_summary(scenario, disclosure, policy, budget, state, evidence):
    rows = [inference_metrics(a, disclosure, policy, budget, state, evidence)
            for k in REPRESENTED for a in artifacts_for(scenario, k, range(8, 12), state)]
    return {
        "scenario": scenario, "disclosure": disclosure, "policy": policy,
        "budget": budget, "state": state, "evidence": evidence, "n": len(rows),
        "accuracy": sum(bool(r["correct"]) for r in rows)/len(rows),
        "median_information_gain": median(float(r["information_gain"]) for r in rows),
        "median_candidate_size": median(int(r["candidate_size"]) for r in rows),
        "median_utility": median(float(r["utility"]) for r in rows),
        "median_final_score": median(float(r["final_score"]) for r in rows),
    }


def false_attribution_summary(scenario, disclosure, policy, budget, state, evidence):
    total = accepted = 0
    events = []
    for k in UNKNOWN:
        for a in artifacts_for(scenario, k, range(8, 12), state):
            m = inference_metrics(a, disclosure, policy, budget, state, evidence)
            ok, pred, score, margin = open_set_accept(m["posterior"])
            total += 1
            if ok:
                accepted += 1
                events.append((a.artifact_id, k, pred, score, margin))
    return {"total": total, "accepted": accepted, "rate": accepted/total if total else 0.0, "events": events}


def stability_control(a, disclosure, calls):
    if disclosure == "D0":
        return True
    responses = [disclose(a, a.z, disclosure, i) for i in range(1, calls+1)]
    if disclosure in {"D1", "D2", "D3", "D4", "D5"}:
        return all(r == responses[0] for r in responses)
    return all(r == "RATE_LIMITED" for r in responses[8:]) and all(r != "RATE_LIMITED" for r in responses[:8])


def controls():
    a = make_artifact("S1", "K2", 0, 4, "A0")
    b = replace(a, truth_tag="changed-hidden-custody-label")
    c1 = hidden_score(a) == hidden_score(b) and all(disclose(a, a.z, d, 1) == disclose(b, b.z, d, 1) for d in ("D1", "D2", "D3", "D4", "D5"))
    c2 = all("syn-" not in json.dumps(disclose(a, a.z, d, 1)) for d in ("D1", "D2", "D3", "D4", "D5", "D6"))
    s = hidden_score(a)
    c3 = disclose(a, a.z, "D1", 1) == ("DETECTED" if s >= 0.65 else "NOT_DETECTED") and disclose(a, a.z, "D3", 1) == round(s, 3)
    c4 = all(run_policy(a, d, p, budget).detector_calls == budget for d in DISCLOSURES[1:] for p in POLICIES for budget in BUDGETS)
    c5 = run_policy(a, "D3", "QF", 16).path == tuple(f"P{((q-1)%5)+1}" for q in range(1, 17))
    k0 = [make_artifact("S1", "K0", o, i, "A0") for o in range(2) for i in range(8, 12)]
    c6 = all(hidden_score(x) < 0.65 for x in k0)
    c7 = run_policy(a, "D3", "QF", 16).path == run_policy(a, "D1", "QF", 16).path
    c8 = run_policy(a, "D4", "QA_REMOVE", 16) == run_policy(a, "D4", "QA_REMOVE", 16)
    c9 = set(range(0, 4)).isdisjoint(range(8, 12))
    a4 = replace(a, state="A4")
    c10 = a4.k == a.k and a4.z == a.z and a4.eps == a.eps
    c11 = all(stability_control(a, d, 16) for d in DISCLOSURES[1:])
    c12 = all(run_policy(a, "D3", p, budget).utility >= 0.80 for p in POLICIES for budget in BUDGETS)
    out = {f"C{i}": v for i, v in enumerate((c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12), 1)}
    out["all_pass"] = all(out.values())
    return out


def classify_summary(control_pass, material, binary, adaptive, mitigation, false_attr):
    if not control_pass:
        return "CONTROL_FAILED"
    if material or binary or adaptive or mitigation:
        return "DETECTOR_MEDIATED_INFERENCE_OBSERVED"
    if false_attr:
        return "FALSE_ATTRIBUTION_ONLY_OBSERVED"
    return "NO_PREDECLARED_EFFECT_ESTABLISHED"


def stable_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=list)
    return hashlib.sha256(raw.encode()).hexdigest()


def family_labels(selected, unknown):
    idx = {(r["scenario"], r["disclosure"], r["policy"], r["budget"], r["state"], r["evidence"]): r for r in selected}
    uidx = {(r["scenario"], r["d"], r["p"], r["budget"], r["state"], r["e"]): r for r in unknown}
    material_groups, binary_groups, adaptive_groups, mitigation_groups = {}, {}, {}, {}

    for r in selected:
        scenario, d, p = str(r["scenario"]), str(r["disclosure"]), str(r["policy"])
        budget, state, evidence = int(r["budget"]), str(r["state"]), str(r["evidence"])
        if d != "D0":
            base = idx[(scenario, "D0", "QF", budget, state, evidence)]
            info_delta = float(r["median_information_gain"])-float(base["median_information_gain"])
            acc_delta = float(r["accuracy"])-float(base["accuracy"])
            if float(r["median_utility"]) >= 0.80 and (info_delta >= 0.20 or acc_delta >= 0.10):
                material_groups.setdefault((d, p, budget, state, evidence), set()).add(scenario)
            if d == "D1" and p == "QF" and budget == 16 and float(r["median_utility"]) >= 0.80 and (info_delta >= 0.20 or acc_delta >= 0.10):
                binary_groups.setdefault((state, evidence), set()).add(scenario)

        if p in {"QA_REMOVE", "QA_SPOOF"}:
            qf = idx[(scenario, d, "QF", budget, state, evidence)]
            if float(r["median_utility"]) >= 0.80 and ((float(r["median_information_gain"])-float(qf["median_information_gain"])) >= 0.10 or (float(r["accuracy"])-float(qf["accuracy"])) >= 0.10):
                adaptive_groups.setdefault((d, p, budget, state, evidence), set()).add(scenario)

        if d == "D6" and p == "QF" and state in {"A0", "A4"}:
            d3 = idx[(scenario, "D3", "QF", budget, state, evidence)]
            d4 = idx[(scenario, "D4", "QF", budget, state, evidence)]
            richer = max(float(d3["median_information_gain"]), float(d4["median_information_gain"]))
            u6 = uidx[(scenario, "D6", "QF", budget, state, evidence)]
            u3 = uidx[(scenario, "D3", "QF", budget, state, evidence)]
            u4 = uidx[(scenario, "D4", "QF", budget, state, evidence)]
            richer_ufir = min(float(u3["rate"]), float(u4["rate"]))
            fa_ok = float(u6["rate"]) <= richer_ufir + 0.05
            if richer > 0 and (richer-float(r["median_information_gain"]))/richer >= 0.25 and float(r["median_utility"]) >= 0.80 and fa_ok:
                mitigation_groups.setdefault((budget, state, evidence), set()).add(scenario)

    material_pass = [k for k, v in material_groups.items() if len(v) >= 2]
    binary_pass = [k for k, v in binary_groups.items() if len(v) >= 2]
    adaptive_pass = [k for k, v in adaptive_groups.items() if len(v) >= 2]
    mitigation_pass = [k for k, v in mitigation_groups.items() if len(v) >= 2]
    false_attr = any(int(u["accepted"]) > 0 for u in unknown)
    return {
        "material": bool(material_pass), "binary": bool(binary_pass),
        "adaptive": bool(adaptive_pass), "mitigation": bool(mitigation_pass),
        "false_attr": false_attr, "material_families": material_pass,
        "binary_families": binary_pass, "adaptive_families": adaptive_pass,
        "mitigation_families": mitigation_pass,
    }


def candidate_reference():
    ctl, selected, unknown = controls(), [], []
    for scenario in SCENARIOS:
        for state in CORE_STATES:
            for evidence in CORE_EVIDENCE:
                for budget in BUDGETS:
                    selected.append(condition_summary(scenario, "D0", "QF", budget, state, evidence))
                    for d in DISCLOSURES[1:]:
                        for p in POLICIES:
                            selected.append(condition_summary(scenario, d, p, budget, state, evidence))
    for scenario in SCENARIOS:
        for state in ("A0", "A4"):
            for evidence in CORE_EVIDENCE:
                for budget in BUDGETS:
                    unknown.append({**{"scenario": scenario, "d": "D0", "p": "QF", "budget": budget, "state": state, "e": evidence}, **false_attribution_summary(scenario, "D0", "QF", budget, state, evidence)})
                    for d in DISCLOSURES[1:]:
                        for p in POLICIES:
                            unknown.append({**{"scenario": scenario, "d": d, "p": p, "budget": budget, "state": state, "e": evidence}, **false_attribution_summary(scenario, d, p, budget, state, evidence)})
    details = family_labels(selected, unknown)
    flags = {k: bool(details[k]) for k in ("material", "binary", "adaptive", "mitigation", "false_attr")}
    classification = classify_summary(ctl["all_pass"], **flags)
    report = {
        "controls": ctl, "condition_count": len(selected),
        "unknown_condition_count": len(unknown), "flags": flags,
        "family_details": details, "classification": classification,
        "conditions": selected, "unknown": unknown,
    }
    report["sha256"] = stable_hash(report)
    return report
