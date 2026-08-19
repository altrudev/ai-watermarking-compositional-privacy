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

The repository includes the inverse experiment: instead of stopping after identifying possible linkage channels, the lab attempts to break those channels and then attacks its own privacy transformations with re-identification tests.

**v0.1 is synthetic-only.** It does not ingest real people, real accounts, provider logs, scraped social profiles, or private identity datasets. The simulated watermark is an abstract provider/model signal, not an implementation or emulation of Claude, SynthID, OpenAI, Gemini, or another deployed watermark.

The reference synthetic run contains 480 generation events. Under the strongest declared provider-plus-publisher evidence policy:

- combined baseline person attribution: **82.08%**
- after removing only the simulated provenance marker: **56.88%**
- after the composite privacy transformation: **5.42%**
- measured correlation gain over the strongest single signal: **47.91 percentage points**

These results demonstrate behavior inside the controlled synthetic model; they are not claims about a deployed provider.

## Unlinkability Lab v0.2 — actual synthetic text

v0.2 replaces the abstract semantic/style vectors with **actual generated text** and derives linkage evidence from the text itself: lexical surface features, semantic topic features, and a 16-dimension stylometric profile. It retains the simulated provenance, provider, and timing channels so the experiment can measure how independent weak signals compose.

The public artifact is deliberately an edited derivative rather than a byte-identical copy of the synthetic generation. This prevents exact text equality from trivially becoming the experiment.

Reference v0.2 population: **24 synthetic persons / 288 generation events**.

| Condition | Person top-1 | Generation top-1 |
|---|---:|---:|
| Combined evidence | **81.94%** | **44.44%** |
| Provenance removed only | **28.47%** | **12.15%** |
| Composite privacy transform | **3.12%** | **0.69%** |

The strongest individual person-attribution signal was only **20.83%**. Combining the available signals increased attribution to **81.94%**, a **61.11 percentage-point correlation gain** inside the declared synthetic-text model.

The composite transform retained approximately **84.04% topic/semantic utility**, **85.51% content-word retention**, and **91.19% text-length retention** under the lab's internal measures. These are synthetic utility measurements, not a claim of human-perceived quality or anonymity.

A useful negative result also appeared: changing stylometry alone did not materially improve system-level privacy in the combined test because other linkage channels continued to dominate. That is why the lab evaluates transformations against the complete evidence composition rather than grading each transformation in isolation.

## Unlinkability Lab v0.3 — transformation-chain persistence

v0.3 tests whether privacy improvement is monotonic across a complete transformation history:

`original → edit → paraphrase → summarize → translate → model edit → multi-model edit`

The reference run uses **12 synthetic persons / 144 generation events**. Random person attribution is **8.33%**.

| Stage | Person top-1 |
|---|---:|
| Original publication derivative | **98.61%** |
| Edit | **98.61%** |
| Paraphrase + provenance removal | **34.03%** |
| Summarize | **9.03%** |
| Translate proxy | **18.06%** |
| Model-edit proxy | **27.08%** |
| Multi-model-edit proxy | **25.69%** |

The important result is negative: **privacy was not monotonic**. Attribution fell close to random after summarization, then increased again during later transformations. The strongest individual linkage channel also migrated `style → lexical → style → lexical` during the chain.

The final chain therefore receives `NOT_SUPPORTED` for the declared unlinkability threshold. v0.3 preserves the adverse result rather than tuning later transforms until the benchmark passes.

This adds two standing distinctions:

> **Intermediate unlinkability ≠ end-to-end unlinkability.**

> **Final artifact state ≠ complete privacy lineage.**

## Unlinkability Lab v0.4 — transformation path dependence

v0.4 holds the transformation set constant and changes only the order. It evaluates all **24 permutations** of:

`paraphrase + summarize + translate + model edit`

Every path starts from the same artifacts, applies each transform exactly once, ends with identical metadata, removes the same simulated provenance fields, and has the same cumulative publication delay.

Yet person attribution ranges from **25.69% to 44.44%** — an **18.75 percentage-point spread** against an 8.33% random-person baseline.

Lowest residual attribution:

`summary → model edit → translate → paraphrase` → **25.69%**

Highest residual attribution:

`paraphrase → translate → model edit → summary` → **44.44%**

The strongest pairwise ordering effect was between summarization and model editing: paths with summarization before model editing averaged **26.39%** person attribution, while the reverse order averaged **40.97%**.

v0.4 therefore adds:

> **Transformation Set ≠ Transformation History ≠ Privacy Outcome.**

And the proposed **Privacy Path Dependence Invariant**:

> A privacy claim about a transformed artifact must preserve and evaluate the ordered transformation history. The same set of privacy transformations must not be assumed to produce equivalent unlinkability when their order differs.

## Unlinkability Lab v0.5 — robustness of path dependence

v0.5 tests whether the v0.4 ordering effect survives changes in population size, random seed, source-text length, transformation strength, seeded stochastic behavior, and attribution-policy weights. It also adds a commuting-order negative control.

The full canonical scenario exactly reproduces v0.4. Across the **13-scenario** robustness matrix, transformation-order path dependence remained material in **12/13 scenarios (92.31%)**. The only non-material condition was the half-strength transform case, where all 24 orders produced the same person-attribution result.

The commuting control reverses `lowercase` and `normalize whitespace`; both orders produce identical final text and metadata, confirming that the harness does not report path dependence merely because operations were permuted.

v0.5 therefore adds:

> **Single Benchmark Result ≠ Robust System Property.**

And the proposed **Privacy Robustness Invariant**:

> A privacy property inferred from one transformation path, population, seed, model, or scoring policy must not be promoted to a system-level property until it survives declared perturbation tests, includes negative controls, and preserves the conditions under which the property fails.

