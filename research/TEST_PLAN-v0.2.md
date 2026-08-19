# Text Unlinkability Lab v0.2 — Test Plan

**Status:** Experimental synthetic-text benchmark  
**Scope:** Synthetic identities, synthetic text, and abstract provenance signals only  
**Purpose:** Replace v0.1's abstract semantic/style vectors with actual generated text and measurable text-derived linkage features.

## Research question

How much identity linkage remains when attribution is performed over actual text-derived signals, and which combinations of privacy transformations are required before attribution materially collapses?

The experiment tests the inverse of the original provenance-mediated identity-linkage problem:

`known synthetic origin → published artifact → attribution → privacy transform → re-attribution`

## DDC-governed scope

### Authority
This experiment is authorized only for synthetic identities created by the harness.

### Inputs
Allowed:
- locally generated synthetic person/account/session/generation identifiers;
- locally generated synthetic text;
- simulated provider/model provenance labels;
- deterministic timestamps.

Not allowed:
- real names or real account identifiers;
- scraped social profiles;
- real provider logs;
- real private conversations;
- imported user identity datasets;
- external identity-resolution services.

### Transition under test
A synthetic artifact is transformed to reduce one or more linkage channels and then subjected to the same attribution procedure again.

### Verification
A privacy transformation is not accepted as evidence of unlinkability by itself. Verification requires post-transformation re-attribution and measured residual linkage.

### Claim boundary
The harness may report measured attribution rates for the declared experiment. It must not report universal claims such as `ANONYMOUS`, `UNTRACEABLE`, or `SAFE`.

Standing rules:

> **Privacy transformation ≠ privacy evidence**

> **Failed re-identification ≠ proven anonymity**

## Text-derived linkage channels

v0.2 derives its signals from actual synthetic text:

1. **Lexical surface features** — hashed bag-of-word representation after boilerplate/style-token filtering.
2. **Semantic topic features** — synonym-normalized counts over controlled topic concepts.
3. **Stylometric features** — 16 measurable features including sentence length, lexical diversity, punctuation, first-person frequency, hedge/transition/signature usage, contractions, and paragraphing.
4. **Simulated provenance** — abstract provider/model watermark family.
5. **Provider hint** — simulated provider identity.
6. **Timing** — generation-to-publication temporal proximity.

No proprietary watermark detector is implemented or emulated.

## Population

Reference configuration:

- 24 synthetic persons
- 2 accounts per person
- 3 sessions per account
- 2 generations per session
- 288 generation events

Every identity-bearing identifier uses the `syn-` namespace.

## Publication derivative

The public artifact is deliberately not byte-identical to the synthetic provider output. Topic terms are deterministically paraphrased before publication so exact surface equality cannot trivially dominate the experiment.

This is important because the research question concerns correlation across multiple weak signals rather than exact-file lookup.

## Attribution tests

The suite measures:

- generation top-1 attribution;
- generation top-5 attribution;
- account top-1 attribution;
- person top-1 attribution;
- mean generation rank;
- mean near-best anonymity set.

Single-signal runs are compared with the combined provider-plus-publisher adversary to measure correlation gain.

## Privacy transformations

v0.2 tests provenance removal, publication delay, surface paraphrase, style normalization, topic generalization, and a composite transform combining all of them.

## Utility measurements

The composite transform is evaluated for topic/semantic retention, content-word retention, and text-length retention. Utility is measured rather than assumed.

## Required regression gates

1. deterministic synthetic population;
2. synthetic-only identity enforcement;
3. actual text generation;
4. text-derived feature extraction;
5. combined evidence materially stronger than any individual channel;
6. provenance removal does not equal unlinkability;
7. paraphrase changes lexical representation while preserving semantic representation;
8. style normalization changes measurable style;
9. timing remains a distinct channel;
10. composite transform lowers attribution;
11. utility remains bounded and measured;
12. no real-identity loader/network identity path is introduced.

## Reproduction

```bash
python -m py_compile lab/text_unlinkability_lab.py tests/test_text_unlinkability_lab.py
python -m unittest discover -s tests -v
python -m lab.text_unlinkability_lab
```

A change to population size, seed, feature extraction, scoring policy, adversary evidence, or transformation strength constitutes a new experiment and must receive a separately identified result record.
