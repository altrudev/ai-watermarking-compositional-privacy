from __future__ import annotations

from dataclasses import dataclass, replace
from math import sqrt
from random import Random
from statistics import mean
from typing import Optional, Sequence
import hashlib
import re


@dataclass(frozen=True)
class SyntheticAuthor:
    person_id: str
    signature_words: tuple[str, ...]
    phrase_habit: str
    punctuation_habit: str
    sentence_bias: int
    topic_bias: int


@dataclass(frozen=True)
class TextGeneration:
    person_id: str
    account_id: str
    session_id: str
    generation_id: str
    provider: str
    model: str
    created_minute: int
    watermark_family: str
    text: str


@dataclass(frozen=True)
class TextArtifact:
    target_generation_id: str
    published_minute: int
    provider_hint: Optional[str]
    watermark_family: Optional[str]
    text: str


@dataclass(frozen=True)
class Utility:
    semantic_retention: float
    content_retention: float


TOPICS: tuple[tuple[str, ...], ...] = (
    ("river", "water", "shore", "current", "harbor", "tide", "bridge", "island"),
    ("forest", "tree", "moss", "trail", "cedar", "rain", "canopy", "valley"),
    ("market", "price", "trade", "buyer", "seller", "demand", "supply", "contract"),
    ("system", "state", "transition", "evidence", "authority", "policy", "runtime", "memory"),
    ("music", "rhythm", "sound", "frequency", "voice", "tone", "pattern", "signal"),
    ("city", "street", "building", "transit", "district", "public", "route", "station"),
)

NEUTRAL_SYNONYMS = {
    "river": "waterway", "shore": "edge", "current": "flow", "harbor": "port", "tide": "cycle",
    "forest": "woodland", "tree": "plant", "moss": "groundcover", "trail": "path", "cedar": "evergreen",
    "market": "exchange", "price": "cost", "trade": "transaction", "buyer": "customer", "seller": "vendor",
    "system": "environment", "state": "condition", "transition": "change", "evidence": "record", "authority": "permission",
    "music": "audio", "rhythm": "cadence", "sound": "audio", "frequency": "rate", "voice": "speaker",
    "city": "urban area", "street": "road", "building": "structure", "transit": "transport", "district": "area",
}

COMMON_WORDS = (
    "clear", "steady", "useful", "careful", "direct", "measured", "practical", "visible",
    "change", "result", "context", "process", "question", "example", "detail", "reason",
)

PHRASES = (
    "in practical terms", "from another angle", "the important point is", "in this case",
    "what matters here is", "as a working rule", "in the larger picture", "at the same time",
)

PUNCT = (",", ";", "—", ":")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9']*")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


def stable_int(value: str) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big")


def tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vector lengths differ")
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def topic_vector(text: str) -> tuple[float, ...]:
    words = tokens(text)
    counts = []
    for topic in TOPICS:
        topic_set = set(topic) | {NEUTRAL_SYNONYMS.get(word, word) for word in topic}
        counts.append(sum(1 for token in words if token in topic_set))
    return tuple(float(x) for x in counts)


def style_vector(text: str) -> tuple[float, ...]:
    words = tokens(text)
    sentences = [s.strip() for s in SENTENCE_RE.findall(text) if s.strip()]
    wc = max(1, len(words))
    sc = max(1, len(sentences))
    lengths = [len(tokens(s)) for s in sentences]
    return (
        mean(lengths) / 30.0 if lengths else 0.0,
        text.count(",") / wc, text.count(";") / wc, text.count("—") / wc, text.count(":") / wc,
        text.count("!") / sc, text.count("?") / sc,
        len(set(words)) / wc,
        sum(1 for phrase in PHRASES if phrase in text.lower()) / len(PHRASES),
    )


def lexical_vector(text: str, vocabulary: Sequence[str]) -> tuple[float, ...]:
    words = tokens(text)
    wc = max(1, len(words))
    counts = {word: 0 for word in vocabulary}
    for word in words:
        if word in counts:
            counts[word] += 1
    return tuple(counts[word] / wc for word in vocabulary)


