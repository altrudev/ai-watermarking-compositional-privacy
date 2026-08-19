# Reference Results v0.2 — Actual Synthetic Text

**Status:** Experimental synthetic-text benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, generated synthetic text, and abstract provenance signals only

## What changed from v0.1

v0.1 established the architecture using abstract semantic and style vectors.

v0.2 replaces those abstractions with actual generated text and derives lexical, semantic, and stylometric features from the text itself. The public artifact is also an edited derivative rather than a byte-identical copy of the synthetic generation.

## Reference population

- synthetic persons: **24**
- synthetic generation events: **288**
- accounts per person: 2
- sessions per account: 3
- generations per session: 2

## Headline result

Under the combined provider-plus-publisher evidence policy:

| Condition | Person top-1 | Generation top-1 | Generation top-5 |
|---|---:|---:|---:|
| Combined baseline | **81.94%** | **44.44%** | **99.31%** |
| Provenance removed only | **28.47%** | **12.15%** | **51.39%** |
| Composite transform | **3.12%** | **0.69%** | **6.60%** |

The strongest individual person-attribution signal reached only **20.83%**, while the combined system reached **81.94%**.

Measured correlation gain:

```text
81.94% - 20.83% = 61.11 percentage points
```

Within this synthetic-text model, that is a direct empirical demonstration of:

> **Component Privacy ≠ Compositional Privacy**

## Individual linkage channels

| Signal | Person top-1 | Generation top-1 |
|---|---:|---:|
| Lexical surface | 4.86% | 1.04% |
| Semantic topic | **20.83%** | 17.71% |
| Stylometry | 18.06% | 2.43% |
| Simulated watermark | 12.50% | 2.08% |
| Timing | 13.89% | 1.39% |

None of these channels individually approaches the combined attribution rate.

## Watermark/provenance removal is still not unlinkability

Removing only the simulated provenance marker and provider hint reduces person attribution from **81.94%** to **28.47%**.

That is a substantial reduction, but attribution remains far above the 1-in-24 random person baseline of approximately **4.17%**.

So v0.2 independently reproduces the core v0.1 result using actual synthetic text:

> **Watermark removal ≠ unlinkability**

## Composite transformation

The v0.2 composite transform performs:

1. simulated provenance removal;
2. six-hour publication delay;
3. controlled lexical paraphrase;
4. measurable style normalization;
5. bounded topic-term generalization.

After the composite transform:

- person top-1: **3.12%**
- generation top-1: **0.69%**
- generation top-5: **6.60%**
- mean near-best anonymity set: **31.48 candidates**
- mean generation rank: **34.72**

This does not prove anonymity. It shows that the declared attribution procedure collapsed close to or below the random person baseline for this synthetic experiment.

## Utility cost

The composite transformation retained:

- mean topic/semantic retention: **84.04%**
- mean content-word retention: **85.51%**
- mean text-length retention: **91.19%**

These are internal synthetic utility measures, not human quality judgments.

## Important negative result

Style normalization by itself did not materially reduce combined attribution in the reference run.

That is useful evidence: a transformation may successfully change one measurable channel while producing almost no system-level privacy improvement because other channels still dominate.

Likewise, a second surface paraphrase over an already paraphrased publication derivative produced no material combined-attribution improvement.

This is precisely why transformations must be tested against the complete linkage composition rather than evaluated in isolation.

## Interpretation boundary

These results establish behavior only inside this controlled synthetic-text benchmark.

They do **not** establish the behavior of Anthropic, Claude, SynthID, OpenAI, Gemini, LinkedIn, or any deployed provider/platform.

The simulated watermark is an abstract provider/model provenance label. The attribution features are transparent research baselines, not state-of-the-art deanonymization methods.

## Validation

v0.2 exact-source validation:

```text
py_compile: PASS
text unlinkability tests: 12/12 PASS
deterministic 288-generation reference run: PASS
```

v0.2 does not modify the v0.1 experiment files, so the original experiment remains independently reproducible.

## Next experiment

v0.3 should add controlled transformation chains and attribution persistence:

`original → edit → paraphrase → summarize → translate → model-edit → multi-model-edit`

The goal is to measure whether identity actually disappears, merely changes channels, or reappears after several transformations.
