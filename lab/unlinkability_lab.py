from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from enum import Enum
from math import exp, sqrt
from random import Random
from statistics import mean
from typing import Iterable, Optional, Sequence
import json


class Adversary(str, Enum):
    PUBLIC = "public_observer"
    DETECTOR = "watermark_detector_operator"
    PROVIDER = "ai_provider"
    COLLABORATING = "provider_plus_publisher"


class Basis(str, Enum):
    PERSON = "person_profile"
    GENERATION = "generation_profile"


@dataclass(frozen=True)
class SyntheticGeneration:
    person_id: str
    account_id: str
    session_id: str
    generation_id: str
    provider: str
    model: str
    created_minute: int
    watermark_family: str
    person_semantic: tuple[float, ...]
    person_style: tuple[float, ...]
    generation_semantic: tuple[float, ...]
    generation_style: tuple[float, ...]


@dataclass(frozen=True)
class Artifact:
    target_generation_id: str
    published_minute: int
    provider_hint: Optional[str]
    watermark_family: Optional[str]
    semantic: tuple[float, ...]
    style: tuple[float, ...]


@dataclass(frozen=True)
class EvidencePolicy:
    semantic: float = 0.0
    style: float = 0.0
    watermark: float = 0.0
    provider: float = 0.0
    time: float = 0.0
    basis: Basis = Basis.GENERATION

    def normalized(self) -> "EvidencePolicy":
        total = self.semantic + self.style + self.watermark + self.provider + self.time
        if total <= 0:
            raise ValueError("Evidence policy must enable at least one signal")
        return EvidencePolicy(
            semantic=self.semantic / total,
            style=self.style / total,
            watermark=self.watermark / total,
            provider=self.provider / total,
            time=self.time / total,
            basis=self.basis,
        )


@dataclass(frozen=True)
class Metrics:
    samples: int
    generation_top1: float
    generation_top5: float
    account_top1: float
    person_top1: float
    mean_generation_rank: float
    mean_anonymity_set: float
    false_attribution_rate: float


@dataclass(frozen=True)
class Utility:
    semantic_retention: float
    style_retention: float


@dataclass(frozen=True)
class UnlinkabilityClaim:
    adversary: str
    status: str
    reason: str
    person_top1: float
    generation_top1: float
    mean_anonymity_set: float


POLICIES: dict[Adversary, EvidencePolicy] = {
    Adversary.PUBLIC: EvidencePolicy(semantic=0.55, style=0.45, basis=Basis.PERSON),
    Adversary.DETECTOR: EvidencePolicy(
        semantic=0.45, style=0.25, watermark=0.25, provider=0.05, basis=Basis.PERSON
    ),
    Adversary.PROVIDER: EvidencePolicy(
        semantic=0.70, style=0.15, watermark=0.10, provider=0.05, basis=Basis.GENERATION
    ),
    Adversary.COLLABORATING: EvidencePolicy(
        semantic=0.55,
        style=0.10,
        watermark=0.10,
        provider=0.05,
        time=0.20,
        basis=Basis.GENERATION,
    ),
}


def _norm(vector: Sequence[float]) -> float:
    return sqrt(sum(v * v for v in vector))


def _unit(vector: Sequence[float]) -> tuple[float, ...]:
    n = _norm(vector)
    if n == 0:
        return tuple(vector)
    return tuple(v / n for v in vector)


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector lengths differ")
    na, nb = _norm(a), _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def _jitter(vector: Sequence[float], rng: Random, sigma: float) -> tuple[float, ...]:
    return _unit(tuple(v + rng.gauss(0.0, sigma) for v in vector))


def _blend(a: Sequence[float], b: Sequence[float], weight_b: float) -> tuple[float, ...]:
    if not 0.0 <= weight_b <= 1.0:
        raise ValueError("blend weight must be in [0, 1]")
    return _unit(tuple((1.0 - weight_b) * x + weight_b * y for x, y in zip(a, b)))


def centroid(vectors: Iterable[Sequence[float]]) -> tuple[float, ...]:
    rows = list(vectors)
    if not rows:
        raise ValueError("Cannot compute centroid of empty population")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("Vector lengths differ")
    return _unit(tuple(sum(row[i] for row in rows) / len(rows) for i in range(width)))


