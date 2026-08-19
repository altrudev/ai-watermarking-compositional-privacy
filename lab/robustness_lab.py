from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from itertools import combinations, permutations
from random import Random
from statistics import mean, median
from typing import Sequence
import hashlib
import json
import re

from lab.transformation_chain_lab import (
    Artifact,
    Generation,
    PARAPHRASE,
    SENTENCE_RE,
    TOPICS,
    TRANSLATION,
    WEIGHTS,
    evaluate,
    generate_population,
    make_artifacts,
    model_edit_stage,
    paraphrase_stage,
    summarize_stage,
    translate_stage,
    utility,
)

POLICIES = {
    "baseline": WEIGHTS,
    "lexical_heavy": (.55, .15, .10, .05, .00, .15),
    "semantic_heavy": (.15, .55, .10, .05, .00, .15),
    "style_heavy": (.15, .15, .50, .05, .00, .15),
    "content_only": (.45, .35, .20, .00, .00, .00),
}
TRANSFORM_NAMES = ("paraphrase", "summarize", "translate", "model_edit")


def _gate(artifact: Artifact, key: str, seed: int) -> float:
    payload = f"{seed}|{artifact.target_generation_id}|{key}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") / float(2**64 - 1)


def _partial_paraphrase(artifact: Artifact, strength: float, seed: int, stochastic: bool) -> Artifact:
    if strength >= 1.0 and not stochastic:
        return paraphrase_stage(artifact)
    text = artifact.text
    probability = max(0.0, min(1.0, strength))
    for source, target in sorted(PARAPHRASE.items(), key=lambda item: -len(item[0])):
        threshold = _gate(artifact, f"para:{source}", seed if stochastic else 0)
        if threshold < probability:
            text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.I)
    if strength >= .75:
        text = text.replace("The important part", "A key point").replace("What matters here", "A relevant point")
    return replace(artifact, text=text, watermark_family=None, provider_hint=None)