The lab preserves the earlier rules:

> **Privacy transformation ≠ privacy evidence.**

> **Failed re-identification ≠ proven anonymity.**

> **Intermediate unlinkability ≠ end-to-end unlinkability.**

Run locally with standard Python only:

```bash
python -m unittest discover -s tests -v
python -m lab.robustness_lab
```

Research files:

### v0.1
- [`lab/unlinkability_lab.py`](lab/unlinkability_lab.py) - deterministic abstract attribution/unlinkability harness
- [`tests/test_unlinkability_lab.py`](tests/test_unlinkability_lab.py) - v0.1 adversarial regression suite
- [`research/TEST_PLAN.md`](research/TEST_PLAN.md) - v0.1 DDC-governed test plan and threat model
- [`research/CLAIM_REGISTER.md`](research/CLAIM_REGISTER.md) - v0.1 claim maturity and explicit non-claims
- [`research/RESULTS-v0.1.md`](research/RESULTS-v0.1.md) - human-readable v0.1 reference results
- [`research/reference-report-v0.1.json`](research/reference-report-v0.1.json) - machine-readable v0.1 experiment record

### v0.2
- [`lab/text_unlinkability_lab.py`](lab/text_unlinkability_lab.py) - actual synthetic-text attribution/unlinkability harness
- [`tests/test_text_unlinkability_lab.py`](tests/test_text_unlinkability_lab.py) - actual-text adversarial regression suite
- [`research/TEST_PLAN-v0.2.md`](research/TEST_PLAN-v0.2.md) - DDC-governed v0.2 test plan
- [`research/CLAIM_REGISTER-v0.2.md`](research/CLAIM_REGISTER-v0.2.md) - v0.2 claim register and non-claims
- [`research/RESULTS-v0.2.md`](research/RESULTS-v0.2.md) - v0.2 results and interpretation boundary
- [`research/reference-report-v0.2.json`](research/reference-report-v0.2.json) - machine-readable v0.2 result record

### v0.3
- [`lab/transformation_chain_lab.py`](lab/transformation_chain_lab.py) - transformation-history and channel-migration harness
- [`tests/test_transformation_chain_lab.py`](tests/test_transformation_chain_lab.py) - v0.3 adversarial regression suite
- [`research/TEST_PLAN-v0.3.md`](research/TEST_PLAN-v0.3.md) - v0.3 DDC-governed test plan
- [`research/CLAIM_REGISTER-v0.3.md`](research/CLAIM_REGISTER-v0.3.md) - v0.3 claim register and explicit non-claims
- [`research/RESULTS-v0.3.md`](research/RESULTS-v0.3.md) - transformation-chain results
- [`research/VALIDATION-v0.3.md`](research/VALIDATION-v0.3.md) - exact-source validation record
- [`research/reference-report-v0.3.json`](research/reference-report-v0.3.json) - machine-readable v0.3 result record

### v0.4
- [`lab/path_dependence_lab.py`](lab/path_dependence_lab.py) - exhaustive transformation-order experiment
- [`tests/test_path_dependence_lab.py`](tests/test_path_dependence_lab.py) - v0.4 path-dependence regression suite
- [`research/TEST_PLAN-v0.4.md`](research/TEST_PLAN-v0.4.md) - DDC-governed v0.4 test plan
- [`research/CLAIM_REGISTER-v0.4.md`](research/CLAIM_REGISTER-v0.4.md) - v0.4 claims and explicit non-claims
- [`research/RESULTS-v0.4.md`](research/RESULTS-v0.4.md) - path-dependence results
- [`research/VALIDATION-v0.4.md`](research/VALIDATION-v0.4.md) - v0.4 validation record
- [`research/reference-report-v0.4.json`](research/reference-report-v0.4.json) - machine-readable v0.4 result record

### v0.5
- [`lab/robustness_lab.py`](lab/robustness_lab.py) - path-dependence robustness matrix and negative control
- [`tests/test_robustness_lab.py`](tests/test_robustness_lab.py) - v0.5 regression/adversarial suite
- [`research/TEST_PLAN-v0.5.md`](research/TEST_PLAN-v0.5.md) - DDC-governed robustness test plan
- [`research/CLAIM_REGISTER-v0.5.md`](research/CLAIM_REGISTER-v0.5.md) - v0.5 claims and explicit non-claims
- [`research/RESULTS-v0.5.md`](research/RESULTS-v0.5.md) - robustness results and boundary case
- [`research/VALIDATION-v0.5.md`](research/VALIDATION-v0.5.md) - exact-source validation record
- [`research/reference-report-v0.5.json`](research/reference-report-v0.5.json) - machine-readable v0.5 record

## Publication files

- [`paper.md`](paper.md) - full research note
- [`CITATION.cff`](CITATION.cff) - machine-readable citation metadata

## Suggested citation

Rukhaylo, Valentyn. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

## Research provenance

The central system-level research question - whether non-identifying model provenance can become human attribution through correlation with generation and identity records - was formulated by **Valentyn Rukhaylo of Altru.dev on August 18, 2026**.

Research assistance was provided using ChatGPT for literature discovery, source comparison, technical synthesis, drafting, and implementation of the synthetic unlinkability test harness. The publication and lab distinguish documented facts from derived architectural implications, experimental results, hypotheses, and explicit non-claims.

## Keywords

AI text watermarking · AI provenance · Claude watermark · Anthropic · AI privacy · privacy engineering · model attribution · user attribution · human attribution · compositional privacy · provenance-mediated identity linkage · unlinkability · re-identification testing · stylometry · semantic linkage · transformation lineage · path dependence · privacy robustness · generative AI governance · AI accountability · digital privacy