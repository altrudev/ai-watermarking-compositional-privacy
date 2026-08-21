from __future__ import annotations

from dataclasses import asdict, replace
from itertools import combinations, permutations
from statistics import median
from typing import Callable, Sequence
import hashlib
import json
import re

from lab.noncommutativity_lab import CachedEvaluator
from lab.transformation_chain_lab import (
    Artifact,
    HEDGES,
    SENTENCE_RE,
    SIGNATURES,
    TOPICS,
    TRANSITIONS,
    evaluate,
    generate_population,
    make_artifacts,
)


POLICIES = {
    "canonical_combined": (0.30, 0.20, 0.10, 0.10, 0.05, 0.25),
    "text_only": (0.45, 0.30, 0.25, 0.00, 0.00, 0.00),
    "lexical_heavy": (0.55, 0.15, 0.10, 0.05, 0.05, 0.10),
    "timing_heavy": (0.20, 0.15, 0.10, 0.10, 0.05, 0.40),
    "metadata_light": (0.35, 0.20, 0.15, 0.10, 0.05, 0.15),
}

SCENARIOS = {
    "S1": {"persons": 8, "seed": 41, "artifact_seed": 7000},
    "S2": {"persons": 8, "seed": 73, "artifact_seed": 9001},
    "S3": {"persons": 12, "seed": 41, "artifact_seed": 9001},
    "S4": {"persons": 12, "seed": 101, "artifact_seed": 7000},
    "S5": {"persons": 16, "seed": 73, "artifact_seed": 7000},
    "S6": {"persons": 16, "seed": 101, "artifact_seed": 9001},
}

SCENARIO_TRANSFERS = (("S1", "S2"), ("S3", "S4"), ("S5", "S6"))

LEXICAL_GENERALIZE = {
    "depends": "relates",
    "change": "affect",
    "isolated": "separate",
    "combine": "join",
    "survives": "remains",
    "removed": "omitted",
    "expose": "reveal",
    "tested": "checked",
    "interchangeable": "equivalent",
    "important": "relevant",
}

LEXICAL_SUBSTITUTE = {
    "signal": "indicator",
    "turn": "convert",
    "through": "via",
    "requires": "needs",
    "separate": "distinct",
    "looks": "appears",
    "yet": "though",
    "still": "continues",
    "must": "should",
    "why": "reason",
}


def _replace_words(text: str, mapping: dict[str, str]) -> str:
    result = text
    for source, target in sorted(mapping.items(), key=lambda item: -len(item[0])):
        result = re.sub(rf"\b{re.escape(source)}\b", target, result, flags=re.I)
    return result


def _sentences(text: str) -> list[str]:
    return [row.strip() for row in SENTENCE_RE.split(text.strip()) if row.strip()]


def lexical_generalize(artifact: Artifact) -> Artifact:
    return replace(artifact, text=_replace_words(artifact.text, LEXICAL_GENERALIZE))


