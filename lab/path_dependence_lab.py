from __future__ import annotations

from dataclasses import asdict
from itertools import permutations
from statistics import mean
from typing import Iterable, Sequence
import json

from .transformation_chain_lab import (
    Artifact,
    SINGLE_SIGNALS,
    evaluate,
    generate_population,
    make_artifacts,
    model_edit_stage,
    multi_model_edit_stage,
    paraphrase_stage,
    summarize_stage,
    translate_stage,
    utility,
)


# v0.3's neutral edit stage is intentionally excluded: its reference result did
# not change attribution. v0.4 permutes the five privacy-relevant transforms.
PATH_TRANSFORMS = {
    "paraphrase": paraphrase_stage,
    "summarize": summarize_stage,
    "translate": translate_stage,
    "model_edit": model_edit_stage,
    "multi_model_edit": multi_model_edit_stage,
}
TRANSFORM_NAMES = tuple(PATH_TRANSFORMS)
ORDER_SENSITIVITY_THRESHOLD = 0.10
UTILITY_MATCH_TOLERANCE = {
    "semantic_retention": 0.015,
    "content_word_retention": 0.035,
    "length_ratio": 0.035,
}


def all_orders() -> tuple[tuple[str, ...], ...]:
    return tuple(permutations(TRANSFORM_NAMES))


def validate_order(order: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(order)
    if len(normalized) != len(TRANSFORM_NAMES):
        raise ValueError("Path must contain each declared transform exactly once")
    if set(normalized) != set(TRANSFORM_NAMES) or len(set(normalized)) != len(normalized):
        raise ValueError("Path must contain each declared transform exactly once")
    return normalized


def apply_order(artifacts: Sequence[Artifact], order: Sequence[str]) -> list[Artifact]:
    normalized = validate_order(order)
    current = list(artifacts)
    for name in normalized:
        current = [PATH_TRANSFORMS[name](artifact) for artifact in current]
    return current


def mean_utility(original: Sequence[Artifact], current: Sequence[Artifact]) -> dict[str, float]:
    rows = [utility(before, after) for before, after in zip(original, current)]
    return {key: mean(row[key] for row in rows) for key in rows[0]}


def _order_id(order: Sequence[str]) -> str:
    return "→".join(order)


def evaluate_order(population, original: Sequence[Artifact], order: Sequence[str]) -> dict:
    normalized = validate_order(order)
    final_artifacts = apply_order(original, normalized)
    return {
        "order": list(normalized),
        "order_id": _order_id(normalized),
        "metrics": asdict(evaluate(population, final_artifacts)),
        "utility": mean_utility(original, final_artifacts),
    }


def utility_matched(left: dict, right: dict) -> bool:
    return all(
        abs(left["utility"][key] - right["utility"][key]) <= tolerance
        for key, tolerance in UTILITY_MATCH_TOLERANCE.items()
    )


def strongest_matched_utility_contrast(results: Sequence[dict]) -> dict | None:
    best = None
    for i, left in enumerate(results):
        for right in results[i + 1 :]:
            if not utility_matched(left, right):
                continue
            delta = abs(left["metrics"]["person_top1"] - right["metrics"]["person_top1"])
            if best is None or delta > best["person_top1_delta"]:
                low, high = sorted((left, right), key=lambda row: row["metrics"]["person_top1"])
                best = {
                    "person_top1_delta": delta,
                    "lower_attribution_order": low,
                    "higher_attribution_order": high,
                }
    return best


def trace_order(population, original: Sequence[Artifact], order: Sequence[str]) -> dict:
    normalized = validate_order(order)
    current = list(original)
    stages = []
    for name in normalized:
        current = [PATH_TRANSFORMS[name](artifact) for artifact in current]
        metrics = asdict(evaluate(population, current))
        single_channels = {
            signal: asdict(evaluate(population, current, weights))
            for signal, weights in SINGLE_SIGNALS.items()
        }
        strongest = max(single_channels.items(), key=lambda item: item[1]["person_top1"])[0]
        stages.append({
            "after": name,
            "metrics": metrics,
            "strongest_channel": strongest,
            "utility": mean_utility(original, current),
        })
    return {"order": list(normalized), "stages": stages}


def run_experiment(persons: int = 12, seed: int = 41, orders: Iterable[Sequence[str]] | None = None) -> dict:
    population = generate_population(persons=persons, seed=seed)
    original = make_artifacts(population)
    declared_orders = tuple(tuple(order) for order in (orders if orders is not None else all_orders()))
    if not declared_orders:
        raise ValueError("At least one transform order is required")
    results = [evaluate_order(population, original, order) for order in declared_orders]
    ranked = sorted(results, key=lambda row: (row["metrics"]["person_top1"], row["metrics"]["generation_top1"], row["order_id"]))
    minimum, maximum = ranked[0], ranked[-1]
    sensitivity = maximum["metrics"]["person_top1"] - minimum["metrics"]["person_top1"]
    matched = strongest_matched_utility_contrast(results)
    random_baseline = 1.0 / persons
    supported = sensitivity >= ORDER_SENSITIVITY_THRESHOLD

    return {
        "schema": "altru.dev/path-dependent-compositional-privacy/0.4",
        "research_scope": "synthetic-only",
        "source_experiment": "transformation-chain-attribution-persistence-v0.3",
        "population": {"persons": persons, "generations": len(population)},
        "transform_set": list(TRANSFORM_NAMES),
        "orders_evaluated": len(results),
        "random_person_baseline": random_baseline,
        "order_sensitivity_threshold": ORDER_SENSITIVITY_THRESHOLD,
        "order_sensitivity": sensitivity,
        "order_sensitivity_pp": sensitivity * 100.0,
        "minimum_final_attribution": minimum,
        "maximum_final_attribution": maximum,
        "matched_utility_contrast": matched,
        "minimum_path_trace": trace_order(population, original, minimum["order"]),
        "maximum_path_trace": trace_order(population, original, maximum["order"]),
        "final_claim": {
            "status": "supported_for_declared_test" if supported else "not_supported",
            "proposition": "The same declared transformation set can produce materially different attribution outcomes when transformation order changes.",
            "boundary": "Declared synthetic population, transparent proxy transformations, scoring model, and threshold only; not proof of real-world anonymity or path dependence.",
        },
        "all_final_results": results,
        "limitations": [
            "Synthetic identities and generated synthetic text only.",
            "Transformations are transparent deterministic proxies, not proprietary production models.",
            "The neutral v0.3 edit stage is excluded because it did not alter the v0.3 reference attribution result.",
            "Final-artifact privacy is evaluated under the declared attribution model only.",
            "A low-attribution intermediate or final state is not proof of anonymity.",
            "A supported path-dependence result is an experimental property of this declared benchmark, not a universal privacy law.",
        ],
    }


def main() -> None:
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
