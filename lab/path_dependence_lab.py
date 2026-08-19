from __future__ import annotations

from dataclasses import asdict
from itertools import combinations, permutations
from statistics import mean
from typing import Sequence
import hashlib
import json

from lab.transformation_chain_lab import (
    Artifact,
    SINGLE_SIGNALS,
    evaluate,
    generate_population,
    make_artifacts,
    model_edit_stage,
    paraphrase_stage,
    summarize_stage,
    translate_stage,
    utility,
)

# v0.4 isolates order as the experimental variable.
# Every path contains exactly the same four transformations once.
TRANSFORMS = {
    "paraphrase": paraphrase_stage,
    "summarize": summarize_stage,
    "translate": translate_stage,
    "model_edit": model_edit_stage,
}
TRANSFORM_NAMES = tuple(TRANSFORMS)


def apply_path(artifacts: Sequence[Artifact], path: Sequence[str]) -> list[Artifact]:
    if tuple(sorted(path)) != tuple(sorted(TRANSFORM_NAMES)) or len(path) != len(TRANSFORM_NAMES):
        raise ValueError("Path must contain each v0.4 transform exactly once")
    current = list(artifacts)
    for name in path:
        current = [TRANSFORMS[name](artifact) for artifact in current]
    return current


def _aggregate_digest(artifacts: Sequence[Artifact]) -> str:
    digest = hashlib.sha256()
    for artifact in sorted(artifacts, key=lambda row: row.target_generation_id):
        digest.update(artifact.target_generation_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(artifact.text.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(artifact.published_minute).encode("ascii"))
        digest.update(b"\0")
        digest.update((artifact.provider_hint or "").encode("utf-8"))
        digest.update(b"\0")
        digest.update((artifact.watermark_family or "").encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _mean_utility(original: Sequence[Artifact], current: Sequence[Artifact]) -> dict[str, float]:
    rows = [utility(left, right) for left, right in zip(original, current)]
    return {key: mean(row[key] for row in rows) for key in rows[0]}


def _metadata_signature(artifacts: Sequence[Artifact]) -> tuple[tuple[str, int, str | None, str | None], ...]:
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


def _single_channel_report(population, artifacts: Sequence[Artifact]) -> dict:
    results = {
        signal: asdict(evaluate(population, artifacts, weights))
        for signal, weights in SINGLE_SIGNALS.items()
    }
    strongest_channel, strongest_metrics = max(
        results.items(),
        key=lambda item: (item[1]["person_top1"], item[0]),
    )
    return {
        "strongest_channel": strongest_channel,
        "strongest_channel_person_top1": strongest_metrics["person_top1"],
        "single_channel_metrics": results,
    }


def run_path_dependence_experiment(persons: int = 12, seed: int = 41) -> dict:
    if persons <= 1:
        raise ValueError("At least two synthetic persons are required")

    population = generate_population(persons, seed)
    original = make_artifacts(population)
    random_baseline = 1.0 / persons

    path_results: list[dict] = []
    final_artifacts_by_path: dict[tuple[str, ...], list[Artifact]] = {}
    metadata_signatures = set()

    for path in permutations(TRANSFORM_NAMES):
        final_artifacts = apply_path(original, path)
        final_artifacts_by_path[path] = final_artifacts
        metrics = evaluate(population, final_artifacts)
        metadata_signatures.add(_metadata_signature(final_artifacts))
        path_results.append(
            {
                "path": list(path),
                "final_artifact_digest": _aggregate_digest(final_artifacts),
                "metrics": asdict(metrics),
                "utility": _mean_utility(original, final_artifacts),
            }
        )

    path_results.sort(
        key=lambda row: (
            row["metrics"]["person_top1"],
            row["metrics"]["generation_top1"],
            tuple(row["path"]),
        )
    )

    person_values = [row["metrics"]["person_top1"] for row in path_results]
    generation_values = [row["metrics"]["generation_top1"] for row in path_results]

    first_effects = {
        name: mean(
            row["metrics"]["person_top1"]
            for row in path_results
            if row["path"][0] == name
        )
        for name in TRANSFORM_NAMES
    }
    last_effects = {
        name: mean(
            row["metrics"]["person_top1"]
            for row in path_results
            if row["path"][-1] == name
        )
        for name in TRANSFORM_NAMES
    }

    pairwise_order_effects = {}
    for left, right in combinations(TRANSFORM_NAMES, 2):
        left_before = [
            row["metrics"]["person_top1"]
            for row in path_results
            if row["path"].index(left) < row["path"].index(right)
        ]
        right_before = [
            row["metrics"]["person_top1"]
            for row in path_results
            if row["path"].index(right) < row["path"].index(left)
        ]
        pairwise_order_effects[f"{left}_before_{right}"] = {
            "left_before_right_mean_person_top1": mean(left_before),
            "right_before_left_mean_person_top1": mean(right_before),
            "difference": mean(left_before) - mean(right_before),
        }

    unique_artifact_digests = len({row["final_artifact_digest"] for row in path_results})
    spread = max(person_values) - min(person_values)
    materiality_threshold = random_baseline

    best = path_results[0]
    worst = path_results[-1]
    best_key = tuple(best["path"])
    worst_key = tuple(worst["path"])
    best["channel_analysis"] = _single_channel_report(population, final_artifacts_by_path[best_key])
    worst["channel_analysis"] = _single_channel_report(population, final_artifacts_by_path[worst_key])

    return {
        "research_scope": "synthetic-only",
        "experiment": "transformation-order path dependence",
        "population": {
            "persons": persons,
            "generations": len(population),
        },
        "transform_multiset": list(TRANSFORM_NAMES),
        "path_count": len(path_results),
        "random_person_baseline": random_baseline,
        "controlled_conditions": {
            "same_transform_multiset_every_path": True,
            "same_transform_count_every_path": True,
            "final_metadata_signature_count": len(metadata_signatures),
            "final_metadata_identical_across_paths": len(metadata_signatures) == 1,
            "all_paths_remove_provider_and_watermark": all(
                sig_row[2] is None and sig_row[3] is None
                for signature in metadata_signatures
                for sig_row in signature
            ),
            "order_is_primary_manipulated_variable": len(metadata_signatures) == 1,
        },
        "person_top1": {
            "minimum": min(person_values),
            "maximum": max(person_values),
            "mean": mean(person_values),
            "spread": spread,
            "spread_in_percentage_points": spread * 100.0,
        },
        "generation_top1": {
            "minimum": min(generation_values),
            "maximum": max(generation_values),
            "mean": mean(generation_values),
        },
        "unique_final_artifact_digests": unique_artifact_digests,
        "best_path": best,
        "worst_path": worst,
        "mean_person_top1_by_first_transform": first_effects,
        "mean_person_top1_by_last_transform": last_effects,
        "pairwise_order_effects": pairwise_order_effects,
        "paths": path_results,
        "claim": {
            "status": "path_dependent" if spread >= materiality_threshold else "not_established",
            "materiality_threshold": materiality_threshold,
            "statement": (
                "The same transformation multiset produced materially different residual attribution "
                "when only transformation order changed."
                if spread >= materiality_threshold
                else
                "Material path dependence was not established under the declared threshold."
            ),
            "boundary": (
                "Synthetic identities, transparent deterministic transformations, and the declared "
                "attribution model only; this is not proof of behavior in deployed AI systems."
            ),
        },
        "standing_rules": [
            "Privacy transformation != privacy evidence.",
            "Failed re-identification != proven anonymity.",
            "Intermediate unlinkability != end-to-end unlinkability.",
            "Same transformations != same privacy outcome.",
        ],
    }


def main() -> None:
    print(json.dumps(run_path_dependence_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
