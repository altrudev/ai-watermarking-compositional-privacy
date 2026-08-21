from __future__ import annotations

from dataclasses import replace
from itertools import combinations
from statistics import mean
import json

from lab.cross_family_replication_lab import FAMILIES, POLICIES, SCENARIOS, _apply, prepare_scenario
from lab.transformation_chain_lab import (
    SINGLE_SIGNALS,
    cosine,
    lexical_vector,
    semantic_vector,
    style_vector,
)

# The historical SINGLE_SIGNALS helper predates provider-only reporting and
# contains lexical/semantic/style/watermark/time. v0.7's frozen scorer has six
# declared channels, so diagnostics add provider explicitly without changing
# any scoring, policy, transformation, partition, or claim threshold.
DIAGNOSTIC_SIGNALS = {
    **SINGLE_SIGNALS,
    "provider": (0, 0, 0, 0, 1, 0),
}


def _metadata_signature(artifacts):
    return tuple(
        (
            artifact.target_generation_id,
            artifact.published_minute,
            artifact.provider_hint,
            artifact.watermark_family,
        )
        for artifact in artifacts
    )


def _mean_feature_divergence(left, right, vectorizer) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Pairwise diagnostics require non-empty equal artifact sets")
    return mean(
        1.0 - max(-1.0, min(1.0, cosine(vectorizer(a.text), vectorizer(b.text))))
        for a, b in zip(left, right)
    )


def _text_difference_fraction(left, right) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Pairwise diagnostics require non-empty equal artifact sets")
    return mean(float(a.text != b.text) for a, b in zip(left, right))


def scenario_commuting_control_diagnostics(scenario_name: str) -> dict:
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    _population, _calibration, holdout, evaluator = prepare_scenario(scenario_name)
    lower_then_space = [
        replace(row, text=" ".join(row.text.lower().split()))
        for row in holdout
    ]
    space_then_lower = [
        replace(row, text=" ".join(row.text.split()).lower())
        for row in holdout
    ]
    final_text_identical = all(
        left.text == right.text
        for left, right in zip(lower_then_space, space_then_lower)
    )
    final_metadata_identical = (
        _metadata_signature(lower_then_space) == _metadata_signature(space_then_lower)
    )
    policies = {}
    for policy_name, weights in POLICIES.items():
        left_metrics = evaluator.evaluate(lower_then_space, weights)
        right_metrics = evaluator.evaluate(space_then_lower, weights)
        person_delta = left_metrics.person_top1 - right_metrics.person_top1
        generation_delta = left_metrics.generation_top1 - right_metrics.generation_top1
        policies[policy_name] = {
            "person_top1_difference": person_delta,
            "generation_top1_difference": generation_delta,
            "control_pass": (
                final_text_identical
                and final_metadata_identical
                and person_delta == 0
                and generation_delta == 0
            ),
        }
    return {
        "scenario": scenario_name,
        "holdout_samples": len(holdout),
        "final_text_identical": final_text_identical,
        "final_metadata_identical": final_metadata_identical,
        "policies": policies,
        "all_policies_pass": all(row["control_pass"] for row in policies.values()),
    }


def scenario_pairwise_diagnostics(scenario_name: str) -> dict:
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    population, calibration, _holdout, evaluator = prepare_scenario(scenario_name)
    family_rows = {}

    for family_name, transforms in FAMILIES.items():
        pair_rows = {}
        for left_name, right_name in combinations(tuple(transforms), 2):
            left_right = _apply(calibration, transforms, (left_name, right_name))
            right_left = _apply(calibration, transforms, (right_name, left_name))

            policy_deltas = {}
            for policy_name, weights in POLICIES.items():
                left_metrics = evaluator.evaluate(left_right, weights)
                right_metrics = evaluator.evaluate(right_left, weights)
                policy_deltas[policy_name] = {
                    "person_top1_difference": left_metrics.person_top1 - right_metrics.person_top1,
                    "generation_top1_difference": left_metrics.generation_top1 - right_metrics.generation_top1,
                }

            single_channel_deltas = {}
            for channel_name, weights in DIAGNOSTIC_SIGNALS.items():
                left_metrics = evaluator.evaluate(left_right, weights)
                right_metrics = evaluator.evaluate(right_left, weights)
                single_channel_deltas[channel_name] = (
                    left_metrics.person_top1 - right_metrics.person_top1
                )

            max_delta = max(abs(value) for value in single_channel_deltas.values())
            largest_changed_channels = sorted(
                name
                for name, value in single_channel_deltas.items()
                if abs(value) == max_delta
            )

            pair_key = f"{left_name}|{right_name}"
            pair_rows[pair_key] = {
                "left_before_right": [left_name, right_name],
                "right_before_left": [right_name, left_name],
                "calibration_samples": len(calibration),
                "final_text_difference_fraction": _text_difference_fraction(left_right, right_left),
                "final_metadata_identical": (
                    _metadata_signature(left_right) == _metadata_signature(right_left)
                ),
                "feature_divergence": {
                    "lexical": _mean_feature_divergence(left_right, right_left, lexical_vector),
                    "semantic": _mean_feature_divergence(left_right, right_left, semantic_vector),
                    "style": _mean_feature_divergence(left_right, right_left, style_vector),
                },
                "policy_order_effects": policy_deltas,
                "single_channel_person_top1_difference": single_channel_deltas,
                "largest_changed_channels": largest_changed_channels,
                "largest_absolute_channel_delta": max_delta,
            }

        family_rows[family_name] = {
            "transform_names": list(transforms),
            "pair_count": len(pair_rows),
            "pairs": pair_rows,
        }

    return {
        "schema": "altru.dev/cross-family-replication-pairwise-diagnostics/0.7",
        "research_scope": "synthetic-only",
        "protocol_commit": "786ebb3d097d999e15f72cbfce536e59566206a1",
        "scenario": scenario_name,
        "population_generations": len(population),
        "families": family_rows,
    }


def run_all_pairwise_diagnostics() -> dict:
    return {
        "schema": "altru.dev/cross-family-replication-pairwise-diagnostics-set/0.7",
        "research_scope": "synthetic-only",
        "protocol_commit": "786ebb3d097d999e15f72cbfce536e59566206a1",
        "controls": {
            scenario_name: scenario_commuting_control_diagnostics(scenario_name)
            for scenario_name in SCENARIOS
        },
        "scenarios": {
            scenario_name: scenario_pairwise_diagnostics(scenario_name)
            for scenario_name in SCENARIOS
        },
    }


def main() -> None:
    print(json.dumps(run_all_pairwise_diagnostics(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
