from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from statistics import mean
from typing import Iterable, Sequence

from .textual_model import (
    TextArtifact, TextGeneration, assert_synthetic_only, cosine, lexical_vector, style_vector,
    topic_vector, tokens, transform_artifact, utility,
)


class Adversary(str, Enum):
    PUBLIC = "public_observer"
    DETECTOR = "detector_operator"
    PROVIDER = "ai_provider"
    COLLABORATING = "provider_plus_publisher"
    ADAPTIVE = "adaptive_provider_plus_publisher"


@dataclass(frozen=True)
class EvidencePolicy:
    semantic: float = 0.0
    style: float = 0.0
    lexical: float = 0.0
    watermark: float = 0.0
    provider: float = 0.0
    time: float = 0.0
    basis: str = "generation"

    def normalized(self) -> "EvidencePolicy":
        total = self.semantic + self.style + self.lexical + self.watermark + self.provider + self.time
        if total <= 0:
            raise ValueError("Evidence policy must enable at least one signal")
        return EvidencePolicy(self.semantic / total, self.style / total, self.lexical / total,
                              self.watermark / total, self.provider / total, self.time / total, self.basis)


@dataclass(frozen=True)
class Metrics:
    samples: int
    generation_top1: float
    generation_top5: float
    account_top1: float
    person_top1: float
    false_attribution_rate: float
    mean_generation_rank: float
    mean_anonymity_set: float


@dataclass(frozen=True)
class FrontierPoint:
    strength: float
    person_top1: float
    generation_top1: float
    semantic_retention: float
    content_retention: float


POLICIES: dict[Adversary, EvidencePolicy] = {
    Adversary.PUBLIC: EvidencePolicy(semantic=0.30, style=0.30, lexical=0.40, basis="person"),
    Adversary.DETECTOR: EvidencePolicy(semantic=0.24, style=0.22, lexical=0.29, watermark=0.20, provider=0.05, basis="person"),
    Adversary.PROVIDER: EvidencePolicy(semantic=0.42, style=0.16, lexical=0.22, watermark=0.12, provider=0.08, basis="generation"),
    Adversary.COLLABORATING: EvidencePolicy(semantic=0.30, style=0.14, lexical=0.20, watermark=0.10,
                                           provider=0.06, time=0.20, basis="generation"),
}


def _vocabulary(population: Sequence[TextGeneration]) -> tuple[str, ...]:
    vocab = set()
    for row in population:
        vocab.update(word for word in tokens(row.text) if word.startswith("sig"))
    return tuple(sorted(vocab))


def _average(vectors: Iterable[Sequence[float]]) -> tuple[float, ...]:
    rows = list(vectors)
    width = len(rows[0])
    return tuple(sum(row[i] for row in rows) / len(rows) for i in range(width))


def _profiles(population: Sequence[TextGeneration]):
    vocab = _vocabulary(population)
    by_person: dict[str, list[TextGeneration]] = {}
    for row in population:
        by_person.setdefault(row.person_id, []).append(row)
    person_profiles = {
        person_id: {
            "semantic": _average(topic_vector(row.text) for row in rows),
            "style": _average(style_vector(row.text) for row in rows),
            "lexical": _average(lexical_vector(row.text, vocab) for row in rows),
        }
        for person_id, rows in by_person.items()
    }
    generation_profiles = {
        row.generation_id: {
            "semantic": topic_vector(row.text),
            "style": style_vector(row.text),
            "lexical": lexical_vector(row.text, vocab),
        }
        for row in population
    }
    return vocab, person_profiles, generation_profiles


def _time_score(delta_minutes: int) -> float:
    return max(0.0, 1.0 - min(abs(delta_minutes), 360) / 360.0)


