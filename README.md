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

The repository now includes the inverse experiment: instead of stopping after identifying possible linkage channels, the lab attempts to break those channels and then attacks its own privacy transformations with re-identification tests.

**v0.1 is synthetic-only.** It does not ingest real people, real accounts, provider logs, scraped social profiles, or private identity datasets. The simulated watermark is an abstract provider/model signal, not an implementation or emulation of Claude, SynthID, OpenAI, Gemini, or another deployed watermark.

The reference synthetic run contains 480 generation events. Under the strongest declared provider-plus-publisher evidence policy:

- combined baseline person attribution: **82.08%**
- after removing only the simulated provenance marker: **56.88%**
- after the composite privacy transformation: **5.42%**
- measured correlation gain over the strongest single signal: **47.91 percentage points**

These results demonstrate behavior inside the controlled synthetic model; they are not claims about a deployed provider.

The lab enforces two standing rules:

> **Privacy transformation ≠ privacy evidence.**

> **Failed re-identification ≠ proven anonymity.**

Run locally with standard Python only:

```bash
python -m unittest discover -s tests -v
python -m lab.unlinkability_lab
```

Research files:

- [`lab/unlinkability_lab.py`](lab/unlinkability_lab.py) - deterministic attribution/unlinkability harness
- [`tests/test_unlinkability_lab.py`](tests/test_unlinkability_lab.py) - adversarial regression suite
- [`research/TEST_PLAN.md`](research/TEST_PLAN.md) - DDC-governed test plan and threat model
- [`research/CLAIM_REGISTER.md`](research/CLAIM_REGISTER.md) - claim maturity and explicit non-claims
- [`research/RESULTS-v0.1.md`](research/RESULTS-v0.1.md) - human-readable reference results
- [`research/reference-report-v0.1.json`](research/reference-report-v0.1.json) - machine-readable experiment record

## Publication files

- [`paper.md`](paper.md) - full research note
- [`CITATION.cff`](CITATION.cff) - machine-readable citation metadata

## Suggested citation

Rukhaylo, Valentyn. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

## Research provenance

The central system-level research question - whether non-identifying model provenance can become human attribution through correlation with generation and identity records - was formulated by **Valentyn Rukhaylo of Altru.dev on August 18, 2026**.

Research assistance was provided using ChatGPT for literature discovery, source comparison, technical synthesis, drafting, and implementation of the synthetic unlinkability test harness. The publication and lab distinguish documented facts from derived architectural implications, experimental results, hypotheses, and explicit non-claims.

## Keywords

AI text watermarking · AI provenance · Claude watermark · Anthropic · AI privacy · privacy engineering · model attribution · user attribution · human attribution · compositional privacy · provenance-mediated identity linkage · unlinkability · re-identification testing · generative AI governance · AI accountability · digital privacy
