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

## Publication files

- [`paper.md`](paper.md) - full research note
- [`CITATION.cff`](CITATION.cff) - machine-readable citation metadata

## Suggested citation

Rukhaylo, Valentyn. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

## Research provenance

The central system-level research question - whether non-identifying model provenance can become human attribution through correlation with generation and identity records - was formulated by **Valentyn Rukhaylo of Altru.dev on August 18, 2026**.

Research assistance was provided using ChatGPT for literature discovery, source comparison, technical synthesis, and drafting. The publication distinguishes documented facts from derived architectural implications and hypotheses.

## Keywords

AI text watermarking · AI provenance · Claude watermark · Anthropic · AI privacy · privacy engineering · model attribution · user attribution · human attribution · compositional privacy · provenance-mediated identity linkage · generative AI governance · AI accountability · digital privacy
