# From Model Provenance to Human Attribution

## The Compositional Privacy Risk of AI Text Watermarking

**Technical Research Note / Privacy Threat Analysis**  
**Author:** Valentyn Rukhaylo · Altru.dev  
**Original publication:** August 18, 2026  
**Original paper version:** 1.0  
**Repository:** https://github.com/altrudev/ai-watermarking-compositional-privacy

> **Central proposition:** A provenance signal may contain no identifying information and still participate in an identifying system.

## Current repository research state

**Completed experimental lineage:** v0.1 through v0.7  
**Current governed program:** v0.8 open-set / false-attribution study  
**v0.8 status:** protocol audited; implementation authorized; canonical reference run **not yet authorized**  
**Next candidate direction:** v0.9 attribution-boundary / key-architecture study, recorded as a candidate only and **not implementation-authorized**

The public README previously stopped at v0.5 even though the repository had progressed through v0.7 results and a fully audited v0.8 pre-execution protocol. This README now reflects the actual governed state without rewriting historical result files.

## Abstract

AI text watermarking is increasingly being deployed as infrastructure for determining whether a generative model participated in producing a piece of text. Anthropic's announced Claude text watermark illustrates the intended model: the watermark is imperceptible to readers, provides evidence that Claude was involved in producing or processing text, and - according to Anthropic - carries no information identifying a particular user, organization, or conversation.

This research asks a different system-level question.

A provenance signal does not need to **contain** personal identity to participate in a system capable of establishing personal identity. If a public artifact can be associated with a provider or model family, and other evidence exists separately, the artifact may become more linkable when those signals are composed.

The paper introduces **provenance-mediated identity linkage** as a privacy threat-model category and proposes a **Compositional Privacy Invariant** for AI provenance systems.

The repository then attacks its own proposition through synthetic attribution/unlinkability experiments, transformation-chain tests, path-dependence analysis, robustness tests, mechanism analysis, replication/falsification, and an open-set false-attribution program.

## Core distinctions

- **Embedded Identity != Linkability != Attribution**
- **Model Attribution != User Attribution**
- **Artifact Identifier != Human Identifier**
- **Detection != Provenance != Attribution != Identity Resolution != Authority**
- **Component Privacy != Compositional Privacy**
- **Watermark signal != attribution evidence**
- **Candidate reduction != evidence creation**
- **Key secrecy != architectural secrecy**
- **Detector behavior != internal watermark architecture**
- **Provider assertion != independently verified privacy property**
- **Correlation != Authorization**
- **Provenance != Authorship != Ownership != Responsibility**

## Proposed Compositional Privacy Invariant

> Information classified as non-identifying in isolation must not be assumed non-identifying after correlation with provenance signals, generation records, content fingerprints, semantic representations, timestamps, account metadata, platform records, network observations, or other auxiliary datasets.

For AI provenance specifically:

> A transition from model or artifact provenance to generation-event, session, account, organization, or human attribution should be treated as a separate identity-disclosure operation requiring an independent purpose, authority basis, access decision, evidence record, and audit trail.

## Research method

The repository now documents the method explicitly in [`research/RESEARCH_METHOD.md`](research/RESEARCH_METHOD.md).

The working sequence is:

`observation -> hypothesis -> adversarial challenge -> assumption isolation -> counter-model -> predeclared test -> execution -> adverse-result retention -> claim review -> lineage update`

External criticism is treated as hypothesis-generating input, not experimental evidence. Material challenges and their research consequences are recorded in [`research/EXTERNAL_REVIEW_LOG.md`](research/EXTERNAL_REVIEW_LOG.md).

## Unlinkability Lab v0.1

The first inverse experiment attempted to break linkage channels and then attacked its own privacy transformations with re-identification tests.

**Synthetic-only.** No real people, real accounts, provider logs, scraped social profiles, or private identity datasets are used. The simulated watermark is an abstract provider/model signal, not an implementation or emulation of a deployed watermark.

Reference synthetic run: 480 generation events.

- combined baseline person attribution: **82.08%**
- after removing only the simulated provenance marker: **56.88%**
- after the composite privacy transformation: **5.42%**
- measured correlation gain over the strongest single signal: **47.91 percentage points**

These results describe the controlled synthetic model only.

## Unlinkability Lab v0.2 — actual synthetic text

v0.2 replaced abstract semantic/style vectors with actual generated synthetic text and derived linkage evidence from lexical, semantic, and stylometric features.

Reference population: **24 synthetic persons / 288 generation events**.

