from __future__ import annotations

from dataclasses import asdict, replace
from itertools import combinations, permutations
from math import sqrt
from statistics import mean
from typing import Sequence
import json

from lab.transformation_chain_lab import (
    Artifact,
    SINGLE_SIGNALS,
    WEIGHTS,
    cosine,
    evaluate,
    generate_population,
    lexical_vector,
    make_artifacts,
    model_edit_stage,
    paraphrase_stage,
    semantic_vector,
    style_vector,
    summarize_stage,
    translate_stage,
)

TRANSFORMS = {
    "paraphrase": paraphrase_stage,
    "summarize": summarize_stage,
    "translate": translate_stage,
    "model_edit": model_edit_stage,
}
TRANSFORM_NAMES = tuple(TRANSFORMS)


def _apply(artifacts: Sequence[Artifact], path: Sequence[str]) -> list[Artifact]:
    current = list(artifacts)
    for name in path:
        current = [TRANSFORMS[name](artifact) for artifact in current]
    return current


def _metadata_signature(artifacts: Sequence[Artifact]):
    return tuple(
        sorted(
            (
                artifact.target_generation_id,
                artifact.published_minute,
                artifact.provider_hint,
                artifact.watermark_family,
            )
            for artifact in artifacts
        )
    )


def _mean_feature_divergence(left: Sequence[Artifact], right: Sequence[Artifact], vectorizer) -> float:
    rows = []
    for a, b in zip(left, right):
        rows.append(1.0 - max(-1.0, min(1.0, cosine(vectorizer(a.text), vectorizer(b.text)))))
    return mean(rows)


def _text_difference_fraction(left: Sequence[Artifact], right: Sequence[Artifact]) -> float:
    return mean(float(a.text != b.text) for a, b in zip(left, right))


