# Reference Results v0.4 — Transformation Path Dependence

**Status:** Experimental synthetic benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, generated synthetic text, transparent deterministic transformation proxies, and declared attribution model only

## Research question

v0.3 showed that attribution can fall and then rise again across a transformation chain.

v0.4 asks a stricter question:

> If the **same transformations** are applied exactly once, does changing only their order change the residual attribution outcome?

The experiment holds the transformation multiset constant and evaluates every permutation of:

`paraphrase → summarize → translate → model edit`

There are **24 possible orders**.

## Controlled conditions

All 24 paths use:

- the same 12 synthetic persons;
- the same 144 generation events;
- the same starting artifacts;
- the same four transformations exactly once;
- the same cumulative publication delay;
- the same final removal of simulated provider and watermark metadata;
- the same attribution model and scoring weights.

The final metadata signature is identical across all paths. Therefore transformation **order** is the primary manipulated variable.

## Headline result

Random person baseline: **8.33%**

Across the 24 orders:

| Measure | Minimum | Maximum | Spread |
|---|---:|---:|---:|
| Person top-1 attribution | **25.69%** | **44.44%** | **18.75 percentage points** |
| Generation top-1 attribution | **4.17%** | **14.58%** | **10.42 percentage points** |

The same transformation multiset therefore produced materially different privacy outcomes when only the order changed.

> **Transformation Set ≠ Transformation History ≠ Privacy Outcome**

## Best and worst paths

Lowest residual person attribution:

`summary → model edit → translate → paraphrase`

- person top-1: **25.69%**
- generation top-1: **4.17%**

Highest residual person attribution:

`paraphrase → translate → model edit → summary`

- person top-1: **44.44%**
- generation top-1: **14.58%**

Both paths contain exactly the same four operations once.

## First-transform effect

Mean final person attribution grouped by the first operation:

| First transform | Mean final person top-1 |
|---|---:|
| summarize | **26.39%** |
| translate | **31.60%** |
| paraphrase | **35.76%** |
| model edit | **40.97%** |

In this benchmark, starting with summarization produced substantially less residual attribution than starting with model editing.

## Last-transform effect

Mean final person attribution grouped by the last operation:

| Last transform | Mean final person top-1 |
|---|---:|
| model edit | **26.39%** |
| paraphrase | **31.60%** |
| translate | **35.76%** |
| summarize | **40.97%** |

The position effect is not symmetric with the identity of the operation: the same operation can be associated with different privacy outcomes depending on where it occurs in the history.

## Pairwise order effect

The strongest measured pairwise order effect was:

- `summarize before model edit`: **26.39%** mean person attribution
- `model edit before summarize`: **40.97%**
- difference: **14.58 percentage points**

Other pairwise ordering differences were also observed.

## Final-artifact divergence

The 24 paths produced **4 distinct aggregate final-artifact digests** despite having:

- the same starting population,
- the same transformation set,
- the same number of transformations,
- identical final metadata.

This is expected for non-commutative text transformations, but v0.4 quantifies the privacy consequence of that non-commutativity.

## Utility

Across paths, internal synthetic utility stayed in a narrow band:

- semantic retention: approximately **99.42%–99.81%**
- content-word retention: approximately **44.96%–45.09%**
- length ratio: approximately **50.01%–51.24%**

The measured attribution spread therefore did not require a comparably large swing in these utility measures.

## DDC interpretation

v0.4 adds a new standing distinction:

> **Transformation Set ≠ Transformation History ≠ Privacy Outcome**

And a proposed **Privacy Path Dependence Invariant**:

> A privacy claim about a transformed artifact must preserve and evaluate the ordered transformation history. Two artifacts produced from the same source using the same set of privacy transformations must not be assumed to have equivalent unlinkability when the order of those transformations differs.

This extends the existing rules:

- **Privacy transformation ≠ privacy evidence**
- **Failed re-identification ≠ proven anonymity**
- **Intermediate unlinkability ≠ end-to-end unlinkability**
- **Same transformations ≠ same privacy outcome**

## Interpretation boundary

These results establish path dependence only inside this controlled synthetic benchmark.

They do **not** establish that any deployed AI provider, watermarking system, translation model, or editing model has the same quantitative behavior.

The translation and model-edit operations are transparent deterministic proxies. They are used to test system properties, not to emulate proprietary systems.

## Validation

Exact v0.4 source validation:

```text
Python compile: PASS
v0.4 tests: 11/11 PASS
v0.3 + v0.4 local regression: 23/23 PASS
deterministic 24-path / 144-generation reference run: PASS
```

The v0.4 branch is additive and does not modify v0.1, v0.2, or v0.3 experiment files.

## Next experiment

v0.5 should test whether the path-dependence effect survives:

1. larger synthetic populations;
2. repeated seeds;
3. longer and shorter texts;
4. different transformation strengths;
5. stochastic rather than deterministic transformations;
6. alternate attribution policies;
7. equivalent-order controls for operations that should commute.

That will distinguish a benchmark-specific ordering effect from a more general privacy property.