def generate_population(
    persons: int = 60,
    accounts_per_person: int = 2,
    sessions_per_account: int = 4,
    generations_per_session: int = 2,
    seed: int = 17,
) -> list[SyntheticGeneration]:
    """Generate a deterministic synthetic-only population.

    The harness intentionally has no loader for real identity datasets in v0.1.
    Every identity is generated locally and carries the ``syn-`` prefix.
    """
    if min(persons, accounts_per_person, sessions_per_account, generations_per_session) <= 0:
        raise ValueError("Population dimensions must be positive")

    rng = Random(seed)
    providers = ("provider-a", "provider-b", "provider-c")
    models = ("model-1", "model-2")
    topic_centers = [_unit(tuple(rng.gauss(0, 1) for _ in range(10))) for _ in range(8)]
    style_centers = [_unit(tuple(rng.gauss(0, 1) for _ in range(8))) for _ in range(10)]
    rows: list[SyntheticGeneration] = []

    for person_index in range(persons):
        person_id = f"syn-person-{person_index:04d}"
        person_semantic = _jitter(topic_centers[person_index % len(topic_centers)], rng, 0.35)
        person_style = _jitter(style_centers[person_index % len(style_centers)], rng, 0.42)

        for account_index in range(accounts_per_person):
            account_id = f"{person_id}-acct-{account_index}"
            provider = providers[(person_index + account_index) % len(providers)]
            model = models[(person_index + 2 * account_index) % len(models)]
            watermark_family = f"{provider}:{model}"

            for session_index in range(sessions_per_account):
                session_id = f"{account_id}-sess-{session_index}"
                topic = topic_centers[(person_index + session_index + account_index) % len(topic_centers)]
                session_semantic = _blend(topic, person_semantic, 0.25)

                for generation_index in range(generations_per_session):
                    generation_id = f"{session_id}-gen-{generation_index}"
                    created_minute = 100_000 + (
                        person_index * 11
                        + account_index * 17
                        + session_index * 23
                        + generation_index * 7
                    ) % 240
                    rows.append(
                        SyntheticGeneration(
                            person_id=person_id,
                            account_id=account_id,
                            session_id=session_id,
                            generation_id=generation_id,
                            provider=provider,
                            model=model,
                            created_minute=created_minute,
                            watermark_family=watermark_family,
                            person_semantic=person_semantic,
                            person_style=person_style,
                            generation_semantic=_jitter(session_semantic, rng, 0.24),
                            generation_style=_jitter(person_style, rng, 0.28),
                        )
                    )

    assert_synthetic_only(rows)
    return rows


def assert_synthetic_only(population: Sequence[SyntheticGeneration]) -> None:
    if not population:
        raise ValueError("Population is empty")
    for row in population:
        ids = (row.person_id, row.account_id, row.session_id, row.generation_id)
        if not all(value.startswith("syn-") for value in ids):
            raise ValueError("v0.1 accepts synthetic identities only")


def make_artifacts(population: Sequence[SyntheticGeneration], seed: int = 9000) -> list[Artifact]:
    assert_synthetic_only(population)
    artifacts: list[Artifact] = []
    for index, row in enumerate(population):
        rng = Random(seed + index)
        artifacts.append(
            Artifact(
                target_generation_id=row.generation_id,
                published_minute=row.created_minute + rng.randint(2, 45),
                provider_hint=row.provider,
                watermark_family=row.watermark_family,
                semantic=_jitter(row.generation_semantic, rng, 0.33),
                style=_jitter(row.generation_style, rng, 0.36),
            )
        )
    return artifacts


def score_candidate(artifact: Artifact, candidate: SyntheticGeneration, policy: EvidencePolicy) -> float:
    p = policy.normalized()
    if p.basis == Basis.PERSON:
        semantic_reference = candidate.person_semantic
        style_reference = candidate.person_style
    else:
        semantic_reference = candidate.generation_semantic
        style_reference = candidate.generation_style

    semantic_score = (cosine(artifact.semantic, semantic_reference) + 1.0) / 2.0
    style_score = (cosine(artifact.style, style_reference) + 1.0) / 2.0
    watermark_score = float(
        artifact.watermark_family is not None
        and artifact.watermark_family == candidate.watermark_family
    )
    provider_score = float(
        artifact.provider_hint is not None and artifact.provider_hint == candidate.provider
    )

    delta = artifact.published_minute - candidate.created_minute
    time_score = exp(-delta / 50.0) if delta >= 0 else 0.0

    return (
        p.semantic * semantic_score
        + p.style * style_score
        + p.watermark * watermark_score
        + p.provider * provider_score
        + p.time * time_score
    )


