# Test Plan v0.5 — Path-Dependence Robustness

## Purpose

Determine whether v0.4 transformation-order path dependence survives controlled perturbations or is specific to one synthetic benchmark configuration.

## DDC authority and scope boundary

Authorized: generated `syn-` identities, generated text, transparent deterministic/seeded-stochastic transforms, declared local attribution policies, and local evidence only.

Excluded: real identities/accounts, private/provider logs, scraped profiles, external identity corpora, proprietary watermark reverse engineering, and claims about deployed providers.

## Predecessor contract

v0.1-v0.4 files must remain unchanged. Before any robustness claim, the full canonical scenario must reproduce v0.4 exactly:

- person top-1 min 25.694444%
- max 44.444444%
- spread 18.75 percentage points
- same best and worst paths

## Perturbation families

1. population size;
2. generation seed;
3. controlled text-length proxy;
4. transformation strength;
5. reproducible stochastic transform decisions;
6. attribution-policy weights;
7. commuting-order negative control.

## Path contract

Every privacy path contains exactly once:

`paraphrase, summarize, translate, model_edit`

## Sampling contract

The canonical reproduction evaluates all 144 artifacts. Stress scenarios evaluate an evenly spaced deterministic sample of 18 artifacts while each artifact is still ranked against the full candidate-generation population. Sampling is recorded per scenario.

## Measurements

- person top-1;
- generation top-1/top-5;
- path spread;
- random-person baseline;
- first/last and pairwise order effects;
- internal utility;
- commuting-control equality.

## Materiality rule

A scenario is material when:

`max(person_top1) - min(person_top1) >= 1 / persons`

This is a declared benchmark threshold, not a statistical-significance or legal-anonymity definition.

## Robustness gate

`ROBUST_IN_DECLARED_MATRIX` requires canonical parity, ≥80% material scenarios, a passing commuting negative control, preservation of negative results, and explicit scope boundaries. Otherwise downgrade to `MIXED` or `NOT_ESTABLISHED`.

## Standing rules

- Privacy transformation ≠ privacy evidence.
- Failed re-identification ≠ proven anonymity.
- Intermediate unlinkability ≠ end-to-end unlinkability.
- Transformation set ≠ transformation history ≠ privacy outcome.
- Single benchmark result ≠ robust system property.
