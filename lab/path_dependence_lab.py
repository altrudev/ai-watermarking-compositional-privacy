from __future__ import annotations

from itertools import permutations
from statistics import mean
from typing import Iterable, Sequence
from math import exp
import json

from .transformation_chain_lab import (
    Artifact,
    WEIGHTS,
    cosine,
    lexical_vector,
    semantic_vector,
    style_vector,
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


class CachedEvaluator:
    """Exact v0.3 scoring semantics with reusable candidate/text features."""

    def __init__(self, population):
        self.population = list(population)
        self.by_generation = {row.generation_id: row for row in self.population}
        self.feature_cache = {}
        self.candidate_features = {row.generation_id: self._features(row.text) for row in self.population}

    def _features(self, text):
        cached = self.feature_cache.get(text)
        if cached is None:
            cached = (lexical_vector(text), semantic_vector(text), style_vector(text))
            self.feature_cache[text] = cached
        return cached

    def evaluate(self, artifacts, weights=WEIGHTS):
        total = sum(weights)
        if total <= 0:
            raise ValueError("At least one attribution signal must be enabled")
        w = [value / total for value in weights]
        p1 = g1 = g5 = 0
        ranks = []
        anonymity = []
        for artifact in artifacts:
            target = self.by_generation[artifact.target_generation_id]
            af = self._features(artifact.text)
            ranked = []
            for candidate in self.population:
                cf = self.candidate_features[candidate.generation_id]
                lx = (cosine(af[0], cf[0]) + 1) / 2
                sm = (cosine(af[1], cf[1]) + 1) / 2
                st = (cosine(af[2], cf[2]) + 1) / 2
                wm = float(artifact.watermark_family is not None and artifact.watermark_family == candidate.watermark_family)
                provider = float(artifact.provider_hint is not None and artifact.provider_hint == candidate.provider)
                delta = artifact.published_minute - candidate.created_minute
                timing = exp(-delta / 50) if delta >= 0 else 0.0
                score = sum(x * y for x, y in zip((lx, sm, st, wm, provider, timing), w))
                ranked.append((candidate, score))
            ranked.sort(key=lambda item: (-item[1], item[0].generation_id))
            pos = next(i for i, (candidate, _) in enumerate(ranked) if candidate.generation_id == target.generation_id)
            prediction = ranked[0][0]
            p1 += prediction.person_id == target.person_id
            g1 += pos == 0
            g5 += pos < 5
            ranks.append(pos + 1)
            best = ranked[0][1]
            anonymity.append(sum(score >= best - 0.02 for _, score in ranked))
        n = len(artifacts)
        return {
            "samples": n,
            "person_top1": p1 / n,
            "generation_top1": g1 / n,
            "generation_top5": g5 / n,
            "mean_generation_rank": mean(ranks),
            "mean_anonymity_set": mean(anonymity),
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


def evaluate_order(evaluator: CachedEvaluator, original: Sequence[Artifact], order: Sequence[str]) -> dict:
    normalized = validate_order(order)
    final_artifacts = apply_order(original, normalized)
    return {
        "order": list(normalized),
        "order_id": _order_id(normalized),
        "metrics": evaluator.evaluate(final_artifacts),
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


def trace_order(evaluator: CachedEvaluator, original: Sequence[Artifact], order: Sequence[str]) -> dict:
    normalized = validate_order(order)
    current = list(original)
    stages = []
    for name in normalized:
        current = [PATH_TRANSFORMS[name](artifact) for artifact in current]
        stages.append({
            "after": name,
            "metrics": evaluator.evaluate(current),
            "utility": mean_utility(original, current),
        })
    return {"order": list(normalized), "stages": stages}


def run_experiment(persons: int = 8, seed: int = 41, orders: Iterable[Sequence[str]] | None = None) -> dict:
    population = generate_population(persons=persons, seed=seed)
    original = make_artifacts(population)
    declared_orders = tuple(tuple(order) for order in (orders if orders is not None else all_orders()))
    if not declared_orders:
        raise ValueError("At least one transform order is required")
    evaluator = CachedEvaluator(population)
    results = [evaluate_order(evaluator, original, order) for order in declared_orders]
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
        "minimum_path_trace": trace_order(evaluator, original, minimum["order"]),
        "maximum_path_trace": trace_order(evaluator, original, maximum["order"]),
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
