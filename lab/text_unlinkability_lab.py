from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, replace
from enum import Enum
from math import exp, sqrt
from random import Random
from statistics import mean, pstdev
from typing import Iterable, Optional, Sequence
import hashlib
import json
import re


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class TextAdversary(str, Enum):
    PUBLIC = "public_observer"
    DETECTOR = "watermark_detector_operator"
    PROVIDER = "ai_provider"
    COLLABORATING = "provider_plus_publisher"


@dataclass(frozen=True)
class Topic:
    name: str
    terms: tuple[str, ...]
    paraphrases: tuple[str, ...]


TOPICS = (
    Topic("privacy", ("privacy", "identity", "linkage", "metadata", "consent", "anonymity"),
          ("confidentiality", "personhood", "association", "context data", "permission", "unlinkability")),
    Topic("security", ("security", "authority", "access", "verification", "attack", "recovery"),
          ("protection", "authorization", "entry", "validation", "threat", "restoration")),
    Topic("systems", ("system", "transition", "state", "resource", "boundary", "invariant"),
          ("architecture", "change", "condition", "capacity", "limit", "constraint")),
    Topic("provenance", ("provenance", "watermark", "attribution", "origin", "evidence", "trace"),
          ("lineage", "marker", "association", "source", "proof", "trail")),
    Topic("agents", ("agent", "memory", "tool", "directive", "model", "execution"),
          ("worker", "context", "instrument", "instruction", "engine", "operation")),
    Topic("networks", ("network", "signal", "correlation", "channel", "graph", "propagation"),
          ("mesh", "indicator", "association", "path", "map", "spread")),
)

ALL_TOPIC_TERMS = {term for topic in TOPICS for term in topic.terms}
PARAPHRASE_MAP = {
    term: repl
    for topic in TOPICS
    for term, repl in zip(topic.terms, topic.paraphrases)
}
REVERSE_PARAPHRASE_MAP = {v: k for k, v in PARAPHRASE_MAP.items()}

TRANSITIONS = (
    "however", "therefore", "in practice", "more importantly", "at the same time",
    "for example", "in other words", "the important part is", "as a result", "still",
    "from there", "in that case",
)
HEDGES = ("probably", "roughly", "usually", "potentially", "in principle", "often", "sometimes", "arguably")
SIGNATURES = (
    "the important part", "what matters here", "the actual issue", "the useful question",
    "in practical terms", "the main point", "the interesting part", "the real distinction",
    "from a systems view", "at the architecture level", "in this case", "the key detail",
)
GENERIC_WORDS = ("system", "process", "information", "result", "context", "risk")


@dataclass(frozen=True)
class SyntheticAuthorStyle:
    transition: str
    hedge: str
    signature: str
    target_sentence_words: int
    contraction_rate: float
    comma_rate: float
    question_rate: float


@dataclass(frozen=True)
class SyntheticTextGeneration:
    person_id: str
    account_id: str
    session_id: str
    generation_id: str
    provider: str
    model: str
    created_minute: int
    watermark_family: str
    topic: str
    text: str


@dataclass(frozen=True)
class TextArtifact:
    target_generation_id: str
    text: str
    published_minute: int
    provider_hint: Optional[str]
    watermark_family: Optional[str]


@dataclass(frozen=True)
class TextEvidencePolicy:
    lexical: float = 0.0
    semantic: float = 0.0
    style: float = 0.0
    watermark: float = 0.0
    provider: float = 0.0
    time: float = 0.0

    def normalized(self) -> "TextEvidencePolicy":
        total = self.lexical + self.semantic + self.style + self.watermark + self.provider + self.time
        if total <= 0:
            raise ValueError("Evidence policy must enable at least one signal")
        return TextEvidencePolicy(
            lexical=self.lexical / total,
            semantic=self.semantic / total,
            style=self.style / total,
            watermark=self.watermark / total,
            provider=self.provider / total,
            time=self.time / total,
        )


TEXT_POLICIES = {
    TextAdversary.PUBLIC: TextEvidencePolicy(lexical=.35, semantic=.25, style=.40),
    TextAdversary.DETECTOR: TextEvidencePolicy(lexical=.28, semantic=.22, style=.25, watermark=.20, provider=.05),
    TextAdversary.PROVIDER: TextEvidencePolicy(lexical=.45, semantic=.25, style=.10, watermark=.10, provider=.10),
    TextAdversary.COLLABORATING: TextEvidencePolicy(
        lexical=.30, semantic=.20, style=.10, watermark=.10, provider=.05, time=.25
    ),
}