| Condition | Person top-1 | Generation top-1 |
|---|---:|---:|
| Combined evidence | **81.94%** | **44.44%** |
| Provenance removed only | **28.47%** | **12.15%** |
| Composite privacy transform | **3.12%** | **0.69%** |

The strongest individual person-attribution signal was **20.83%**. Combining the declared signals increased attribution to **81.94%**, a **61.11 percentage-point** synthetic correlation gain.

The composite transform retained approximately **84.04% topic/semantic utility**, **85.51% content-word retention**, and **91.19% text-length retention** under the lab's internal measures.

A negative result also appeared: changing stylometry alone did not materially improve system-level privacy because other linkage channels continued to dominate.

## Unlinkability Lab v0.3 — transformation-chain persistence

v0.3 tested:

`original -> edit -> paraphrase -> summarize -> translate -> model edit -> multi-model edit`

Reference population: **12 synthetic persons / 144 generation events**. Random person attribution: **8.33%**.

| Stage | Person top-1 |
|---|---:|
| Original publication derivative | **98.61%** |
| Edit | **98.61%** |
| Paraphrase + provenance removal | **34.03%** |
| Summarize | **9.03%** |
| Translate proxy | **18.06%** |
| Model-edit proxy | **27.08%** |
| Multi-model-edit proxy | **25.69%** |

Privacy improvement was **not monotonic**. Attribution fell close to random and then rose again during later transformations.

> **Intermediate unlinkability != end-to-end unlinkability.**

> **Final artifact state != complete privacy lineage.**

## Unlinkability Lab v0.4 — transformation path dependence

v0.4 held the transformation set constant and evaluated all **24 permutations** of:

`paraphrase + summarize + translate + model edit`

Person attribution ranged from **25.69% to 44.44%**, an **18.75 percentage-point** spread against an 8.33% random baseline.

The strongest pairwise ordering effect involved summarization and model editing: paths with summarization before model editing averaged **26.39%** person attribution, while the reverse order averaged **40.97%**.

> **Transformation Set != Transformation History != Privacy Outcome.**

## Unlinkability Lab v0.5 — robustness of path dependence

v0.5 perturbed population size, random seed, source-text length, transformation strength, stochastic behavior, and attribution-policy weights, and added a commuting-order negative control.

Across the **13-scenario** robustness matrix, path dependence remained material in **12/13 scenarios (92.31%)**. The half-strength transform condition was the declared non-material boundary case.

The commuting control produced identical final text and metadata in both orders.

> **Single Benchmark Result != Robust System Property.**

## Unlinkability Lab v0.6 — pairwise non-commutativity mechanism

v0.6 isolated pairwise ordering effects and tested whether they predicted complete-path attribution variation.

Reference result:

- canonical scorer parity: **PASS**
- commuting negative control: **PASS**
- pairwise full-path predictor Pearson correlation: **0.928292107191**
- predeclared `r >= 0.70` gate: **PASS**
- classification: **`PAIRWISE_MECHANISM_PREDICTIVE_FOR_DECLARED_TEST`**

The dominant local interaction was `summarize -> model_edit` versus `model_edit -> summarize`, with a **23.61 percentage-point** person-attribution difference.

The result remained explicitly local to the declared synthetic benchmark.

## Unlinkability Lab v0.7 — cross-family / cross-policy replication

v0.7 independently challenged the strong local v0.6 mechanism across changed transformation families, scoring policies, population sizes, generation seeds, artifact seeds, holdout partitions, and transfer conditions.

Reference result:

- predictive holdout cells: **5 / 60**
- transfer-supported cells: **3 / 30**
- median holdout Pearson `r`: **0.0**
- median transfer Pearson `r`: **0.0**
- historical scorer parity: **PASS**
- matrix scorer parity: **PASS**
- commuting controls: **PASS**
- classification: **`MECHANISM_NOT_REPLICATED`**

The broader mechanism claim therefore failed its predeclared replication gate. v0.6 remains a valid local result; v0.7 blocks promotion of that result into a broad transferable system property.

> **Replication failure != permission to tune the protocol after observing results.**

## v0.8 — open-set / false-attribution program

v0.8 changes the task from closed-set best-match attribution to an open-set question:

> Is there enough evidence to attribute this artifact to any represented synthetic person at all?

The protocol separately measures known correct acceptance, known wrong acceptance, unknown false identification, rejection, threshold transfer, and the effect of provenance-assisted candidate narrowing.

The full DDC pre-execution audit found and repaired ambiguities involving calibration/holdout partitioning, single-candidate confidence, malformed provenance handling, candidate-filter evidence, transfer usefulness, aggregate-label precedence, repeated measures, calibration provenance, and exact protocol lineage.

