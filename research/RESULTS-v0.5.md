# Reference Results v0.5 — Path-Dependence Robustness

**Status:** Experimental synthetic robustness benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, generated synthetic text, transparent transformations, and declared attribution policies only

## Research question

v0.4 established that the same four transformations can produce different residual attribution when their order changes. v0.5 asks whether that result survives controlled perturbation or disappears when benchmark conditions change.

The matrix varies synthetic population size, generation seed, source-text length, transformation strength, deterministic versus reproducible stochastic transformations, attribution-policy weights, and a commuting-order negative control.

## Canonical parity with v0.4

The full canonical scenario uses **12 synthetic persons / 144 generations / 24 orders / all 144 artifacts evaluated** and exactly reproduces v0.4:

- minimum person top-1: **25.69%**
- maximum person top-1: **44.44%**
- spread: **18.75 percentage points**
- lowest-linkability path: `summarize → model edit → translate → paraphrase`
- highest-linkability path: `paraphrase → translate → model edit → summarize`

This predecessor-parity gate prevents v0.5 from silently changing the phenomenon it is testing.

## Robustness matrix

The reference matrix contains **13 scenarios**. The canonical scenario is exhaustive. Stress scenarios use a deterministic evenly spaced sample of 18 publication artifacts while retaining the full candidate-generation population.

Path dependence crossed the population-relative materiality threshold in **12/13 scenarios (92.31%)**.

Person-attribution spread across the matrix ranged from **0.00 to 55.56 percentage points**, with a mean of **33.07 points** and median of **27.78 points**.

| Scenario | Person min | Person max | Spread | Material |
|---|---:|---:|---:|---|
| `canonical_full` | 25.69% | 44.44% | 18.75 pp | yes |
| `policy_content_only` | 16.67% | 72.22% | 55.56 pp | yes |
| `policy_lexical_heavy` | 16.67% | 66.67% | 50.00 pp | yes |
| `policy_semantic_heavy` | 16.67% | 72.22% | 55.56 pp | yes |
| `policy_style_heavy` | 33.33% | 61.11% | 27.78 pp | yes |
| `population_16` | 11.11% | 38.89% | 27.78 pp | yes |
| `population_6` | 33.33% | 88.89% | 55.56 pp | yes |
| `seed_17` | 33.33% | 66.67% | 33.33 pp | yes |
| `seed_53` | 38.89% | 61.11% | 22.22 pp | yes |
| `sentences_3` | 38.89% | 66.67% | 27.78 pp | yes |
| `sentences_9` | 38.89% | 55.56% | 16.67 pp | yes |
| `stochastic_101` | 27.78% | 66.67% | 38.89 pp | yes |
| `strength_0.50` | 38.89% | 38.89% | 0.00 pp | no |

## Boundary result: weaker transformations

The only scenario that did not cross its materiality threshold was `strength_0.50`. In that condition all 24 orders produced the same person top-1 result, so the measured order spread was **0.00 percentage points**.

That negative result matters. v0.5 does **not** support the claim that order effects are inevitable. In this controlled benchmark, weakening the transformations enough removed the measurable path-dependence effect.

## Directional stability

The sign of the v0.4 `summarize before model edit` pairwise effect remained non-positive in **100%** of declared scenarios. This is a bounded benchmark observation, not a general prescription for production privacy pipelines.

## Equivalent-order control

The negative control reverses two operations designed to commute:

`lowercase → normalize whitespace`

versus

`normalize whitespace → lowercase`

Final text identical: **yes**  
Final metadata identical: **yes**  
Control: **PASS**

The harness therefore does not report path dependence merely because two operations were permuted.

## DDC interpretation

v0.5 adds:

> **Single Benchmark Result ≠ Robust System Property**

And a proposed **Privacy Robustness Invariant**:

> A privacy property inferred from one transformation path, population, seed, model, or scoring policy must not be promoted to a system-level property until it survives declared perturbation tests, includes negative controls, and preserves the conditions under which the property fails.

The standing chain is now:

- **Privacy transformation ≠ privacy evidence**
- **Failed re-identification ≠ proven anonymity**
- **Intermediate unlinkability ≠ end-to-end unlinkability**
- **Transformation set ≠ transformation history ≠ privacy outcome**
- **Single benchmark result ≠ robust system property**

## Claim status

`ROBUST_IN_DECLARED_MATRIX`

This means only that path dependence remained material in at least 80% of the declared synthetic scenarios and the commuting-order control remained invariant. It does not establish a universal law, deployed-provider behavior, or anonymity of any artifact.

## Validation

```text
Python compile: PASS
v0.5 unit/adversarial tests: 15/15 PASS
canonical v0.4 parity: PASS
13-scenario robustness reference run: PASS
commuting-order negative control: PASS
```

## Next experiment

v0.6 should isolate **mechanism**: which state changes make two privacy transforms non-commutative, which channels are created/destroyed by each ordering, and whether the privacy consequence can be predicted before running the full attribution attack.
