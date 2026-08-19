# From Model Provenance to Human Attribution

## The Compositional Privacy Risk of AI Text Watermarking

**Technical Research Note / Privacy Threat Analysis**  
**Author:** Valentyn Rukhaylo · Altru.dev  
**Date:** August 18, 2026  
**Version:** 1.0  
**Repository:** https://github.com/altrudev/ai-watermarking-compositional-privacy

> **Central proposition:** A provenance signal may contain no identifying information and still participate in an identifying system.

## Abstract

AI text watermarking is increasingly being deployed as infrastructure for determining whether a generative model participated in producing a piece of text. Anthropic's recently announced Claude text watermark illustrates the intended model: the watermark is imperceptible to readers, provides evidence that Claude was involved in producing or processing text, and - according to Anthropic - carries no information identifying a particular user, organization, or conversation.

This research note argues that the privacy question cannot end there.

A provenance signal does not need to **contain** personal identity to participate in a system capable of establishing personal identity. If a watermarked public artifact can be associated with a provider, and the provider separately retains generation outputs, request records, timestamps, sessions, account relationships, or other operational metadata, the artifact may in principle become linkable to a particular generation event and, from there, to an account or person.

The paper introduces **provenance-mediated identity linkage** as a privacy threat-model category and proposes a **Compositional Privacy Invariant** for AI provenance systems.

## Core distinctions

- **Embedded Identity ≠ Linkability ≠ Attribution**
- **Model Attribution ≠ User Attribution**
- **Artifact Identifier ≠ Human Identifier**
- **Detection ≠ Identity Resolution**
- **Component Privacy ≠ Compositional Privacy**
- **Correlation ≠ Authorization**

## Proposed Compositional Privacy Invariant

> Information classified as non-identifying in isolation must not be assumed non-identifying after correlation with provenance signals, generation records, content fingerprints, semantic representations, timestamps, account metadata, platform records, network observations, or other auxiliary datasets.

For AI provenance specifically:

> A transition from model or artifact provenance to generation-event, session, account, organization, or human attribution should be treated as a separate identity-disclosure operation requiring an independent purpose, authority basis, access decision, evidence record, and audit trail.

## Unlinkability Lab v0.1

The original inverse experiment uses abstract semantic/style vectors and synthetic-only identities. It remains frozen as the v0.1 baseline.

Reference v0.1:

- combined baseline person attribution: **82.08%**
- after removing only the simulated provenance marker: **56.88%**
- after the composite privacy transformation: **5.42%**
- measured correlation gain over the strongest single signal: **47.91 percentage points**

Research files:

- [`lab/unlinkability_lab.py`](lab/unlinkability_lab.py)
- [`tests/test_unlinkability_lab.py`](tests/test_unlinkability_lab.py)
- [`research/TEST_PLAN.md`](research/TEST_PLAN.md)
- [`research/CLAIM_REGISTER.md`](research/CLAIM_REGISTER.md)
- [`research/RESULTS-v0.1.md`](research/RESULTS-v0.1.md)
- [`research/reference-report-v0.1.json`](research/reference-report-v0.1.json)

## Textual Compositional Privacy Benchmark v0.2

v0.2 moves the experiment to **actual generated synthetic text**. Semantic, lexical, and stylometric evidence is derived from the text itself, then combined with an abstract provenance signal, provider hint, and timing evidence.

The reference run contains **36 synthetic people and 288 synthetic text generations**.

- strongest single signal: **56.60%** person top-1
- combined provider + publisher evidence: **74.65%** person top-1
- measured compositional correlation gain: **18.06 percentage points**
- after removing provenance/provider only: **71.88%** person top-1
- after full composite transformation under an adaptive attack: **6.77%** person top-1
- full-transform benchmark semantic retention: **100.00%**
- full-transform exact-content retention: **61.18%**

The adaptive attack calibrates on one partition of transformed artifacts and evaluates on another, so the privacy result is not merely failure of the original fixed evidence weighting.

The benchmark preserves the standing rules:

> **Privacy transformation ≠ privacy evidence.**

> **Fixed-attack failure ≠ adaptive-attack failure.**

> **Failed re-identification ≠ proven anonymity.**

v0.2 files:

- [`lab/textual_model.py`](lab/textual_model.py) — deterministic synthetic text population and transformations
- [`lab/textual_attack.py`](lab/textual_attack.py) — adversary, attribution, and adaptive attack logic
- [`lab/textual_benchmark.py`](lab/textual_benchmark.py) — reference benchmark/report runner
- [`tests/test_textual_benchmark.py`](tests/test_textual_benchmark.py) — v0.2 adversarial regression suite
- [`research/TEST_PLAN-v0.2.md`](research/TEST_PLAN-v0.2.md) — DDC-governed textual benchmark protocol
- [`research/CLAIM_REGISTER-v0.2.md`](research/CLAIM_REGISTER-v0.2.md) — claim maturity and explicit non-claims
- [`research/RESULTS-v0.2.md`](research/RESULTS-v0.2.md) — human-readable reference results
- [`research/reference-report-v0.2.json`](research/reference-report-v0.2.json) — machine-readable experiment record

Run locally with standard Python only:

```bash
python -m unittest discover -s tests -v
python -m lab.textual_benchmark
```

Both v0.1 and v0.2 are synthetic research apparatus. They do not ingest real people, real accounts, provider logs, scraped social profiles, or private identity datasets. The simulated provenance signal is not an implementation or emulation of Claude, SynthID, OpenAI, Gemini, or another deployed watermark.

## Publication files

- [`paper.md`](paper.md) - full published v1.0 research note
- [`CITATION.cff`](CITATION.cff) - machine-readable citation metadata

The published paper and the active research program are related but not identical: the paper is the immutable v1.0 publication, while this repository contains evolving experiments and evidence that must be cited by exact version/commit when used downstream.

## Suggested citation

Rukhaylo, Valentyn. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

## Research provenance

The central system-level research question - whether non-identifying model provenance can become human attribution through correlation with generation and identity records - was formulated by **Valentyn Rukhaylo of Altru.dev on August 18, 2026**.

Research assistance was provided using ChatGPT for literature discovery, source comparison, technical synthesis, drafting, and implementation of the synthetic unlinkability benchmarks. The publication and lab distinguish documented facts from derived architectural implications, experimental results, hypotheses, and explicit non-claims.

## Keywords

AI text watermarking · AI provenance · Claude watermark · Anthropic · AI privacy · privacy engineering · model attribution · user attribution · human attribution · compositional privacy · provenance-mediated identity linkage · unlinkability · re-identification testing · generative AI governance · AI accountability · digital privacy