@dataclass(frozen=True)
class TextMetrics:
    samples: int
    generation_top1: float
    generation_top5: float
    account_top1: float
    person_top1: float
    mean_generation_rank: float
    mean_anonymity_set: float


@dataclass(frozen=True)
class TextUtility:
    topic_retention: float
    content_word_retention: float
    length_ratio: float


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def _norm(v: Sequence[float]) -> float:
    return sqrt(sum(x*x for x in v))


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector lengths differ")
    na, nb = _norm(a), _norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return sum(x*y for x, y in zip(a, b)) / (na*nb)


def _hash_bucket(token: str, buckets: int = 96) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % buckets


def lexical_vector(text: str, buckets: int = 96) -> tuple[float, ...]:
    counts = [0.0] * buckets
    boilerplate = {
        "the", "a", "an", "and", "or", "to", "of", "is", "are", "it", "this", "that",
        "can", "may", "still", "needs", "own", "rather", "than", "evaluated", "alone",
        "question", "depends", "because", "change", "how", "interpreted", "surrounding",
        "signal", "combine", "changes", "practical", "meaning", "tested", "against",
    }
    style_tokens = set()
    for phrase in TRANSITIONS + HEDGES + SIGNATURES:
        style_tokens.update(_tokens(phrase))
    ignored = boilerplate | style_tokens
    for token in _tokens(text):
        if token in ignored:
            continue
        counts[_hash_bucket(token, buckets)] += 1.0
    n = _norm(counts)
    return tuple(x / n for x in counts) if n else tuple(counts)


def _canonical_concept(token: str) -> str:
    if token in REVERSE_PARAPHRASE_MAP:
        return REVERSE_PARAPHRASE_MAP[token]
    return token


def semantic_vector(text: str) -> tuple[float, ...]:
    normalized_text = text.lower()
    for paraphrase, original in sorted(REVERSE_PARAPHRASE_MAP.items(), key=lambda x: -len(x[0])):
        normalized_text = re.sub(rf"\b{re.escape(paraphrase)}\b", original, normalized_text, flags=re.I)
    tokens = [_canonical_concept(t) for t in _tokens(normalized_text)]
    vector = []
    for topic in TOPICS:
        terms = set(topic.terms)
        vector.append(float(sum(1 for t in tokens if t in terms)))
    vector.append(float(sum(1 for t in tokens if t in GENERIC_WORDS)))
    n = _norm(vector)
    return tuple(x / n for x in vector) if n else tuple(vector)


def style_vector(text: str) -> tuple[float, ...]:
    tokens = _tokens(text)
    if not tokens:
        return (0.0,) * 16
    sentences = [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]
    if not sentences:
        sentences = [text]
    sent_lengths = [max(1, len(_tokens(s))) for s in sentences]
    words = len(tokens)
    unique = len(set(tokens))
    chars = sum(len(t) for t in tokens)
    lower = text.lower()
    transitions = sum(lower.count(x) for x in TRANSITIONS)
    hedges = sum(lower.count(x) for x in HEDGES)
    signatures = sum(lower.count(x) for x in SIGNATURES)
    contractions = sum(1 for t in tokens if "'" in t)
    first_person = sum(1 for t in tokens if t in {"i", "me", "my", "we", "our", "us"})
    return (
        min(mean(sent_lengths) / 30.0, 1.0),
        min(pstdev(sent_lengths) / 15.0, 1.0) if len(sent_lengths) > 1 else 0.0,
        min((chars / words) / 10.0, 1.0),
        unique / words,
        min(text.count(",") / max(1, words) * 8.0, 1.0),
        min(text.count(";") / max(1, words) * 20.0, 1.0),
        min(text.count(":") / max(1, words) * 20.0, 1.0),
        min((text.count("—") + text.count(" - ")) / max(1, words) * 15.0, 1.0),
        min(text.count("?") / max(1, len(sentences)) * 2.0, 1.0),
        min(text.count("!") / max(1, len(sentences)) * 2.0, 1.0),
        min(first_person / words * 10.0, 1.0),
        min(hedges / max(1, len(sentences)), 1.0),
        min(transitions / max(1, len(sentences)), 1.0),
        min(signatures / max(1, len(sentences)), 1.0),
        min(contractions / words * 20.0, 1.0),
        min(text.count("\n\n") / max(1, len(sentences)), 1.0),
    )