def style_flatten(artifact: Artifact) -> Artifact:
    text = artifact.text
    phrases = sorted((*TRANSITIONS, *HEDGES, *SIGNATURES), key=len, reverse=True)
    for phrase in phrases:
        text = re.sub(rf"\b{re.escape(phrase)}\b,?\s*", "", text, flags=re.I)
    text = text.replace(";", ",").replace("\n\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return replace(artifact, text=text)


def sentence_rotate(artifact: Artifact) -> Artifact:
    rows = _sentences(artifact.text)
    if len(rows) > 1:
        rows = rows[1:] + rows[:1]
    return replace(artifact, text=" ".join(rows))


def bounded_compress(artifact: Artifact) -> Artifact:
    rows = _sentences(artifact.text)
    if len(rows) <= 2:
        keep = rows
    else:
        keep = [row for index, row in enumerate(rows) if index % 3 != 1]
    if not keep and rows:
        keep = [rows[0]]
    return replace(artifact, text=" ".join(keep))


def topic_abstraction(artifact: Artifact) -> Artifact:
    mapping = {}
    for _topic, terms in TOPICS.items():
        representative = terms[0]
        for term in terms:
            mapping[term] = representative
    return replace(artifact, text=_replace_words(artifact.text, mapping))


def clause_reorder(artifact: Artifact) -> Artifact:
    output = []
    for sentence in _sentences(artifact.text):
        punctuation = ";" if ";" in sentence else "," if "," in sentence else None
        if punctuation:
            left, right = sentence.split(punctuation, 1)
            terminal = "." if sentence.endswith(".") else "?" if sentence.endswith("?") else ""
            right = right.rstrip(".?").strip()
            output.append(f"{right}{punctuation} {left.strip()}{terminal}".strip())
        else:
            output.append(sentence)
    return replace(artifact, text=" ".join(output))


def segment_rechunk(artifact: Artifact) -> Artifact:
    rows = _sentences(artifact.text)
    if len(rows) < 2:
        return artifact
    rebuilt = []
    index = 0
    while index < len(rows):
        if index + 1 < len(rows):
            left = rows[index].rstrip(".?!")
            right = rows[index + 1].rstrip(".?!")
            rebuilt.append(f"{left}; {right}.")
            index += 2
        else:
            rebuilt.append(rows[index])
            index += 1
    return replace(artifact, text=" ".join(rebuilt))


def lexical_substitute(artifact: Artifact) -> Artifact:
    return replace(artifact, text=_replace_words(artifact.text, LEXICAL_SUBSTITUTE))


FAMILIES: dict[str, dict[str, Callable[[Artifact], Artifact]]] = {
    "structural_normalization": {
        "lexical_generalize": lexical_generalize,
        "style_flatten": style_flatten,
        "sentence_rotate": sentence_rotate,
        "bounded_compress": bounded_compress,
    },
    "representation_segmentation": {
        "topic_abstraction": topic_abstraction,
        "clause_reorder": clause_reorder,
        "segment_rechunk": segment_rechunk,
        "lexical_substitute": lexical_substitute,
    },
}


def _apply(artifacts: Sequence[Artifact], transforms: dict[str, Callable[[Artifact], Artifact]], path: Sequence[str]) -> list[Artifact]:
    current = list(artifacts)
    for name in path:
        current = [transforms[name](artifact) for artifact in current]
    return current


def partition_artifacts(artifacts: Sequence[Artifact]) -> tuple[list[Artifact], list[Artifact]]:
    calibration, holdout = [], []
    for artifact in artifacts:
        low_bit = hashlib.sha256(artifact.target_generation_id.encode("utf-8")).digest()[-1] & 1
        (calibration if low_bit == 0 else holdout).append(artifact)
    if not calibration or not holdout:
        raise ValueError("Deterministic partition produced an empty calibration or holdout set")
    return calibration, holdout


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or not xs:
        raise ValueError("Pearson inputs must be non-empty and equal length")
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [value - mx for value in xs]
    dy = [value - my for value in ys]
    denominator = (sum(value * value for value in dx) * sum(value * value for value in dy)) ** 0.5
    if denominator == 0:
        return 0.0
    return sum(left * right for left, right in zip(dx, dy)) / denominator


def _pair_key(left: str, right: str) -> str:
    return f"{left}|{right}"


def pairwise_effects(evaluator: CachedEvaluator, calibration: Sequence[Artifact], transforms: dict[str, Callable[[Artifact], Artifact]], weights) -> dict:
    names = tuple(transforms)
    effects = {}
    rows = {}
    for left, right in combinations(names, 2):
        left_right = _apply(calibration, transforms, (left, right))
        right_left = _apply(calibration, transforms, (right, left))
        lr = evaluator.evaluate(left_right, weights)
        rl = evaluator.evaluate(right_left, weights)
        effect = lr.person_top1 - rl.person_top1
        key = _pair_key(left, right)
        effects[key] = effect
        rows[key] = {
            "left_before_right": [left, right],
            "right_before_left": [right, left],
            "person_top1_difference": effect,
            "generation_top1_difference": lr.generation_top1 - rl.generation_top1,
            "final_text_difference_fraction": sum(a.text != b.text for a, b in zip(left_right, right_left)) / len(left_right),
            "final_metadata_identical": all(
                (a.target_generation_id, a.published_minute, a.provider_hint, a.watermark_family)
                == (b.target_generation_id, b.published_minute, b.provider_hint, b.watermark_family)
                for a, b in zip(left_right, right_left)
            ),
        }
    return {"effects": effects, "pairs": rows}


def predict_paths(evaluator: CachedEvaluator, holdout: Sequence[Artifact], transforms: dict[str, Callable[[Artifact], Artifact]], weights, effects: dict[str, float]) -> dict:
    names = tuple(transforms)
    ordered_pairs = list(combinations(names, 2))
    rows = []
    for path in permutations(names):
        final = _apply(holdout, transforms, path)
        observed = evaluator.evaluate(final, weights).person_top1
        positions = {name: index for index, name in enumerate(path)}
        score = 0.0
        for left, right in ordered_pairs:
            effect = effects[_pair_key(left, right)]
            score += effect if positions[left] < positions[right] else -effect
        rows.append({"path": list(path), "pairwise_score": score, "observed_person_top1": observed})
    r = _pearson([row["pairwise_score"] for row in rows], [row["observed_person_top1"] for row in rows])
    return {"path_count": len(rows), "pearson_r": r, "paths": rows}


def _holdout_class(r: float) -> str:
    if r >= 0.70:
        return "predictive"
    if r >= 0.30:
        return "partial"
    return "not_predictive"


def _transfer_class(r: float) -> str:
    if r >= 0.50:
        return "transfer_supported"
    if r >= 0.20:
        return "weak_context_dependent_transfer"
    return "transfer_not_supported"


def commuting_control(evaluator: CachedEvaluator, holdout: Sequence[Artifact], weights) -> dict:
    left = [replace(row, text=" ".join(row.text.lower().split())) for row in holdout]
    right = [replace(row, text=" ".join(row.text.split()).lower()) for row in holdout]
    lm = evaluator.evaluate(left, weights)
    rm = evaluator.evaluate(right, weights)
    return {
        "final_text_identical": all(a.text == b.text for a, b in zip(left, right)),
        "final_metadata_identical": all(
            (a.target_generation_id, a.published_minute, a.provider_hint, a.watermark_family)
            == (b.target_generation_id, b.published_minute, b.provider_hint, b.watermark_family)
            for a, b in zip(left, right)
        ),
        "person_top1_difference": lm.person_top1 - rm.person_top1,
        "generation_top1_difference": lm.generation_top1 - rm.generation_top1,
        "control_pass": (
            all(a.text == b.text for a, b in zip(left, right))
            and lm.person_top1 == rm.person_top1
            and lm.generation_top1 == rm.generation_top1
        ),
    }


def prepare_scenario(name: str):
    params = SCENARIOS[name]
    population = generate_population(params["persons"], params["seed"])
    artifacts = make_artifacts(population, seed=params["artifact_seed"])
    calibration, holdout = partition_artifacts(artifacts)
    evaluator = CachedEvaluator(population)
    return population, calibration, holdout, evaluator


def scorer_parity(population, holdout: Sequence[Artifact], evaluator: CachedEvaluator) -> bool:
    transforms = FAMILIES["structural_normalization"]
    path = tuple(transforms)
    sample = _apply(holdout, transforms, path)
    cached = asdict(evaluator.evaluate(sample, POLICIES["canonical_combined"]))
    canonical = asdict(evaluate(population, sample, POLICIES["canonical_combined"]))
    return cached == canonical


def run_reference_matrix() -> dict:
    prepared = {name: prepare_scenario(name) for name in SCENARIOS}
    parity = {}
    controls = {}
    holdout_cells = []
    pair_cache: dict[tuple[str, str, str], dict] = {}

    for scenario_name, (population, calibration, holdout, evaluator) in prepared.items():
        parity[scenario_name] = scorer_parity(population, holdout, evaluator)
        controls[scenario_name] = {}
        for policy_name, weights in POLICIES.items():
            controls[scenario_name][policy_name] = commuting_control(evaluator, holdout, weights)
            for family_name, transforms in FAMILIES.items():
                pair = pairwise_effects(evaluator, calibration, transforms, weights)
                pair_cache[(scenario_name, family_name, policy_name)] = pair
                prediction = predict_paths(evaluator, holdout, transforms, weights, pair["effects"])
                r = prediction["pearson_r"]
                holdout_cells.append({
                    "scenario": scenario_name,
                    "family": family_name,
                    "policy": policy_name,
                    "calibration_samples": len(calibration),
                    "holdout_samples": len(holdout),
                    "pearson_r": r,
                    "classification": _holdout_class(r),
                    "pairwise": pair["pairs"],
                    "paths": prediction["paths"],
                })

    transfer_cells = []
    for source_name, destination_name in SCENARIO_TRANSFERS:
        _source_population, _source_calibration, _source_holdout, _source_evaluator = prepared[source_name]
        _dest_population, _dest_calibration, dest_holdout, dest_evaluator = prepared[destination_name]
        for family_name, transforms in FAMILIES.items():
            for policy_name, weights in POLICIES.items():
                source_pair = pair_cache[(source_name, family_name, policy_name)]
                prediction = predict_paths(dest_evaluator, dest_holdout, transforms, weights, source_pair["effects"])
                r = prediction["pearson_r"]
                transfer_cells.append({
                    "source_scenario": source_name,
                    "destination_scenario": destination_name,
                    "family": family_name,
                    "policy": policy_name,
                    "destination_holdout_samples": len(dest_holdout),
                    "pearson_r": r,
                    "classification": _transfer_class(r),
                    "paths": prediction["paths"],
                })

    all_controls_pass = all(
        row["control_pass"]
        for scenario in controls.values()
        for row in scenario.values()
    )
    all_parity_pass = all(parity.values())
    predictive_count = sum(row["pearson_r"] >= 0.70 for row in holdout_cells)
    transfer_supported_count = sum(row["pearson_r"] >= 0.50 for row in transfer_cells)
    holdout_median = median(row["pearson_r"] for row in holdout_cells)
    transfer_median = median(row["pearson_r"] for row in transfer_cells)

    family_scenario_coverage = all(
        any(
            row["family"] == family
            and row["scenario"] == scenario
            and row["pearson_r"] >= 0.70
            for row in holdout_cells
        )
        for family in FAMILIES
        for scenario in SCENARIOS
    )
    policy_transfer_coverage = all(
        any(row["policy"] == policy and row["pearson_r"] >= 0.50 for row in transfer_cells)
        for policy in POLICIES
    )

    if not all_controls_pass or not all_parity_pass:
        status = "CONTROL_FAILED"
    elif (
        predictive_count >= 42
        and transfer_supported_count >= 15
        and holdout_median >= 0.70
        and transfer_median >= 0.50
        and family_scenario_coverage
        and policy_transfer_coverage
    ):
        status = "MECHANISM_REPLICATED_WITH_TRANSFER_FOR_DECLARED_MATRIX"
    elif predictive_count < 30 or transfer_supported_count < 9:
        status = "MECHANISM_NOT_REPLICATED"
    else:
        status = "CONTEXT_DEPENDENT_REPLICATION"

    return {
        "schema": "altru.dev/cross-family-replication/0.7",
        "research_scope": "synthetic-only",
        "predecessor_commit": "c29b40db9000d3e0a49c2c25fadab215d3084480",
        "protocol_commit": "786ebb3d097d999e15f72cbfce536e59566206a1",
        "families": {name: list(transforms) for name, transforms in FAMILIES.items()},
        "policies": {name: list(weights) for name, weights in POLICIES.items()},
        "scenarios": SCENARIOS,
        "scenario_transfers": [list(pair) for pair in SCENARIO_TRANSFERS],
        "scorer_parity": parity,
        "commuting_controls": controls,
        "holdout_cells": holdout_cells,
        "transfer_cells": transfer_cells,
        "aggregate": {
            "holdout_predictive_count": predictive_count,
            "holdout_cell_count": len(holdout_cells),
            "transfer_supported_count": transfer_supported_count,
            "transfer_cell_count": len(transfer_cells),
            "median_holdout_r": holdout_median,
            "median_transfer_r": transfer_median,
            "family_scenario_coverage": family_scenario_coverage,
            "policy_transfer_coverage": policy_transfer_coverage,
            "all_controls_pass": all_controls_pass,
            "all_scorer_parity_pass": all_parity_pass,
        },
        "claim": {
            "status": status,
            "boundary": "Declared synthetic transform families, adversary policies, scenarios, and scoring model only; not proof of anonymity, real-person attribution, or deployed-provider behavior.",
        },
        "standing_rules": [
            "Privacy transformation != privacy evidence",
            "Failed re-identification != proven anonymity",
            "Synthetic benchmark mechanism != deployed-provider mechanism",
            "Negative and context-dependent replication evidence must be preserved",
        ],
    }


def main() -> None:
    print(json.dumps(run_reference_matrix(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
