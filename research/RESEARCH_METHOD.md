# Research Method

**Status:** normative research-process guidance  
**Scope:** synthetic privacy, provenance, attribution, and unlinkability research  
**Effective date:** 2026-08-22

## Purpose

This repository does not treat the first hypothesis as the conclusion. The method is designed to expose assumptions, invite criticism, convert legitimate challenges into testable questions, and preserve negative or narrowing evidence instead of optimizing the narrative around a preferred result.

Working sequence:

`observation -> hypothesis -> adversarial challenge -> assumption isolation -> counter-model -> predeclared test -> execution -> adverse-result retention -> claim review -> lineage update`

External discussion, peer criticism, or architectural thought experiments can change the next research question, but are not empirical evidence by themselves.

## Method

1. **Observation.** Record what was directly observed and separate it from inference.
2. **Hypothesis.** State the narrowest testable proposition.
3. **Adversarial challenge.** Seek the strongest alternative explanation or objection. The goal is to find which assumption fails first, not defend the first wording.
4. **Assumption isolation.** Identify exactly what changed and which variable must be separated.
5. **Counter-model.** Construct at least one plausible competing explanation and, where possible, design a test that makes different predictions under each model.
6. **Rules before results.** Freeze population, evidence channels, transformations, calibration/holdout separation, metrics, failure gates, controls, claim boundaries, protocol lineage, and DDC audit before canonical execution.
7. **Execution.** Preserve exact lineage, deterministic controls, adverse cells, failed replication, and machine-readable evidence where practical.
8. **Claim review.** A result may support, narrow, falsify, or leave a claim context-dependent. It does not automatically become a universal invariant.
9. **External challenge log.** Record material public or peer challenges as hypothesis-generating criticism, including the assumption targeted and the research consequence. See `research/EXTERNAL_REVIEW_LOG.md`.

## Standing DDC distinctions

- **Need != Authority.**
- **Data != Authority.**
- **Detection != Provenance != Attribution != Identity Resolution != Authority.**
- **Watermark signal != attribution evidence.**
- **Candidate reduction != evidence creation.**
- **Confidence != identity proof.**
- **Correlation != authorization.**
- **Key secrecy != architectural secrecy.**
- **Detector behavior != internal watermark architecture.**
- **Provider assertion != independently verified privacy property.**
- **Failed re-identification != proven anonymity.**
- **Synthetic evidence != deployed-provider evidence.**
- **Experiment result != validated invariant.**
- **Provenance != authorship != ownership != responsibility.**

## Research boundary

The research remains synthetic-only unless a separately authorized future protocol explicitly changes scope. No current result authorizes work on real identities, private account data, provider secrets, or production credentials.

## Publication rule

Public summaries must preserve evidence maturity. A strong local result stays local if broader replication fails. A public debate that exposes a better question is credited as a change in research direction, not presented as proof of the resulting hypothesis.

The objective is not to make every iteration confirm the previous one. The objective is to make every iteration harder to fool.