def content_signature(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "is", "it", "this", "that", "with", "for", "as"}
    return {word for word in tokens(text) if word not in stop and len(word) > 3}


def generate_authors(persons: int = 36, seed: int = 73) -> list[SyntheticAuthor]:
    if persons <= 1:
        raise ValueError("Need at least two synthetic authors")
    rng = Random(seed)
    pool = [f"sig{idx:02d}" for idx in range(6)]
    authors = []
    for i in range(persons):
        authors.append(SyntheticAuthor(
            person_id=f"syn-person-{i:04d}",
            signature_words=(pool[i % len(pool)],),
            phrase_habit=PHRASES[i % 2],
            punctuation_habit=PUNCT[i % 2],
            sentence_bias=10 + (i % 2),
            topic_bias=i % len(TOPICS),
        ))
    rng.shuffle(authors)
    return sorted(authors, key=lambda author: author.person_id)


def _sentence(author: SyntheticAuthor, topic: Sequence[str], rng: Random, sentence_index: int) -> str:
    length = author.sentence_bias + rng.randint(-2, 3)
    words: list[str] = []
    if sentence_index % 2 == 0:
        words.extend(author.phrase_habit.split())
    while len(words) < max(6, length):
        roll = rng.random()
        if roll < 0.42:
            words.append(topic[rng.randrange(len(topic))])
        elif roll < 0.62:
            words.append(author.signature_words[0])
        else:
            words.append(COMMON_WORDS[rng.randrange(len(COMMON_WORDS))])
    punct_at = max(3, min(len(words) - 2, len(words) // 2))
    words[punct_at] += author.punctuation_habit
    sentence = " ".join(words)
    return sentence[0].upper() + sentence[1:] + "."


def generate_text_population(persons: int = 36, accounts_per_person: int = 2, sessions_per_account: int = 2,
                             generations_per_session: int = 2, seed: int = 73) -> list[TextGeneration]:
    if min(persons, accounts_per_person, sessions_per_account, generations_per_session) <= 0:
        raise ValueError("Population dimensions must be positive")
    authors = {author.person_id: author for author in generate_authors(persons, seed)}
    providers = ("provider-a", "provider-b", "provider-c")
    models = ("model-1", "model-2")
    rows: list[TextGeneration] = []
    for person_index in range(persons):
        person_id = f"syn-person-{person_index:04d}"
        author = authors[person_id]
        for account_index in range(accounts_per_person):
            account_id = f"{person_id}-acct-{account_index}"
            provider = providers[(person_index + account_index) % len(providers)]
            model = models[(person_index + account_index) % len(models)]
            family = f"{provider}:{model}"
            for session_index in range(sessions_per_account):
                session_id = f"{account_id}-sess-{session_index}"
                topic = TOPICS[(author.topic_bias + account_index + session_index) % len(TOPICS)]
                for generation_index in range(generations_per_session):
                    generation_id = f"{session_id}-gen-{generation_index}"
                    rng = Random(seed + stable_int(generation_id) % 10_000_000)
                    text = " ".join(_sentence(author, topic, rng, j) for j in range(4 + generation_index))
                    created_minute = 100_000 + (person_index * 13 + account_index * 19 + session_index * 29 + generation_index * 7) % 360
                    rows.append(TextGeneration(person_id, account_id, session_id, generation_id, provider, model,
                                               created_minute, family, text))
    assert_synthetic_only(rows)
    return rows


def assert_synthetic_only(population: Sequence[TextGeneration]) -> None:
    if not population:
        raise ValueError("Population is empty")
    for row in population:
        ids = (row.person_id, row.account_id, row.session_id, row.generation_id)
        if not all(value.startswith("syn-") for value in ids):
            raise ValueError("v0.2 accepts synthetic identities only")


def make_artifacts(population: Sequence[TextGeneration], seed: int = 9001) -> list[TextArtifact]:
    assert_synthetic_only(population)
    artifacts = []
    for index, row in enumerate(population):
        rng = Random(seed + index)
        sentences = [s.strip() for s in SENTENCE_RE.findall(row.text) if s.strip()]
        if len(sentences) > 4 and rng.random() < 0.35:
            sentences = sentences[:-1]
        artifacts.append(TextArtifact(row.generation_id, row.created_minute + rng.randint(2, 40), row.provider,
                                      row.watermark_family, " ".join(sentences)))
    return artifacts


def lexical_normalize(text: str, strength: float = 1.0, salt: str = "lex") -> str:
    replacements = {f"sig{idx:02d}": COMMON_WORDS[idx % len(COMMON_WORDS)] for idx in range(200)}
    raw = re.findall(r"[A-Za-z][A-Za-z0-9']*|[^A-Za-z0-9']+", text)
    word_index = 0
    out = []
    for part in raw:
        if TOKEN_RE.fullmatch(part):
            lower = part.lower()
            if lower in replacements:
                threshold = (stable_int(f"{salt}:{word_index}:{lower}") % 10_000) / 10_000.0
                if threshold < strength:
                    repl = replacements[lower]
                    part = repl.capitalize() if part[:1].isupper() else repl
            word_index += 1
        out.append(part)
    return "".join(out)


def style_normalize(text: str, strength: float = 1.0) -> str:
    if strength <= 0:
        return text
    normalized = text
    if strength >= 0.25:
        normalized = normalized.replace(";", ",").replace("—", ",").replace(":", ",")
    if strength >= 0.50:
        for phrase in PHRASES:
            normalized = re.sub(rf"\b{re.escape(phrase)}\b\s*,?\s*", "", normalized, flags=re.I)
    if strength >= 0.75:
        sentences = [s.strip() for s in SENTENCE_RE.findall(normalized) if s.strip()]
        rebuilt = []
        for sentence in sentences:
            words = tokens(sentence)
            rebuilt.extend(" ".join(chunk).capitalize() + "." for chunk in
                           [words[i:i + 12] for i in range(0, len(words), 12)] if chunk)
        normalized = " ".join(rebuilt)
    return re.sub(r"\s+", " ", normalized).strip()


def semantic_generalize(text: str, strength: float = 1.0, salt: str = "sem") -> str:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9']*|[^A-Za-z0-9']+", text)
    word_index = 0
    out = []
    for part in raw:
        if TOKEN_RE.fullmatch(part):
            lower = part.lower()
            if lower in NEUTRAL_SYNONYMS:
                threshold = (stable_int(f"{salt}:{word_index}:{lower}") % 10_000) / 10_000.0
                if threshold < strength:
                    repl = NEUTRAL_SYNONYMS[lower]
                    part = repl.capitalize() if part[:1].isupper() else repl
            word_index += 1
        out.append(part)
    return "".join(out)


def transform_artifact(artifact: TextArtifact, strength: float = 1.0) -> TextArtifact:
    if not 0.0 <= strength <= 1.0:
        raise ValueError("strength must be in [0, 1]")
    marker, provider, published = artifact.watermark_family, artifact.provider_hint, artifact.published_minute
    text = artifact.text
    if strength > 0:
        marker = None
        provider = None
        published += round(360 * strength)
    text = lexical_normalize(text, strength, artifact.target_generation_id)
    text = style_normalize(text, strength)
    text = semantic_generalize(text, min(0.70, strength * 0.70), artifact.target_generation_id)
    return replace(artifact, text=text, watermark_family=marker, provider_hint=provider, published_minute=published)


def utility(original: TextArtifact, transformed: TextArtifact) -> Utility:
    semantic = min(1.0, max(0.0, cosine(topic_vector(original.text), topic_vector(transformed.text))))
    before, after = content_signature(original.text), content_signature(transformed.text)
    union = before | after
    content = len(before & after) / len(union) if union else 1.0
    return Utility(semantic, content)