def rank_candidates(
    artifact: Artifact,
    population: Sequence[SyntheticGeneration],
    policy: EvidencePolicy,
) -> list[tuple[SyntheticGeneration, float]]:
    assert_synthetic_only(population)
    ranked = [(candidate, score_candidate(artifact, candidate, policy)) for candidate in population]
    ranked.sort(key=lambda item: (-item[1], item[0].generation_id))
    return ranked


def evaluate(
    population: Sequence[SyntheticGeneration],
    artifacts: Sequence[Artifact],
    policy: EvidencePolicy,
    anonymity_band: float = 0.02,
) -> Metrics:
    assert_synthetic_only(population)
    if not artifacts:
        raise ValueError("No artifacts to evaluate")
    by_generation = {row.generation_id: row for row in population}

    generation_top1 = generation_top5 = account_top1 = person_top1 = 0
    ranks: list[int] = []
    anonymity_sets: list[int] = []

    for artifact in artifacts:
        target = by_generation.get(artifact.target_generation_id)
        if target is None:
            raise ValueError("Artifact target is outside the synthetic population")
        ranked = rank_candidates(artifact, population, policy)
        position = next(
            i for i, (candidate, _score) in enumerate(ranked)
            if candidate.generation_id == target.generation_id
        )
        predicted = ranked[0][0]
        generation_top1 += int(position == 0)
        generation_top5 += int(position < 5)
        account_top1 += int(predicted.account_id == target.account_id)
        person_top1 += int(predicted.person_id == target.person_id)
        ranks.append(position + 1)
        best_score = ranked[0][1]
        anonymity_sets.append(
            sum(1 for _candidate, candidate_score in ranked if candidate_score >= best_score - anonymity_band)
        )

    n = len(artifacts)
    person_rate = person_top1 / n
    return Metrics(
        samples=n,
        generation_top1=generation_top1 / n,
        generation_top5=generation_top5 / n,
        account_top1=account_top1 / n,
        person_top1=person_rate,
        mean_generation_rank=mean(ranks),
        mean_anonymity_set=mean(anonymity_sets),
        false_attribution_rate=1.0 - person_rate,
    )


def remove_provenance_marker(artifact: Artifact) -> Artifact:
    """Remove the simulated provider/model marker and provider hint.

    This models one linkage-channel removal. It is not represented as anonymization.
    """
    return replace(artifact, watermark_family=None, provider_hint=None)


def delay_publication(artifact: Artifact, minutes: int = 360) -> Artifact:
    if minutes < 0:
        raise ValueError("Delay must be non-negative")
    return replace(artifact, published_minute=artifact.published_minute + minutes)


def semantic_generalize(
    artifact: Artifact,
    semantic_centroid: Sequence[float],
    strength: float = 0.65,
) -> Artifact:
    return replace(artifact, semantic=_blend(artifact.semantic, semantic_centroid, strength))


def normalize_style(
    artifact: Artifact,
    style_centroid: Sequence[float],
    strength: float = 0.80,
) -> Artifact:
    return replace(artifact, style=_blend(artifact.style, style_centroid, strength))


def composite_privacy_transform(
    artifact: Artifact,
    semantic_centroid: Sequence[float],
    style_centroid: Sequence[float],
) -> Artifact:
    transformed = remove_provenance_marker(artifact)
    transformed = delay_publication(transformed, 360)
    transformed = semantic_generalize(transformed, semantic_centroid, 0.65)
    transformed = normalize_style(transformed, style_centroid, 0.80)
    return transformed


def utility(original: Artifact, transformed: Artifact) -> Utility:
    return Utility(
        semantic_retention=(cosine(original.semantic, transformed.semantic) + 1.0) / 2.0,
        style_retention=(cosine(original.style, transformed.style) + 1.0) / 2.0,
    )


def correlation_gain(combined: Metrics, singles: Sequence[Metrics]) -> float:
    if not singles:
        raise ValueError("At least one single-signal result is required")
    return combined.person_top1 - max(result.person_top1 for result in singles)