def _partial_summary(artifact: Artifact, strength: float, seed: int, stochastic: bool) -> Artifact:
    if strength >= 1.0 and not stochastic:
        return summarize_stage(artifact)
    sentences = [item.strip() for item in SENTENCE_RE.split(artifact.text) if item.strip()]
    keep_fraction = max(.25, min(1.0, 1.0 - .5 * strength))
    keep_count = max(2, min(len(sentences), round(len(sentences) * keep_fraction)))
    if stochastic and keep_count < len(sentences):
        rng = Random(int(_gate(artifact, "summary", seed) * (2**31 - 1)))
        indices = sorted(rng.sample(range(len(sentences)), keep_count))
        kept = [sentences[index] for index in indices]
    else:
        step = max(1, len(sentences) // keep_count)
        kept = sentences[::step][:keep_count]
    return replace(artifact, text=" ".join(kept), published_minute=artifact.published_minute + 90)


def _partial_translate(artifact: Artifact, strength: float, seed: int, stochastic: bool) -> Artifact:
    if strength >= 1.0 and not stochastic:
        return translate_stage(artifact)
    probability = max(0.0, min(1.0, strength))
    output = []
    for part in re.split(r"(\W+)", artifact.text):
        replacement = TRANSLATION.get(part.lower())
        if replacement is not None and _gate(artifact, f"translate:{part.lower()}", seed if stochastic else 0) >= probability:
            replacement = None
        output.append(replacement.capitalize() if replacement and part[:1].isupper() else replacement if replacement else part)
    return replace(artifact, text="".join(output), published_minute=artifact.published_minute + 120)


def _partial_model_edit(artifact: Artifact, strength: float, seed: int, stochastic: bool) -> Artifact:
    if strength >= 1.0 and not stochastic:
        return model_edit_stage(artifact)
    sentences = [item.strip() for item in SENTENCE_RE.split(artifact.text) if item.strip()]
    transformed = sentences[:]
    swaps = max(1, round(max(0, len(sentences) - 1) * max(0.0, min(1.0, strength)))) if sentences else 0
    if stochastic:
        rng = Random(int(_gate(artifact, "model", seed) * (2**31 - 1)))
        for _ in range(swaps):
            if len(transformed) > 1:
                left = rng.randrange(len(transformed) - 1)
                transformed[left], transformed[left + 1] = transformed[left + 1], transformed[left]
    else:
        for index in range(min(swaps, max(0, len(transformed) - 1))):
            transformed[index], transformed[index + 1] = transformed[index + 1], transformed[index]
    text = " ".join(transformed)
    if strength >= .5:
        text = text.replace("We ", "The analysis ").replace("?", ".")
    return replace(artifact, text=text, published_minute=artifact.published_minute + 180)


def _apply_transform(artifact: Artifact, name: str, strength: float, seed: int, stochastic: bool) -> Artifact:
    return {
        "paraphrase": _partial_paraphrase,
        "summarize": _partial_summary,
        "translate": _partial_translate,
        "model_edit": _partial_model_edit,
    }[name](artifact, strength, seed, stochastic)


def apply_path(artifacts: Sequence[Artifact], path: Sequence[str], strength: float = 1.0, seed: int = 0, stochastic: bool = False) -> list[Artifact]:
    if tuple(sorted(path)) != tuple(sorted(TRANSFORM_NAMES)) or len(path) != len(TRANSFORM_NAMES):
        raise ValueError("Path must contain each v0.5 transform exactly once")
    current = list(artifacts)
    for step, name in enumerate(path):
        current = [_apply_transform(row, name, strength, seed + step * 1009, stochastic) for row in current]
    return current


def _length_variant(population: Sequence[Generation], sentence_count: int) -> list[Generation]:
    if sentence_count == 6:
        return list(population)
    if sentence_count not in {3, 9}:
        raise ValueError("v0.5 length proxy supports 3, 6, or 9 sentences")
    output = []
    for row in population:
        sentences = [item.strip() for item in SENTENCE_RE.split(row.text) if item.strip()]
        if sentence_count == 3:
            text = " ".join(sentences[:3])
        else:
            extra = sentences[:3]
            text = " ".join(sentences + extra)
        output.append(replace(row, text=text))
    return output


def _mean_utility(original: Sequence[Artifact], current: Sequence[Artifact]) -> dict[str, float]:
    rows = [utility(left, right) for left, right in zip(original, current)]
    return {key: mean(row[key] for row in rows) for key in rows[0]}


def _metadata_signature(artifacts: Sequence[Artifact]):
    return tuple(sorted((row.target_generation_id, row.published_minute, row.provider_hint, row.watermark_family) for row in artifacts))


def _sample_artifacts(artifacts: Sequence[Artifact], limit: int | None) -> list[Artifact]:
    if limit is None or limit >= len(artifacts):
        return list(artifacts)
    if limit <= 0:
        raise ValueError("artifact_limit must be positive or None")
    indices = [round(i * (len(artifacts) - 1) / max(1, limit - 1)) for i in range(limit)]
    return [artifacts[index] for index in indices]


@lru_cache(maxsize=128)
def path_matrix(
    persons: int = 12,
    seed: int = 41,
    sentence_count: int = 6,
    strength: float = 1.0,
    stochastic: bool = False,
    policy: str = "baseline",
    artifact_limit: int | None = 36,
    artifact_seed: int | None = None,
) -> dict:
    if policy not in POLICIES:
        raise ValueError(f"Unknown policy: {policy}")
    population = _length_variant(generate_population(persons, seed), sentence_count)
    resolved_artifact_seed = 7000 + seed if artifact_seed is None else artifact_seed
    original = _sample_artifacts(make_artifacts(population, seed=resolved_artifact_seed), artifact_limit)
    results, signatures = [], set()
    for path in permutations(TRANSFORM_NAMES):
        final = apply_path(original, path, strength=strength, seed=seed, stochastic=stochastic)
        signatures.add(_metadata_signature(final))
        metrics = evaluate(population, final, POLICIES[policy])
        results.append({"path": list(path), "metrics": asdict(metrics), "utility": _mean_utility(original, final)})
    values = [row["metrics"]["person_top1"] for row in results]
    generation_values = [row["metrics"]["generation_top1"] for row in results]
    results.sort(key=lambda row: (row["metrics"]["person_top1"], row["metrics"]["generation_top1"], tuple(row["path"])))
    baseline = 1.0 / persons
    pairwise = {}
    for left, right in combinations(TRANSFORM_NAMES, 2):
        left_values = [row["metrics"]["person_top1"] for row in results if row["path"].index(left) < row["path"].index(right)]
        right_values = [row["metrics"]["person_top1"] for row in results if row["path"].index(right) < row["path"].index(left)]
        pairwise[f"{left}_before_{right}"] = mean(left_values) - mean(right_values)
    spread = max(values) - min(values)
    return {
        "parameters": {
            "persons": persons, "seed": seed, "sentence_count": sentence_count, "strength": strength,
            "stochastic": stochastic, "policy": policy, "artifact_limit": artifact_limit,
            "artifact_seed": resolved_artifact_seed,
        },
        "population_generations": len(population),
        "evaluated_artifacts": len(original),
        "random_person_baseline": baseline,
        "path_count": len(results),
        "final_metadata_identical_across_paths": len(signatures) == 1,
        "person_top1": {
            "minimum": min(values), "maximum": max(values), "mean": mean(values),
            "spread": spread, "median": median(values),
        },
        "generation_top1": {
            "minimum": min(generation_values), "maximum": max(generation_values), "mean": mean(generation_values),
        },
        "material_path_dependence": spread >= baseline,
        "best_path": results[0],
        "worst_path": results[-1],
        "mean_person_top1_by_first_transform": {
            name: mean(row["metrics"]["person_top1"] for row in results if row["path"][0] == name)
            for name in TRANSFORM_NAMES
        },
        "mean_person_top1_by_last_transform": {
            name: mean(row["metrics"]["person_top1"] for row in results if row["path"][-1] == name)
            for name in TRANSFORM_NAMES
        },
        "pairwise_order_differences": pairwise,
    }


def _commuting_control(artifacts: Sequence[Artifact]) -> dict:
    lower_then_space = [replace(row, text=" ".join(row.text.lower().split())) for row in artifacts]
    space_then_lower = [replace(row, text=" ".join(row.text.split()).lower()) for row in artifacts]
    text_equal = all(left.text == right.text for left, right in zip(lower_then_space, space_then_lower))
    metadata_equal = _metadata_signature(lower_then_space) == _metadata_signature(space_then_lower)
    return {
        "operations": ["lowercase", "normalize_space"],
        "final_text_identical": text_equal,
        "final_metadata_identical": metadata_equal,
        "control_pass": text_equal and metadata_equal,
    }


def run_robustness_experiment() -> dict:
    scenarios = [("canonical_full", path_matrix(persons=12, seed=41, artifact_limit=None, artifact_seed=7000))]
    for persons in (6, 16):
        scenarios.append((f"population_{persons}", path_matrix(persons=persons, seed=41, artifact_limit=18)))
    for seed in (17, 53):
        scenarios.append((f"seed_{seed}", path_matrix(persons=8, seed=seed, artifact_limit=18)))
    for sentence_count in (3, 9):
        scenarios.append((f"sentences_{sentence_count}", path_matrix(persons=8, seed=41, sentence_count=sentence_count, artifact_limit=18)))
    scenarios.append(("strength_0.50", path_matrix(persons=8, seed=41, strength=.50, artifact_limit=18)))
    scenarios.append(("stochastic_101", path_matrix(persons=8, seed=101, stochastic=True, strength=.75, artifact_limit=18)))
    for policy in ("lexical_heavy", "semantic_heavy", "style_heavy", "content_only"):
        scenarios.append((f"policy_{policy}", path_matrix(persons=8, seed=41, policy=policy, artifact_limit=18)))

    material = [row for _name, row in scenarios if row["material_path_dependence"]]
    spreads = [row["person_top1"]["spread"] for _name, row in scenarios]
    control_population = generate_population(12, 41)
    control = _commuting_control(make_artifacts(control_population, seed=7000))
    summarize_before_model = [row["pairwise_order_differences"]["summarize_before_model_edit"] for _name, row in scenarios]
    fraction = len(material) / len(scenarios)
    status = "robust_in_declared_matrix" if fraction >= .80 and control["control_pass"] else "mixed" if material else "not_established"
    return {
        "research_scope": "synthetic-only",
        "experiment": "v0.5 path-dependence robustness matrix",
        "scenario_count": len(scenarios),
        "scenario_families": [
            "population_size", "seed", "text_length", "transform_strength",
            "stochastic_transform", "attribution_policy", "commuting_control",
        ],
        "material_path_dependence_count": len(material),
        "material_path_dependence_fraction": fraction,
        "person_top1_spread": {
            "minimum": min(spreads), "maximum": max(spreads), "mean": mean(spreads), "median": median(spreads),
        },
        "summarize_before_model_edit_nonpositive_fraction": sum(value <= 0 for value in summarize_before_model) / len(summarize_before_model),
        "commuting_order_control": control,
        "scenarios": {name: row for name, row in scenarios},
        "claim": {
            "status": status,
            "statement": (
                "Transformation-order path dependence remained material across most declared synthetic perturbations and the commuting-order control remained invariant."
                if status == "robust_in_declared_matrix" else
                "The declared robustness matrix produced mixed evidence; path dependence should not yet be generalized."
                if status == "mixed" else
                "Material path dependence was not established across the declared robustness matrix."
            ),
            "boundary": "Synthetic identities, generated synthetic text, transparent transformations, and declared attribution policies only; not proof of deployed-system behavior.",
        },
        "standing_rules": [
            "Privacy transformation != privacy evidence.",
            "Failed re-identification != proven anonymity.",
            "Intermediate unlinkability != end-to-end unlinkability.",
            "Transformation set != transformation history != privacy outcome.",
            "Single benchmark result != robust system property.",
        ],
    }


def main() -> None:
    print(json.dumps(run_robustness_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