**Current status:**

- base protocol: frozen;
- Amendment 1: frozen;
- Claim Amendment 1: frozen;
- full protocol audit: **PASS for implementation**;
- implementation: **not yet canonical in the repository**;
- canonical reference run: **not authorized yet**.

The governed next transition is to implement the exact v0.8 candidate and tests, audit that implementation, and only then authorize a canonical reference run.

## v0.9 candidate — attribution boundary / key architecture

A public technical discussion on 2026-08-22 exposed two useful challenges:

1. when stronger auxiliary evidence already exists, how much **marginal** attribution value does the watermark actually add?
2. how do privacy properties change under global, model-level, rotating, cohort-level, session-level, synthetic user-level, or layered key scopes?

These questions are recorded in [`research/ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md`](research/ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md).

This is **not a v0.9 protocol** and does not authorize implementation. v0.8 must be closed or explicitly superseded through a separate governed transition first.

## Running the completed synthetic labs

The existing labs use the Python standard library.

```bash
python -m unittest discover -s tests -v
```

Individual completed programs can also be run through their module entry points where defined. The v0.8 reference experiment must not be treated as runnable/canonical until its implementation gate is satisfied.

## Research files

### v0.1
- [`lab/unlinkability_lab.py`](lab/unlinkability_lab.py)
- [`tests/test_unlinkability_lab.py`](tests/test_unlinkability_lab.py)
- [`research/TEST_PLAN.md`](research/TEST_PLAN.md)
- [`research/CLAIM_REGISTER.md`](research/CLAIM_REGISTER.md)
- [`research/RESULTS-v0.1.md`](research/RESULTS-v0.1.md)
- [`research/reference-report-v0.1.json`](research/reference-report-v0.1.json)

### v0.2
- [`lab/text_unlinkability_lab.py`](lab/text_unlinkability_lab.py)
- [`tests/test_text_unlinkability_lab.py`](tests/test_text_unlinkability_lab.py)
- [`research/TEST_PLAN-v0.2.md`](research/TEST_PLAN-v0.2.md)
- [`research/CLAIM_REGISTER-v0.2.md`](research/CLAIM_REGISTER-v0.2.md)
- [`research/RESULTS-v0.2.md`](research/RESULTS-v0.2.md)
- [`research/VALIDATION-v0.2.md`](research/VALIDATION-v0.2.md)
- [`research/reference-report-v0.2.json`](research/reference-report-v0.2.json)

### v0.3
- [`lab/transformation_chain_lab.py`](lab/transformation_chain_lab.py)
- [`tests/test_transformation_chain_lab.py`](tests/test_transformation_chain_lab.py)
- [`research/TEST_PLAN-v0.3.md`](research/TEST_PLAN-v0.3.md)
- [`research/CLAIM_REGISTER-v0.3.md`](research/CLAIM_REGISTER-v0.3.md)
- [`research/RESULTS-v0.3.md`](research/RESULTS-v0.3.md)
- [`research/VALIDATION-v0.3.md`](research/VALIDATION-v0.3.md)
- [`research/reference-report-v0.3.json`](research/reference-report-v0.3.json)

### v0.4
- [`lab/path_dependence_lab.py`](lab/path_dependence_lab.py)
- [`tests/test_path_dependence_lab.py`](tests/test_path_dependence_lab.py)
- [`research/TEST_PLAN-v0.4.md`](research/TEST_PLAN-v0.4.md)
- [`research/CLAIM_REGISTER-v0.4.md`](research/CLAIM_REGISTER-v0.4.md)
- [`research/RESULTS-v0.4.md`](research/RESULTS-v0.4.md)
- [`research/VALIDATION-v0.4.md`](research/VALIDATION-v0.4.md)
- [`research/reference-report-v0.4.json`](research/reference-report-v0.4.json)

### v0.5
- [`lab/robustness_lab.py`](lab/robustness_lab.py)
- [`tests/test_robustness_lab.py`](tests/test_robustness_lab.py)
- [`research/TEST_PLAN-v0.5.md`](research/TEST_PLAN-v0.5.md)
- [`research/CLAIM_REGISTER-v0.5.md`](research/CLAIM_REGISTER-v0.5.md)
- [`research/RESULTS-v0.5.md`](research/RESULTS-v0.5.md)
- [`research/VALIDATION-v0.5.md`](research/VALIDATION-v0.5.md)
- [`research/reference-report-v0.5.json`](research/reference-report-v0.5.json)