def evaluate(population: Sequence[TextGeneration], artifacts: Sequence[TextArtifact], policy: EvidencePolicy) -> Metrics:
    assert_synthetic_only(population)
    by_generation = {row.generation_id: row for row in population}
    vocab, person_profiles, generation_profiles = _profiles(population)
    p = policy.normalized()

    if p.basis == "person":
        seen, candidates = set(), []
        for row in population:
            if row.person_id not in seen:
                candidates.append(row)
                seen.add(row.person_id)
    else:
        candidates = list(population)

    candidate_features = [(cand, person_profiles[cand.person_id] if p.basis == "person"
                           else generation_profiles[cand.generation_id]) for cand in candidates]
    top1_generation = top5_generation = top1_account = top1_person = 0
    ranks, anonymity_sets = [], []

    for artifact in artifacts:
        truth = by_generation[artifact.target_generation_id]
        art_sem, art_style, art_lex = topic_vector(artifact.text), style_vector(artifact.text), lexical_vector(artifact.text, vocab)
        scored = []
        for cand, profile in candidate_features:
            score = p.semantic * max(0.0, cosine(art_sem, profile["semantic"]))
            score += p.style * max(0.0, cosine(art_style, profile["style"]))
            score += p.lexical * max(0.0, cosine(art_lex, profile["lexical"]))
            score += p.watermark * (1.0 if artifact.watermark_family and artifact.watermark_family == cand.watermark_family else 0.0)
            score += p.provider * (1.0 if artifact.provider_hint and artifact.provider_hint == cand.provider else 0.0)
            score += p.time * _time_score(artifact.published_minute - cand.created_minute)
            scored.append((score, cand))
        scored.sort(key=lambda pair: (-pair[0], pair[1].generation_id))
        winner = scored[0][1]
        top1_person += winner.person_id == truth.person_id
        top1_account += winner.account_id == truth.account_id
        top1_generation += winner.generation_id == truth.generation_id
        top5_generation += truth.generation_id in {cand.generation_id for _, cand in scored[:5]}
        target_id = truth.generation_id if p.basis == "generation" else truth.person_id
        rank = next((i + 1 for i, (_, cand) in enumerate(scored)
                     if (cand.generation_id if p.basis == "generation" else cand.person_id) == target_id), len(scored) + 1)
        ranks.append(rank)
        best = scored[0][0]
        anonymity_sets.append(sum(1 for score, _ in scored if best - score <= 0.015))

    n = max(1, len(artifacts))
    return Metrics(len(artifacts), top1_generation / n, top5_generation / n, top1_account / n, top1_person / n,
                   1.0 - top1_person / n, mean(ranks), mean(anonymity_sets))


def calibrate_adaptive_policy(population: Sequence[TextGeneration], calibration_artifacts: Sequence[TextArtifact]):
    signals = {
        "semantic": EvidencePolicy(semantic=1.0), "style": EvidencePolicy(style=1.0),
        "lexical": EvidencePolicy(lexical=1.0), "watermark": EvidencePolicy(watermark=1.0),
        "provider": EvidencePolicy(provider=1.0), "time": EvidencePolicy(time=1.0),
    }
    scores = {name: evaluate(population, calibration_artifacts, policy).person_top1 for name, policy in signals.items()}
    floor = 1.0 / len({row.person_id for row in population})
    weights = {name: max(0.001, score - floor) for name, score in scores.items()}
    return EvidencePolicy(**weights).normalized(), scores


def privacy_utility_frontier(population: Sequence[TextGeneration], artifacts: Sequence[TextArtifact],
                             strengths=(0.0, 0.25, 0.50, 0.75, 1.0)) -> list[FrontierPoint]:
    points = []
    for strength in strengths:
        transformed = [transform_artifact(artifact, strength) for artifact in artifacts]
        split = max(1, len(transformed) // 3)
        adaptive, _ = calibrate_adaptive_policy(population, transformed[:split])
        metrics = evaluate(population, transformed[split:], adaptive)
        utilities = [utility(original, changed) for original, changed in zip(artifacts, transformed)]
        points.append(FrontierPoint(float(strength), metrics.person_top1, metrics.generation_top1,
                                    mean(u.semantic_retention for u in utilities),
                                    mean(u.content_retention for u in utilities)))
    return points
