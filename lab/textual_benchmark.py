from __future__ import annotations

from dataclasses import asdict, replace
from statistics import mean
import json

from .textual_attack import Adversary, EvidencePolicy, POLICIES, calibrate_adaptive_policy, evaluate, privacy_utility_frontier
from .textual_model import generate_text_population, make_artifacts, transform_artifact, utility


def run_reference_benchmark(seed: int = 73) -> dict:
    population = generate_text_population(seed=seed)
    artifacts = make_artifacts(population)
    baseline = {adversary.value: asdict(evaluate(population, artifacts, policy)) for adversary, policy in POLICIES.items()}
    singles = {
        "semantic": EvidencePolicy(semantic=1.0), "style": EvidencePolicy(style=1.0),
        "lexical": EvidencePolicy(lexical=1.0), "watermark": EvidencePolicy(watermark=1.0),
        "provider": EvidencePolicy(provider=1.0), "time": EvidencePolicy(time=1.0),
    }
    single = {name: asdict(evaluate(population, artifacts, policy)) for name, policy in singles.items()}
    strongest_single = max(metrics["person_top1"] for metrics in single.values())
    combined = baseline[Adversary.COLLABORATING.value]["person_top1"]

    provenance_removed = [replace(artifact, watermark_family=None, provider_hint=None) for artifact in artifacts]
    provenance_removed_metrics = asdict(evaluate(population, provenance_removed, POLICIES[Adversary.COLLABORATING]))

    transformed = [transform_artifact(artifact, 1.0) for artifact in artifacts]
    split = max(1, len(transformed) // 3)
    adaptive_policy, calibration_scores = calibrate_adaptive_policy(population, transformed[:split])
    transformed_metrics = asdict(evaluate(population, transformed[split:], adaptive_policy))
    utilities = [utility(original, changed) for original, changed in zip(artifacts, transformed)]
    frontier = [asdict(point) for point in privacy_utility_frontier(population, artifacts)]

    claim = "SUPPORTED_FOR_DECLARED_TEST" if combined > strongest_single and transformed_metrics["person_top1"] < combined else "NOT_SUPPORTED"
    return {
        "schema": "altru.dev/textual-compositional-privacy-benchmark/0.2",
        "status": "experimental-synthetic-benchmark",
        "claim": claim,
        "seed": seed,
        "population": {
            "persons": len({row.person_id for row in population}),
            "accounts": len({row.account_id for row in population}),
            "sessions": len({row.session_id for row in population}),
            "generations": len(population),
        },
        "baseline": baseline,
        "single_signal": single,
        "correlation_gain_pp": round((combined - strongest_single) * 100.0, 4),
        "provenance_removed_only": provenance_removed_metrics,
        "composite_transform_adaptive_attack": transformed_metrics,
        "adaptive_calibration_single_signal_person_top1": calibration_scores,
        "adaptive_policy": asdict(adaptive_policy),
        "utility": {
            "mean_semantic_retention": mean(item.semantic_retention for item in utilities),
            "mean_content_retention": mean(item.content_retention for item in utilities),
        },
        "privacy_utility_frontier": frontier,
        "boundaries": [
            "synthetic identities and synthetic text only", "simulated provenance signal only",
            "no real provider detector", "no real accounts or people",
            "privacy transformation is not privacy evidence", "failed re-identification is not proven anonymity",
        ],
    }


def main() -> None:
    print(json.dumps(run_reference_benchmark(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
