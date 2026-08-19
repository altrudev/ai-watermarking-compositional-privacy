# Reference Results v0.4 — Path Dependence of Compositional Privacy

**Status:** Experimental synthetic-text benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, generated synthetic text, and transparent proxy transformations only

## Research question

v0.4 tests whether the **same privacy-relevant transformation set** produces materially different attribution outcomes when the transformations are applied in different orders.

The declared transform set is:

- paraphrase;
- summarize;
- translate proxy;
- model-edit proxy;
- multi-model-edit proxy.

The neutral `edit` stage from v0.3 is excluded because it did not alter the v0.3 reference attribution result.

All **120 possible orders** of these five transforms are evaluated.

## Reference population

- synthetic persons: **8**;
- synthetic generation events: **96**;
- random person-attribution baseline: **12.50%**.

## Headline result

Final person top-1 attribution varied from **33.33%** to **50.00%** across the 120 orders.

Measured order sensitivity:

```text
50.00% - 33.33% = 16.67 percentage points
```

The predeclared order-sensitivity threshold was **10 percentage points**.

Reference claim:

`SUPPORTED_FOR_DECLARED_TEST`

for the proposition:

> The same declared transformation set can produce materially different attribution outcomes when transformation order changes.

This is an experimental result for the declared synthetic benchmark, not a universal privacy law.

## Lowest-attribution final path

```text
summarize
→ model edit
→ translate
→ paraphrase
→ multi-model edit
```

Final metrics:

- person top-1: **33.33%**;
- generation top-1: **9.38%**;
- generation top-5: **44.79%**;
- semantic retention: **99.78%**;
- content-word retention: **44.80%**;
- length ratio: **49.85%**.

## Highest-attribution final path

```text
translate
→ paraphrase
→ multi-model edit
→ model edit
→ summarize
```

Final metrics:

- person top-1: **50.00%**;
- generation top-1: **14.58%**;
- generation top-5: **51.04%**;
- semantic retention: **99.80%**;
- content-word retention: **43.10%**;
- length ratio: **48.59%**.

## Matched-utility contrast

To test whether the attribution difference could be explained simply by one path destroying more utility, v0.4 searches for path pairs within declared utility tolerances:

- semantic-retention difference ≤ 1.5 percentage points;
- content-word-retention difference ≤ 3.5 percentage points;
- length-ratio difference ≤ 3.5 percentage points.

A matched pair was found with the full **16.67 percentage-point person-attribution difference**.

Lower-attribution path:

```text
summarize
→ translate
→ paraphrase
→ model edit
→ multi-model edit
```

- person top-1: **33.33%**;
- semantic retention: **99.78%**;
- content-word retention: **44.80%**;
- length ratio: **49.85%**.

Higher-attribution path:

```text
translate
→ paraphrase
→ multi-model edit
→ model edit
→ summarize
```

- person top-1: **50.00%**;
- semantic retention: **99.80%**;
- content-word retention: **43.10%**;
- length ratio: **48.59%**.

The endpoint utility measurements are therefore similar under the benchmark's declared metrics while the attribution result differs materially.

## Path traces remain non-monotonic

The minimum-final-attribution path did not improve privacy monotonically:

| Stage | Person top-1 |
|---|---:|
| summarize | 57.29% |
| model edit | 76.04% |
| translate | 77.08% |
| paraphrase | 32.29% |
| multi-model edit | 33.33% |

The maximum-final-attribution path also moved non-monotonically:

| Stage | Person top-1 |
|---|---:|
| translate | 69.79% |
| paraphrase | 26.04% |
| multi-model edit | 48.96% |
| model edit | 50.00% |
| summarize | 50.00% |

This independently reinforces the v0.3 result that a low-attribution intermediate state is not durable evidence of end-to-end unlinkability.

## Distribution across all 120 orders

Final person attribution occupied a broad range rather than one stable endpoint. Nine orders ended at **33.33%** person top-1, while ten ended at **50.00%**, with the remaining paths distributed between them.

The complete full reference run is reproducible from source. The committed machine-readable report stores the extrema, matched-utility contrast, distribution, and SHA-256 identity of the complete reference stdout.

## DDC interpretation

v0.4 adds experimental support for treating privacy as a property of **transformation history**, not only the set of transformations or the final artifact.

Research distinctions supported for further testing:

> **Same transform set ≠ same privacy outcome.**

> **Final artifact state ≠ transformation-path privacy state.**

> **Temporary low attribution ≠ durable unlinkability.**

These remain experimental findings. They are not automatically constitutional rules and do not establish real-world provider or human-attribution behavior.

## Validation

Exact candidate v0.4 source:

- Python compile check: **PASS**;
- exhaustive reference run: **120/120 orders evaluated**;
- v0.4 regression suite: **11/11 PASS**;
- cached evaluator checked against canonical v0.3 scoring semantics: **PASS**;
- full reference stdout SHA-256: `e65c77293fe2e81f7645b89b9e3a014342ca8007c4f1be202f08951fbe75edcb`.

## Explicit non-claims

- This does not prove real-world path dependence for deployed AI systems.
- It does not establish anonymity for any transformation order.
- It does not emulate Claude, SynthID, OpenAI, Gemini, or proprietary model-edit/translation systems.
- Similar benchmark utility scores do not establish equivalent human-perceived quality.
- The result is conditional on the declared synthetic population, transforms, attribution model, metrics, and threshold.

## Next research question

The next useful gate is **cross-seed and cross-population stability**: determine whether the observed order effect survives changes in population size, synthetic author distribution, generation seed, and attribution weighting without tuning the experiment to preserve the result.
