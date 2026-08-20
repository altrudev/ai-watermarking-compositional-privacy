# Reference Results v0.6 — Pairwise Non-Commutativity Mechanism

**Status:** Experimental synthetic-text mechanism benchmark  
**Scope:** Synthetic identities, generated synthetic text, transparent proxy transformations, and the existing attribution model only  
**Predecessor:** `43d4b97a1c9b53a73de079ac166134fba663f494`

## Reference result

The v0.6 reference run evaluates 12 synthetic persons / 144 synthetic generation events, all six unordered pairs of four transformations in both orders, and all 24 complete transformation paths.

- cached evaluator parity with the canonical v0.3 scorer: **PASS**
- commuting negative control: **PASS**
- pairwise full-path predictor Pearson correlation: **0.928292107191**
- predeclared `r >= 0.70` gate: **PASS**
- emitted claim status: `PAIRWISE_MECHANISM_PREDICTIVE_FOR_DECLARED_TEST`

The result supports only the declared synthetic benchmark claim: pairwise ordering effects explain a substantial portion of the observed full-path attribution variation under this fixed population, transformations, and attribution model.

## Pairwise mechanism matrix

| Pair | Final text differs | Metadata identical | Person top-1 order effect | Largest changed channel |
|---|---:|---:|---:|---|
| paraphrase ↔ summarize | 0% | yes | 0.00 pp | lexical (tie at zero) |
| paraphrase ↔ translate | 100% | yes | -1.39 pp | lexical |
| paraphrase ↔ model edit | 0% | yes | 0.00 pp | lexical (tie at zero) |
| summarize ↔ translate | 0% | yes | 0.00 pp | lexical (tie at zero) |
| summarize ↔ model edit | 100% | yes | **-23.61 pp** | lexical |
| translate ↔ model edit | 0% | yes | 0.00 pp | lexical (tie at zero) |

The dominant directional effect is `summarize → model_edit` versus `model_edit → summarize`, with a **23.61 percentage-point** difference in person top-1 attribution. The corresponding generation top-1 difference is **13.89 points**.

The smaller `paraphrase ↔ translate` interaction changes person attribution by **1.39 points**. The remaining four pairs are effectively commuting under the declared final text/attribution measurements.

## Channel evidence

For `summarize ↔ model_edit`, reversing order changes:

- lexical-only person top-1 by **-8.33 pp**;
- semantic-only person top-1 by **-4.86 pp**;
- style-only, watermark-only, and timing-only person attribution by **0.00 pp**.

Final metadata remains identical. The mechanism therefore appears in text-derived evidence channels rather than through a provider/timing metadata difference.

## Negative control

`lowercase → normalize whitespace`

and

`normalize whitespace → lowercase`

produce identical final text and metadata, with zero person and generation attribution difference. The control passes.

## Determinism and exact-source validation

The optimized v0.6 candidate preserves scoring semantics but caches reusable feature/component scores.

- exact candidate Git blob: `f0269836e2b4d611b1aff6eee2f85a5c7b9013a3`
- v0.6 focused tests: **7/7 PASS**
- canonical scorer parity: **PASS**
- two full reference runs serialized with sorted JSON: **byte-identical**
- sorted reference JSON SHA-256: `9ffa255849d49d611503fe3b69c568d594775eb68cd1af5225119047c009e7ad`

## Interpretation boundary

This result does **not** establish a universal transformation-order law, deployed-provider behavior, anonymity, human attribution capability, or a production privacy policy.

It supports a narrower mechanism finding inside the declared synthetic benchmark:

> Some transformation-order effects are concentrated in specific non-commuting transform pairs, and those pairwise effects are strongly predictive of complete-path attribution variation in this reference experiment.

The result must remain experimental until independently tested under broader conditions.

Standing rules remain:

> **Privacy transformation ≠ privacy evidence.**

> **Failed re-identification ≠ proven anonymity.**

> **Synthetic benchmark mechanism ≠ deployed-provider mechanism.**
