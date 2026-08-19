# Path-Dependence Benchmark — Test Plan v0.4

## Purpose

v0.4 tests the next question produced by the v0.3 adverse result: whether privacy depends on the **order** of transformations, not merely on which transformations were applied or what the final artifact looks like.

## DDC research boundary

### Authority

The experiment is authorized only to generate, transform, and re-identify identities and text created by the synthetic harness.

### Prohibited expansion

No real names, accounts, conversations, provider logs, scraped profiles, identity corpora, or proprietary detector data are ingested.

### Standing evidence rules

- Privacy transformation ≠ privacy evidence.
- Intermediate unlinkability ≠ end-to-end unlinkability.
- Final artifact state ≠ complete privacy lineage.
- Same transform set ≠ assumed same privacy outcome.
- Failed re-identification ≠ proven anonymity.

## Transform set

v0.4 permutes five privacy-relevant v0.3 transformations:

1. paraphrase;
2. summarize;
3. translate proxy;
4. model-edit proxy;
5. multi-model-edit proxy.

The v0.3 `edit` stage is excluded because the canonical v0.3 reference run measured no attribution change at that stage. This exclusion is declared before the v0.4 reference result.

Five transforms produce **120 unique orders**. The reference experiment evaluates all of them rather than sampling favorable paths.

## Primary metric

For each order, measure final person top-1 attribution under the unchanged v0.3 combined scoring semantics.

Define order sensitivity as:

```text
maximum final person top-1 across all orders
- minimum final person top-1 across all orders
```

Predeclared support threshold:

**10 percentage points**.

## Utility-matched contrast

To reduce the chance that path dependence is merely a proxy for different destruction levels, search all path pairs for endpoints satisfying all of:

- semantic-retention difference ≤ 0.015;
- content-word-retention difference ≤ 0.035;
- length-ratio difference ≤ 0.035.

Among matched pairs, report the largest person-attribution difference.

This does not prove human-perceived utility equivalence; it only controls for the benchmark's declared utility metrics.

## Test families

### T1 — Exhaustive path construction

- generate exactly 120 unique permutations;
- every order contains each declared transform exactly once;
- missing, repeated, or unknown transform paths fail closed.

### T2 — Scoring compatibility

The cached exhaustive evaluator must reproduce canonical v0.3 `evaluate()` metrics for the same population/artifacts/weights.

### T3 — Determinism

The same population seed and order subset must reproduce identical result records.

### T4 — Exhaustive final-state measurement

Evaluate all 120 paths on the reference population and record person/generation attribution and utility.

### T5 — Order-sensitivity claim gate

Return `supported_for_declared_test` only if measured order sensitivity is at least 0.10. Otherwise return `not_supported`.

### T6 — Utility-matched path comparison

Search the full result set for matched-utility path pairs and report the strongest attribution contrast without changing the tolerances after observing the result.

### T7 — Path traces

Re-run the minimum- and maximum-final-attribution paths stage by stage to preserve the transition history rather than only endpoint metrics.

### T8 — Claim boundary

The output must preserve synthetic-only scope and explicitly reject universal anonymity/path-dependence claims.

## Reference population

- 8 synthetic persons;
- 96 synthetic generation events;
- seed 41;
- random person baseline 12.5%.

The population is smaller than v0.3 because exhaustive path evaluation multiplies the scoring workload by 120. The change is declared as part of the v0.4 experiment and must not be treated as a direct numerical continuation of the v0.3 population.

## Acceptance conditions

The apparatus is valid when:

1. all 120 orders are evaluated;
2. the optimized evaluator matches v0.3 scoring semantics;
3. reference execution is deterministic;
4. result maturity remains synthetic/experimental;
5. utility differences are visible rather than hidden;
6. adverse or null results are preserved rather than tuned away;
7. automated v0.4 tests pass.

A supported result validates only the declared v0.4 benchmark proposition.
