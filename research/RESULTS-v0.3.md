# Reference Results v0.3 — Attribution Persistence Through Transformation Chains

**Status:** Experimental synthetic-text benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, generated synthetic text, and transparent proxy transformations only

## Question

v0.3 asks whether attribution decreases monotonically as an artifact passes through multiple transformations, or whether identifying information can migrate between channels and reappear later.

The tested chain is:

`original → edit → paraphrase → summarize → translate → model edit → multi-model edit`

The experiment uses 12 synthetic persons and 144 synthetic generation events. Random person attribution is therefore **8.33%**.

## Headline result

| Stage | Person top-1 | Generation top-1 | Generation top-5 | Mean near-best anonymity set |
|---|---:|---:|---:|---:|
| Original publication derivative | **98.61%** | 56.25% | 100.00% | 1.63 |
| Edit | **98.61%** | 56.25% | 100.00% | 1.63 |
| Paraphrase + provenance removal | **34.03%** | 11.81% | 55.56% | 1.83 |
| Summarize | **9.03%** | 4.17% | 22.22% | 3.67 |
| Translate proxy | **18.06%** | 6.94% | 23.61% | 17.56 |
| Model-edit proxy | **27.08%** | 8.33% | 34.03% | 23.06 |
| Multi-model-edit proxy | **25.69%** | 7.64% | 34.72% | 23.08 |

## Most important finding

Privacy improvement was **not monotonic**.

Summarization reduced person attribution to **9.03%**, close to the 8.33% random-person baseline. But later transformations raised attribution again:

`9.03% → 18.06% → 27.08% → 25.69%`

The final chain therefore receives:

`NOT_SUPPORTED`

for the declared unlinkability threshold.

This is a stronger result than a clean success case because it demonstrates that a transformation can reduce one set of linkage signals while preserving or exposing another set that becomes more useful to the attacker later.

> **Privacy transformation is not monotonic.**

> **A later transformation can re-expose linkability that appeared to collapse earlier in the chain.**

## Channel migration

The strongest individual person-attribution channel changed during the chain:

- original: **style**
- edit: **lexical**
- paraphrase: **style**
- summarize: **lexical**
- translate: **lexical**
- model edit: **lexical**
- multi-model edit: **lexical**

Observed channel transitions:

`style → lexical → style → lexical`

This is direct evidence inside the synthetic benchmark that identity-bearing information should be treated as a **dynamic linkage graph**, not a fixed identifier that can simply be removed once.

## Provenance removal still does not imply unlinkability

The paraphrase stage removes the simulated provider/model provenance marker and provider hint. Person attribution nevertheless remains **34.03%**, more than four times the random-person baseline.

This independently preserves the earlier finding:

> **Watermark/provenance removal ≠ unlinkability.**

## Semantic preservation and privacy

The proxy chain preserved high semantic-topic similarity even after aggressive transformations. At the final stage the internal semantic-retention measure was approximately **99.71%**, while direct content-word retention fell to **37.36%** and length to **48.76%**.

The important implication is not that these proxy transforms are production anonymizers. It is that **semantic preservation can coexist with substantial residual attribution**, and surface destruction alone is therefore insufficient evidence of privacy.

## Explicit non-claims

These results do not establish the behavior of Claude, Anthropic, SynthID, OpenAI, Gemini, LinkedIn, or any deployed translation/model system.

The translation stage is a deterministic semantics-preserving proxy. The model-edit stages are deterministic transparent proxies. They exist to measure transition effects and channel migration without introducing proprietary black-box behavior.

No real people, accounts, provider logs, private conversations, scraped profiles, or external identity datasets are used.

## Validation

Exact v0.3 implementation validation before repository publication:

- Python compile check: **PASS**
- v0.3 adversarial regression tests: **12/12 PASS**
- deterministic 144-generation reference run: **PASS**
- v0.1 and v0.2 files are not modified by v0.3

Standing rules remain:

> **Privacy transformation ≠ privacy evidence.**

> **Failed re-identification ≠ proven anonymity.**

## Next research question

v0.4 should test **path dependence**: whether the same transformations applied in a different order produce materially different attribution outcomes. If order matters, then privacy becomes a property of the complete transformation history, not merely the final artifact.