def _channel_metrics(population, artifacts):
    return {
        name: asdict(evaluate(population, artifacts, weights))
        for name, weights in SINGLE_SIGNALS.items()
    }


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys) or not xs:
        raise ValueError("Pearson inputs must be non-empty and equal length")
    mx, my = mean(xs), mean(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    denominator = sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    if denominator == 0:
        return 0.0
    return sum(x * y for x, y in zip(dx, dy)) / denominator


def _pair_key(left: str, right: str) -> str:
    return f"{left}|{right}"


def pairwise_mechanisms(population, original: Sequence[Artifact]) -> dict:
    rows = {}
    directional_effects = {}
    for left, right in combinations(TRANSFORM_NAMES, 2):
        left_right = _apply(original, (left, right))
        right_left = _apply(original, (right, left))
        lr_metrics = asdict(evaluate(population, left_right, WEIGHTS))
        rl_metrics = asdict(evaluate(population, right_left, WEIGHTS))
        lr_channels = _channel_metrics(population, left_right)
        rl_channels = _channel_metrics(population, right_left)
        channel_deltas = {
            name: lr_channels[name]["person_top1"] - rl_channels[name]["person_top1"]
            for name in SINGLE_SIGNALS
        }
        strongest_channel = max(channel_deltas, key=lambda name: abs(channel_deltas[name]))
        effect = lr_metrics["person_top1"] - rl_metrics["person_top1"]
        directional_effects[_pair_key(left, right)] = effect
        rows[_pair_key(left, right)] = {
            "left_before_right": [left, right],
            "right_before_left": [right, left],
            "text_difference_fraction": _text_difference_fraction(left_right, right_left),
            "final_metadata_identical": _metadata_signature(left_right) == _metadata_signature(right_left),
            "feature_divergence": {
                "lexical": _mean_feature_divergence(left_right, right_left, lexical_vector),
                "semantic": _mean_feature_divergence(left_right, right_left, semantic_vector),
                "style": _mean_feature_divergence(left_right, right_left, style_vector),
            },
            "combined": {
                "left_before_right": lr_metrics,
                "right_before_left": rl_metrics,
                "signed_person_top1_difference": effect,
                "absolute_person_top1_difference": abs(effect),
                "signed_generation_top1_difference": lr_metrics["generation_top1"] - rl_metrics["generation_top1"],
            },
            "single_channel_person_top1_difference": channel_deltas,
            "largest_changed_channel": strongest_channel,
        }
    return {"pairs": rows, "directional_person_effects": directional_effects}


def full_path_prediction(population, original: Sequence[Artifact], directional_effects: dict[str, float]) -> dict:
    rows = []
    ordered_pairs = list(combinations(TRANSFORM_NAMES, 2))
    for path in permutations(TRANSFORM_NAMES):
        final = _apply(original, path)
        observed = evaluate(population, final, WEIGHTS).person_top1
        score = 0.0
        for left, right in ordered_pairs:
            effect = directional_effects[_pair_key(left, right)]
            score += effect if path.index(left) < path.index(right) else -effect
        rows.append({"path": list(path), "pairwise_score": score, "observed_person_top1": observed})
    correlation = _pearson(
        [row["pairwise_score"] for row in rows],
        [row["observed_person_top1"] for row in rows],
    )
    return {
        "path_count": len(rows),
        "pearson_r": correlation,
        "paths": rows,
    }


def commuting_control(population, original: Sequence[Artifact]) -> dict:
    lower_then_space = [replace(row, text=" ".join(row.text.lower().split())) for row in original]
    space_then_lower = [replace(row, text=" ".join(row.text.split()).lower()) for row in original]
    left_metrics = evaluate(population, lower_then_space, WEIGHTS)
    right_metrics = evaluate(population, space_then_lower, WEIGHTS)
    text_equal = all(a.text == b.text for a, b in zip(lower_then_space, space_then_lower))
    metadata_equal = _metadata_signature(lower_then_space) == _metadata_signature(space_then_lower)
    return {
        "operations": ["lowercase", "normalize_whitespace"],
        "final_text_identical": text_equal,
        "final_metadata_identical": metadata_equal,
        "person_top1_difference": left_metrics.person_top1 - right_metrics.person_top1,
        "generation_top1_difference": left_metrics.generation_top1 - right_metrics.generation_top1,
        "control_pass": (
            text_equal
            and metadata_equal
            and left_metrics.person_top1 == right_metrics.person_top1
            and left_metrics.generation_top1 == right_metrics.generation_top1
        ),
    }


def run_experiment(persons: int = 12, seed: int = 41, artifact_seed: int = 7000) -> dict:
    population = generate_population(persons, seed)
    original = make_artifacts(population, seed=artifact_seed)
    pairwise = pairwise_mechanisms(population, original)
    prediction = full_path_prediction(population, original, pairwise["directional_person_effects"])
    control = commuting_control(population, original)
    r = prediction["pearson_r"]
    if not control["control_pass"]:
        status = "CONTROL_FAILED"
    elif r >= 0.70:
        status = "PAIRWISE_MECHANISM_PREDICTIVE_FOR_DECLARED_TEST"
    elif r >= 0.30:
        status = "PARTIAL_PAIRWISE_EXPLANATION"
    else:
        status = "PAIRWISE_MECHANISM_NOT_PREDICTIVE"
    return {
        "schema": "altru.dev/noncommutativity-mechanism/0.6",
        "research_scope": "synthetic-only",
        "predecessor_experiment_commit": "43d4b97a1c9b53a73de079ac166134fba663f494",
        "parameters": {
            "persons": persons,
            "generations": len(population),
            "seed": seed,
            "artifact_seed": artifact_seed,
            "transforms": list(TRANSFORM_NAMES),
        },
        "pairwise": pairwise,
        "full_path_prediction": prediction,
        "commuting_control": control,
        "claim": {
            "status": status,
            "boundary": "Declared synthetic population, transparent transformations, and attribution model only; not proof of anonymity or deployed-provider mechanism.",
        },
        "standing_rules": [
            "Privacy transformation != privacy evidence",
            "Failed re-identification != proven anonymity",
            "Synthetic benchmark mechanism != deployed-provider mechanism",
            "Predictor failure is a valid result",
        ],
    }


def main() -> None:
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