### v0.6
- [`lab/noncommutativity_lab.py`](lab/noncommutativity_lab.py)
- [`tests/test_noncommutativity_lab.py`](tests/test_noncommutativity_lab.py)
- [`research/TEST_PLAN-v0.6.md`](research/TEST_PLAN-v0.6.md)
- [`research/CLAIM_REGISTER-v0.6.md`](research/CLAIM_REGISTER-v0.6.md)
- [`research/RESULTS-v0.6.md`](research/RESULTS-v0.6.md)
- [`research/VALIDATION-v0.6.md`](research/VALIDATION-v0.6.md)
- [`research/reference-report-v0.6.json`](research/reference-report-v0.6.json)

### v0.7
- [`lab/cross_family_replication_lab.py`](lab/cross_family_replication_lab.py)
- [`lab/cross_family_replication_diagnostics.py`](lab/cross_family_replication_diagnostics.py)
- [`tests/test_cross_family_replication_lab.py`](tests/test_cross_family_replication_lab.py)
- [`tests/test_cross_family_replication_diagnostics.py`](tests/test_cross_family_replication_diagnostics.py)
- [`research/TEST_PLAN-v0.7.md`](research/TEST_PLAN-v0.7.md)
- [`research/CLAIM_REGISTER-v0.7.md`](research/CLAIM_REGISTER-v0.7.md)
- [`research/RESULTS-v0.7.md`](research/RESULTS-v0.7.md)
- [`research/VALIDATION-v0.7.md`](research/VALIDATION-v0.7.md)
- [`research/holdout-matrix-v0.7.json`](research/holdout-matrix-v0.7.json)
- [`research/transfer-matrix-v0.7.json`](research/transfer-matrix-v0.7.json)

### v0.8 — pre-execution governed state
- [`research/TEST_PLAN-v0.8.md`](research/TEST_PLAN-v0.8.md)
- [`research/TEST_PLAN-v0.8-AMENDMENT-1.md`](research/TEST_PLAN-v0.8-AMENDMENT-1.md)
- [`research/CLAIM_REGISTER-v0.8-PREDECLARED.md`](research/CLAIM_REGISTER-v0.8-PREDECLARED.md)
- [`research/CLAIM_REGISTER-v0.8-AMENDMENT-1.md`](research/CLAIM_REGISTER-v0.8-AMENDMENT-1.md)
- [`research/DDC_AUDIT-v0.8-PROTOCOL.md`](research/DDC_AUDIT-v0.8-PROTOCOL.md)
- [`research/DDC_FULL_AUDIT-v0.8-PROTOCOL.md`](research/DDC_FULL_AUDIT-v0.8-PROTOCOL.md)
- [`docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json`](docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json)

### Research governance and next questions
- [`research/RESEARCH_METHOD.md`](research/RESEARCH_METHOD.md)
- [`research/EXTERNAL_REVIEW_LOG.md`](research/EXTERNAL_REVIEW_LOG.md)
- [`research/ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md`](research/ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md)

## Publication files

- [`paper.md`](paper.md) — original full research note, Version 1.0
- [`publications/Beyond_Model_Provenance_v1.0.md`](publications/Beyond_Model_Provenance_v1.0.md) — continuation publication record through v0.7
- [`publications/README.md`](publications/README.md) — publication index
- [`CITATION.cff`](CITATION.cff) — original publication citation metadata

The published v1.0 artifacts remain immutable historical records. New research questions are added through the repository lineage rather than silently rewriting previously published evidence.

## Suggested citation

Rukhaylo, Valentyn. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

For the continued experimental program through v0.7, see the separate *Beyond Model Provenance* publication record in `publications/`.

## Research provenance

The central system-level research question — whether non-identifying model provenance can become human attribution through correlation with other evidence — was formulated by **Valentyn Rukhaylo of Altru.dev on August 18, 2026**.

Research assistance was provided using ChatGPT for literature discovery, source comparison, technical synthesis, drafting, implementation support, synthetic test design, and audit assistance. The repository separates documented facts, hypotheses, synthetic experimental results, architectural implications, public criticism, and explicit nonclaims.

## Keywords

AI text watermarking · AI provenance · Claude watermark · Anthropic · AI privacy · privacy engineering · model attribution · user attribution · human attribution · compositional privacy · provenance-mediated identity linkage · unlinkability · re-identification testing · stylometry · semantic linkage · transformation lineage · path dependence · non-commutativity · replication · false attribution · open-set attribution · key architecture · auditability · generative AI governance · AI accountability · digital privacy