def _author_style(person_index: int) -> SyntheticAuthorStyle:
    return SyntheticAuthorStyle(
        transition=TRANSITIONS[person_index % len(TRANSITIONS)],
        hedge=HEDGES[(person_index * 3) % len(HEDGES)],
        signature=SIGNATURES[(person_index * 5) % len(SIGNATURES)],
        target_sentence_words=(12, 16, 20, 24)[person_index % 4],
        contraction_rate=(0.0, 0.25, 0.5, 0.75)[(person_index // 2) % 4],
        comma_rate=(0.15, 0.35, 0.55)[(person_index // 3) % 3],
        question_rate=(0.0, 0.15, 0.30)[(person_index // 5) % 3],
    )


def _maybe_contract(text: str, rng: Random, rate: float) -> str:
    if rng.random() < rate:
        text = text.replace("it is", "it's").replace("do not", "don't").replace("cannot", "can't")
    return text


def _sentence(style: SyntheticAuthorStyle, topic: Topic, rng: Random, index: int) -> str:
    terms = list(topic.terms)
    rng.shuffle(terms)
    a, b, c, d = terms[:4]
    templates = (
        f"{style.transition.capitalize()}, the {a} question depends on {b}, because {c} can change how the {d} is interpreted",
        f"{style.signature.capitalize()} is that {a} and {b} are not interchangeable; {c} still needs its own {d}",
        f"We {style.hedge} treat {a} as a signal, but the surrounding {b} can turn that signal into {c} through {d}",
        f"The {a} may look isolated, yet {b} and {c} can combine, which changes the practical meaning of {d}",
        f"If {a} survives while {b} is removed, does the remaining {c} still expose the {d}",
        f"This is why {a} needs to be tested against {b}, {c}, and the resulting {d} rather than evaluated alone",
    )
    text = templates[index % len(templates)]
    if rng.random() < style.comma_rate:
        text = text.replace(" because ", ", because ", 1)
    if rng.random() < style.question_rate and index == 4:
        text += "?"
    else:
        text += "."
    return _maybe_contract(text, rng, style.contraction_rate)


def generate_text_population(
    persons: int = 36,
    accounts_per_person: int = 2,
    sessions_per_account: int = 3,
    generations_per_session: int = 2,
    seed: int = 29,
) -> list[SyntheticTextGeneration]:
    if min(persons, accounts_per_person, sessions_per_account, generations_per_session) <= 0:
        raise ValueError("Population dimensions must be positive")
    rng = Random(seed)
    providers = ("provider-a", "provider-b", "provider-c")
    models = ("model-1", "model-2")
    rows: list[SyntheticTextGeneration] = []

    for p in range(persons):
        person_id = f"syn-person-{p:04d}"
        style = _author_style(p)
        for a in range(accounts_per_person):
            account_id = f"{person_id}-acct-{a}"
            provider = providers[(p + a) % len(providers)]
            model = models[(p + 2*a) % len(models)]
            watermark = f"{provider}:{model}"
            for s in range(sessions_per_account):
                session_id = f"{account_id}-sess-{s}"
                topic = TOPICS[(p + a + s) % len(TOPICS)]
                for g in range(generations_per_session):
                    generation_id = f"{session_id}-gen-{g}"
                    local_rng = Random(seed * 100000 + p*1000 + a*100 + s*10 + g)
                    sentence_count = 5 + ((p + s + g) % 3)
                    sentences = [_sentence(style, topic, local_rng, i + g) for i in range(sentence_count)]
                    if (p + g) % 3 == 0 and len(sentences) >= 6:
                        text = " ".join(sentences[:3]) + "\n\n" + " ".join(sentences[3:])
                    else:
                        text = " ".join(sentences)
                    created = 200_000 + (p*13 + a*19 + s*29 + g*7) % 300
                    rows.append(SyntheticTextGeneration(
                        person_id=person_id,
                        account_id=account_id,
                        session_id=session_id,
                        generation_id=generation_id,
                        provider=provider,
                        model=model,
                        created_minute=created,
                        watermark_family=watermark,
                        topic=topic.name,
                        text=text,
                    ))
    assert_synthetic_text_only(rows)
    return rows


def assert_synthetic_text_only(population: Sequence[SyntheticTextGeneration]) -> None:
    if not population:
        raise ValueError("Population is empty")
    for row in population:
        for value in (row.person_id, row.account_id, row.session_id, row.generation_id):
            if not value.startswith("syn-"):
                raise ValueError("v0.2 accepts synthetic identities only")


def make_text_artifacts(population: Sequence[SyntheticTextGeneration], seed: int = 4400) -> list[TextArtifact]:
    assert_synthetic_text_only(population)
    artifacts = []
    for i, row in enumerate(population):
        rng = Random(seed + i)
        text = paraphrase_surface(row.text)
        if i % 4 == 0:
            text = text.replace("This is why", "This is also why", 1)
        artifacts.append(TextArtifact(
            target_generation_id=row.generation_id,
            text=text,
            published_minute=row.created_minute + rng.randint(2, 50),
            provider_hint=row.provider,
            watermark_family=row.watermark_family,
        ))
    return artifacts


def _centroid(vectors: Iterable[Sequence[float]]) -> tuple[float, ...]:
    rows = list(vectors)
    if not rows:
        raise ValueError("Cannot compute centroid of empty rows")
    width = len(rows[0])
    values = tuple(sum(row[i] for row in rows)/len(rows) for i in range(width))
    n = _norm(values)
    return tuple(x/n for x in values) if n else values


def person_style_profiles(population: Sequence[SyntheticTextGeneration]) -> dict[str, tuple[float, ...]]:
    groups: dict[str, list[tuple[float, ...]]] = defaultdict(list)
    for row in population:
        groups[row.person_id].append(style_vector(row.text))
    return {person: _centroid(vectors) for person, vectors in groups.items()}


def _candidate_features(
    population: Sequence[SyntheticTextGeneration],
) -> tuple[
    dict[str, tuple[float, ...]],
    dict[str, tuple[float, ...]],
    dict[str, tuple[float, ...]],
]:
    lexical = {row.generation_id: lexical_vector(row.text) for row in population}
    semantic = {row.generation_id: semantic_vector(row.text) for row in population}
    styles = person_style_profiles(population)
    return lexical, semantic, styles


def score_text_candidate(
    artifact: TextArtifact,
    candidate: SyntheticTextGeneration,
    policy: TextEvidencePolicy,
    style_profiles: dict[str, tuple[float, ...]],
    *,
    artifact_lexical: Optional[tuple[float, ...]] = None,
    artifact_semantic: Optional[tuple[float, ...]] = None,
    artifact_style: Optional[tuple[float, ...]] = None,
    candidate_lexical: Optional[tuple[float, ...]] = None,
    candidate_semantic: Optional[tuple[float, ...]] = None,
) -> float:
    p = policy.normalized()
    a_lex = artifact_lexical or lexical_vector(artifact.text)
    a_sem = artifact_semantic or semantic_vector(artifact.text)
    a_style = artifact_style or style_vector(artifact.text)
    c_lex = candidate_lexical or lexical_vector(candidate.text)
    c_sem = candidate_semantic or semantic_vector(candidate.text)

    lexical = (cosine(a_lex, c_lex) + 1.0)/2.0
    semantic = (cosine(a_sem, c_sem) + 1.0)/2.0
    style = (cosine(a_style, style_profiles[candidate.person_id]) + 1.0)/2.0
    watermark = float(artifact.watermark_family is not None and artifact.watermark_family == candidate.watermark_family)
    provider = float(artifact.provider_hint is not None and artifact.provider_hint == candidate.provider)
    delta = artifact.published_minute - candidate.created_minute
    time = exp(-delta/60.0) if delta >= 0 else 0.0
    return p.lexical*lexical + p.semantic*semantic + p.style*style + p.watermark*watermark + p.provider*provider + p.time*time


def rank_text_candidates(
    artifact: TextArtifact,
    population: Sequence[SyntheticTextGeneration],
    policy: TextEvidencePolicy,
    style_profiles: Optional[dict[str, tuple[float, ...]]] = None,
) -> list[tuple[SyntheticTextGeneration, float]]:
    assert_synthetic_text_only(population)
    c_lex, c_sem, profiles = _candidate_features(population)
    if style_profiles is not None:
        profiles = style_profiles
    a_lex = lexical_vector(artifact.text)
    a_sem = semantic_vector(artifact.text)
    a_style = style_vector(artifact.text)
    ranked = [
        (
            row,
            score_text_candidate(
                artifact,
                row,
                policy,
                profiles,
                artifact_lexical=a_lex,
                artifact_semantic=a_sem,
                artifact_style=a_style,
                candidate_lexical=c_lex[row.generation_id],
                candidate_semantic=c_sem[row.generation_id],
            ),
        )
        for row in population
    ]
    ranked.sort(key=lambda item: (-item[1], item[0].generation_id))
    return ranked


def evaluate_text(
    population: Sequence[SyntheticTextGeneration],
    artifacts: Sequence[TextArtifact],
    policy: TextEvidencePolicy,
    anonymity_band: float = .015,
) -> TextMetrics:
    assert_synthetic_text_only(population)
    if not artifacts:
        raise ValueError("No artifacts")
    by_gen = {r.generation_id: r for r in population}
    c_lex, c_sem, profiles = _candidate_features(population)
    normalized_policy = policy.normalized()
    gen1=gen5=acct1=person1=0
    ranks=[]
    sets=[]
    for artifact in artifacts:
        target = by_gen.get(artifact.target_generation_id)
        if target is None:
            raise ValueError("Artifact target outside population")
        a_lex = lexical_vector(artifact.text)
        a_sem = semantic_vector(artifact.text)
        a_style = style_vector(artifact.text)
        ranked = []
        for row in population:
            score = score_text_candidate(
                artifact,
                row,
                normalized_policy,
                profiles,
                artifact_lexical=a_lex,
                artifact_semantic=a_sem,
                artifact_style=a_style,
                candidate_lexical=c_lex[row.generation_id],
                candidate_semantic=c_sem[row.generation_id],
            )
            ranked.append((row, score))
        ranked.sort(key=lambda item: (-item[1], item[0].generation_id))
        pos = next(i for i,(r,_) in enumerate(ranked) if r.generation_id == target.generation_id)
        pred = ranked[0][0]
        gen1 += pos == 0
        gen5 += pos < 5
        acct1 += pred.account_id == target.account_id
        person1 += pred.person_id == target.person_id
        ranks.append(pos+1)
        best = ranked[0][1]
        sets.append(sum(1 for _,score in ranked if score >= best-anonymity_band))
    n=len(artifacts)
    return TextMetrics(n, gen1/n, gen5/n, acct1/n, person1/n, mean(ranks), mean(sets))


def strip_text_provenance(artifact: TextArtifact) -> TextArtifact:
    return replace(artifact, provider_hint=None, watermark_family=None)


def delay_text_publication(artifact: TextArtifact, minutes: int = 360) -> TextArtifact:
    if minutes < 0:
        raise ValueError("Delay must be non-negative")
    return replace(artifact, published_minute=artifact.published_minute+minutes)


def paraphrase_surface(text: str) -> str:
    """Deterministic lexical paraphrase over the controlled synthetic vocabulary."""
    out = text
    for source, target in sorted(PARAPHRASE_MAP.items(), key=lambda x: -len(x[0])):
        out = re.sub(rf"\b{re.escape(source)}\b", target, out, flags=re.I)
    return out


def normalize_text_style(text: str) -> str:
    """Remove synthetic author-preference markers and normalize punctuation/contractions."""
    out = text
    for phrase in sorted(set(TRANSITIONS + HEDGES + SIGNATURES), key=len, reverse=True):
        out = re.sub(rf"\b{re.escape(phrase)}\b[,]?\s*", "", out, flags=re.I)
    replacements = {
        "it's": "it is", "don't": "do not", "can't": "cannot",
        ";": ".", "—": ",", " - ": ", ", "!": ".", "?": ".",
    }
    for source,target in replacements.items():
        out = out.replace(source, target)
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"\.\s*,", ".", out)
    out = re.sub(r"\.{2,}", ".", out)
    sentences=[]
    for sent in SENTENCE_RE.split(out):
        words=sent.split()
        if len(words) > 22:
            cut=len(words)//2
            sentences.append(" ".join(words[:cut]).rstrip(",") + ".")
            sentences.append(" ".join(words[cut:]).lstrip(", ").rstrip(".") + ".")
        else:
            sentences.append(sent if sent.endswith(".") else sent+".")
    return " ".join(s[0].upper()+s[1:] if s else s for s in sentences)


def generalize_topic_terms(text: str, fraction: float = .55) -> str:
    """Replace a deterministic fraction of specific topic terms with generic concepts."""
    if not 0 <= fraction <= 1:
        raise ValueError("fraction must be [0,1]")
    tokens = text.split()
    eligible=[]
    for i, raw in enumerate(tokens):
        clean=re.sub(r"[^A-Za-z'-]", "", raw).lower()
        canonical=_canonical_concept(clean)
        if canonical in ALL_TOPIC_TERMS:
            eligible.append(i)
    count=int(round(len(eligible)*fraction))
    for offset,i in enumerate(eligible[:count]):
        punct="".join(ch for ch in tokens[i] if not ch.isalnum() and ch not in "'-")
        tokens[i]=GENERIC_WORDS[offset % len(GENERIC_WORDS)] + punct
    return " ".join(tokens)


def text_composite_transform(artifact: TextArtifact) -> TextArtifact:
    transformed=strip_text_provenance(artifact)
    transformed=delay_text_publication(transformed, 360)
    text=paraphrase_surface(transformed.text)
    text=normalize_text_style(text)
    text=generalize_topic_terms(text, .55)
    return replace(transformed, text=text)


def text_utility(original: TextArtifact, transformed: TextArtifact) -> TextUtility:
    s1=semantic_vector(original.text)
    s2=semantic_vector(transformed.text)
    topic_retention=(cosine(s1,s2)+1)/2
    a=set(_tokens(original.text))
    b=set(_tokens(transformed.text))
    content_a={x for x in a if len(x)>3}
    overlap=len(content_a & b)/max(1,len(content_a))
    length_ratio=min(len(_tokens(original.text)),len(_tokens(transformed.text)))/max(1,max(len(_tokens(original.text)),len(_tokens(transformed.text))))
    return TextUtility(topic_retention, overlap, length_ratio)


def correlation_gain(combined: TextMetrics, singles: Sequence[TextMetrics]) -> float:
    if not singles:
        raise ValueError("Need single-signal metrics")
    return combined.person_top1 - max(x.person_top1 for x in singles)


def run_text_reference_experiment(persons: int = 24, seed: int = 29) -> dict:
    population=generate_text_population(persons=persons, seed=seed)
    artifacts=make_text_artifacts(population)
    policy=TEXT_POLICIES[TextAdversary.COLLABORATING]
    baseline=evaluate_text(population, artifacts, policy)
    singles={
        "lexical": evaluate_text(population, artifacts, TextEvidencePolicy(lexical=1)),
        "semantic": evaluate_text(population, artifacts, TextEvidencePolicy(semantic=1)),
        "style": evaluate_text(population, artifacts, TextEvidencePolicy(style=1)),
        "watermark": evaluate_text(population, artifacts, TextEvidencePolicy(watermark=1)),
        "timing": evaluate_text(population, artifacts, TextEvidencePolicy(time=1)),
    }
    stripped=evaluate_text(population, [strip_text_provenance(a) for a in artifacts], policy)
    paraphrased=evaluate_text(population, [replace(a,text=paraphrase_surface(a.text)) for a in artifacts], policy)
    styled=evaluate_text(population, [replace(a,text=normalize_text_style(a.text)) for a in artifacts], policy)
    composite_artifacts=[text_composite_transform(a) for a in artifacts]
    composite=evaluate_text(population, composite_artifacts, policy)
    utilities=[text_utility(a,b) for a,b in zip(artifacts, composite_artifacts)]
    return {
        "version":"0.2",
        "research_scope":"synthetic-text-only",
        "population":{"persons":persons,"generations":len(population)},
        "baseline":asdict(baseline),
        "single_signal":{k:asdict(v) for k,v in singles.items()},
        "correlation_gain_person_top1":correlation_gain(baseline,list(singles.values())),
        "transformed":{
            "provenance_removed":asdict(stripped),
            "surface_paraphrase":asdict(paraphrased),
            "style_normalized":asdict(styled),
            "composite":asdict(composite),
        },
        "utility":{
            "mean_topic_retention":mean(x.topic_retention for x in utilities),
            "mean_content_word_retention":mean(x.content_word_retention for x in utilities),
            "mean_length_ratio":mean(x.length_ratio for x in utilities),
        },
        "limitations":[
            "All people, accounts, sessions and texts are synthetic.",
            "The watermark is an abstract provider/model label, not a detector for any deployed provider.",
            "Lexical, semantic and stylometric features are transparent baseline features, not state-of-the-art authorship attribution.",
            "A failed attribution attempt is evidence only for the declared synthetic experiment, not proof of anonymity.",
        ],
    }


def main() -> None:
    print(json.dumps(run_text_reference_experiment(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