def evaluate_unlinkability_claim(
    adversary: Adversary,
    metrics: Metrics,
    *,
    max_person_top1: float = 0.10,
    max_generation_top1: float = 0.10,
    min_mean_anonymity_set: float = 3.0,
) -> UnlinkabilityClaim:
    """Evaluate a bounded unlinkability claim, never a universal anonymity claim."""
    conditions = [
        metrics.person_top1 <= max_person_top1,
        metrics.generation_top1 <= max_generation_top1,
        metrics.mean_anonymity_set >= min_mean_anonymity_set,
    ]
    if all(conditions):
        return UnlinkabilityClaim(
            adversary=adversary.value,
            status="supported_for_declared_test",
            reason=(
                "Re-identification stayed below the declared thresholds for this synthetic "
                "population, evidence policy, and adversary only. This is not proof of anonymity."
            ),
            person_top1=metrics.person_top1,
            generation_top1=metrics.generation_top1,
            mean_anonymity_set=metrics.mean_anonymity_set,
        )
    return UnlinkabilityClaim(
        adversary=adversary.value,
        status="not_supported",
        reason="At least one declared residual-linkability threshold was exceeded.",
        person_top1=metrics.person_top1,
        generation_top1=metrics.generation_top1,
        mean_anonymity_set=metrics.mean_anonymity_set,
    )


def run_reference_experiment(persons: int = 30, seed: int = 17) -> dict:
    population = generate_population(persons=persons, seed=seed)
    artifacts = make_artifacts(population)
    semantic_center = centroid(row.generation_semantic for row in population)
    style_center = centroid(row.generation_style for row in population)

    baseline = {
        adversary.value: evaluate(population, artifacts, policy)
        for adversary, policy in POLICIES.items()
    }

    single_signal_policies = {
        "semantic": EvidencePolicy(semantic=1.0, basis=Basis.GENERATION),
        "style": EvidencePolicy(style=1.0, basis=Basis.PERSON),
        "watermark": EvidencePolicy(watermark=1.0, basis=Basis.PERSON),
        "time": EvidencePolicy(time=1.0, basis=Basis.GENERATION),
    }
    single_signal = {
        name: evaluate(population, artifacts, policy)
        for name, policy in single_signal_policies.items()
    }

    transformed_sets = {
        "marker_removed": [remove_provenance_marker(a) for a in artifacts],
        "publication_delayed": [delay_publication(a) for a in artifacts],
        "semantic_generalized": [semantic_generalize(a, semantic_center) for a in artifacts],
        "style_normalized": [normalize_style(a, style_center) for a in artifacts],
        "composite": [
            composite_privacy_transform(a, semantic_center, style_center) for a in artifacts
        ],
    }
    collaborating_policy = POLICIES[Adversary.COLLABORATING]
    transformed = {
        name: evaluate(population, rows, collaborating_policy)
        for name, rows in transformed_sets.items()
    }

    utility_values = [utility(a, b) for a, b in zip(artifacts, transformed_sets["composite"])]
    combined_metrics = baseline[Adversary.COLLABORATING.value]
    gain = correlation_gain(combined_metrics, list(single_signal.values()))
    claim = evaluate_unlinkability_claim(
        Adversary.COLLABORATING,
        transformed["composite"],
    )

    def serializable(value):
        if hasattr(value, "__dataclass_fields__"):
            return asdict(value)
        return value

    return {
        "research_scope": "synthetic-only",
        "population_generations": len(population),
        "baseline": {k: serializable(v) for k, v in baseline.items()},
        "single_signal": {k: serializable(v) for k, v in single_signal.items()},
        "correlation_gain_person_top1": gain,
        "transformed": {k: serializable(v) for k, v in transformed.items()},
        "composite_utility": {
            "mean_semantic_retention": mean(v.semantic_retention for v in utility_values),
            "mean_style_retention": mean(v.style_retention for v in utility_values),
        },
        "unlinkability_claim": asdict(claim),
        "limitations": [
            "Synthetic linkage vectors are abstractions, not a detector for Claude or any other deployed watermark.",
            "No real people, accounts, conversations, provider logs, or platform datasets are used.",
            "A failed re-identification attempt is evidence only for the declared adversary and test configuration.",
        ],
    }


def main() -> None:
    print(json.dumps(run_reference_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
