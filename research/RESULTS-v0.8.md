# Results v0.8 — Open-Set Attribution and False-Attribution Study

**Status:** completed synthetic experiment candidate  
**Frozen aggregate classification:** `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`  
**Scope:** synthetic-only  
**Base protocol:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Audited amendment head:** `0a3f970beb200be97e04b9bc86b56584021e040a`  
**Implementation specification:** `87a01c30b4d7ea1185fbaba48966f8786a6b60a7`

## Executive result

v0.8 tested whether the declared synthetic attribution system could do something a closed-set matcher cannot: recognize when the true synthetic person is absent and abstain rather than force an attribution.

The strongest conclusion is not that the open-set control broadly worked, and it is not that the frozen matrix-wide false-attribution alarm fired. The result is more constrained:

> **Open-set control was feasible only in a small, context-dependent part of the declared matrix. Across most declared conditions, no predeclared score/margin threshold simultaneously met the required unknown-source rejection and known-source usefulness constraints.**

The frozen aggregate label is therefore:

`CONTEXT_DEPENDENT_OPEN_SET_CONTROL`

This label must not be paraphrased as “open-set attribution is generally safe.”

## Complete declared matrix

The matrix contained 108 core cells:

`3 scenarios × 3 artifact states × 4 evidence policies × 3 narrowing modes`

Calibration outcome:

| Scenario | Core cells | Feasible | Infeasible |
|---|---:|---:|---:|
| S1 | 36 | 10 | 26 |
| S2 | 36 | 3 | 33 |
| S3 | 36 | 0 | 36 |
| **Total** | **108** | **13** | **95** |

Thus **95/108 cells were `CALIBRATION_INFEASIBLE`** under the frozen rule. They remain adverse evidence and were not removed from the denominator.

By artifact state:

- `published_derivative`: 13/36 feasible;
- `provenance_removed`: 0/36 feasible;
- `post_transform_chain`: 0/36 feasible.

The transformed-state result does **not** establish anonymity. It means only that the declared scorer plus frozen open-set threshold rule could not simultaneously satisfy the predeclared false-identification and useful-known-attribution constraints in those cells.

## Metrics in the 13 evaluated cells

Among cells for which calibration was feasible:

- median UFIR: **1.0417%**;
- median KCAR: **75.0%**;
- median KWAR: **0.0%**;
- median equal-prior accepted precision: **96.55%**;
- median UPER: **12.5%**;
- cells with UFIR ≥10%: **1**;
- cells with UFIR ≥20%: **0**;
- cells with HS-UFIR ≥5%: **3**.

These values describe only the evaluated synthetic cells. They do not rescue the 95 calibration-infeasible cells and are not population estimates.

## Scenario behavior

### S1

10/36 cells were feasible.

Across feasible S1 cells:

- median UFIR: 1.0417%;
- UFIR range: 0% to 10.4167%;
- median KCAR: 80.2083%;
- KCAR range: 29.1667% to 97.9167%;
- median KWAR: 0%;
- maximum KWAR: 2.0833%;
- median UPER: 12.5%;
- maximum UPER: 50%.

One particularly adverse S1 cell was `published_derivative / canonical_combined / global`: calibration selected `tau_score=0.83`, `tau_margin=0`; holdout KCAR was 75%, UFIR 10.4167%, KWAR 0%, and UPER 50%.

Provider/model narrowing in that same condition reduced UFIR by 9.375 percentage points and increased KCAR by 8.333 points. This is evidence that narrowing can improve one context.

However timing-heavy narrowing showed the opposite tradeoff: relative to global, narrowing increased UFIR by 2.083 percentage points and KWAR by 2.083 points while increasing KCAR by 12.5 points. Candidate narrowing therefore does not have a single privacy direction in this benchmark.

### S2

Only 3/36 cells were feasible. All three were the `published_derivative / canonical_combined` condition under the three narrowing modes.

For those cells:

- UFIR: 8.3333%;
- KCAR: approximately 38.54%–39.58%;
- KWAR: 5.2083%;
- HS-UFIR: 6.25%;
- UPER: 25%;
- accepted precision: approximately 74%–74.51%.

The selected calibration threshold was approximately `tau_score=0.86`, `tau_margin=0.02` for these conditions.

### S3

0/36 cells were feasible.

The frozen calibration rule could not find a score/margin pair that simultaneously achieved the required calibration UFIR, KCAR and KWAR conditions in any S3 cell.

## Forced-choice observation

Across the declared candidate modes, unknown artifacts commonly retained at least one represented candidate. Without abstention, the underlying closed-set ranking operation therefore still produces a best available represented candidate even though the true synthetic person is absent.

This is why v0.8 distinguishes:

**Best match ≠ sufficient match.**

The experiment does not interpret the forced-choice candidate as truth.

## False-attribution events

Across the 13 evaluated cells, the retained evidence contains:

- 46 accepted false-attribution **cell-event instances**;
- 20 unique U-test target generations involved;
- 7 unique U-test persons involved;
- 7 unique predicted represented persons;
- 20 unique target-generation → predicted-person pairs.

The number 46 must not be described as 46 independent incidents because the same synthetic artifacts are evaluated repeatedly across policies and narrowing modes.

High-score false attribution:

- 18 cell-event instances;
- 6 unique target generations;
- 2 unique target persons;
- 2 unique predicted persons.

All six unique high-score false events occurred in the S2 canonical condition and recur across its three narrowing modes.

Accepted wrong-known attribution:

- 17 cell-event instances;
- 6 unique known target generations;
- 4 unique target persons;
- 4 unique predicted persons.

## Threshold transfer

The transfer experiment was deliberately frozen before the result.

### S1 → S2

- source thresholds unavailable: 26/36 cells;
- transferred/evaluated cells: 10;
- median destination UFIR: **21.875%**;
- median destination KCAR: **69.2708%**;
- median destination KWAR: **16.6667%**;
- transfer gate: **FAIL**.

### S2 → S3

- source thresholds unavailable: 33/36 cells;
- transferred/evaluated cells: 3;
- median destination UFIR: **36.8056%**;
- median destination KCAR: **34.7222%**;
- median destination KWAR: **12.5%**;
- transfer gate: **FAIL**.

The transfer hypothesis is therefore not supported.

A useful distinction emerging from this result is:

> **Calibrated confidence ≠ transferable confidence.**

A threshold that constrains false matches in one declared synthetic population did not remain equivalently controlled when transferred to another.

## Aggregate classification

The frozen result is `CONTEXT_DEPENDENT_OPEN_SET_CONTROL` because:

- all controls and scorer-parity checks passed;
- the positive `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX` gate cannot pass with 95 calibration-infeasible cells and failed transfer;
- the frozen matrix-wide `FALSE_ATTRIBUTION_RISK_OBSERVED` trigger was not reached under its predeclared thresholds;
- nevertheless, cell-level false attribution and high-score false attribution are present and must remain visible.

The absence of the formal matrix-wide risk label must **not** be interpreted as absence of false-attribution risk. That label has a specific frozen aggregate threshold; it is separate from the observed cell-level events.

## Determinism and evidence

Two independent complete executions from the exact candidate bytes produced byte-identical 223,416-byte sorted compact JSON results.

SHA-256:

`8e0d60322528d44eccf42801caaf5af24e48848d6b75e875b23a59f0a9feca43`

All C1–C7 controls passed. Historical scorer parity passed across all 3 scenarios × 3 artifact states × 4 policies.

A result-level audit identified one evidence-retention defect after the computation: the initial aggregate package did not retain every protocol-required per-artifact raw score row. The scorer, thresholds and result were not changed. A separate deterministic raw-evidence exporter was added and reproduced twice.

The raw evidence now retains **44,928 per-artifact records**:

- S1: 10,368;
- S2: 13,824;
- S3: 20,736.

The complete evidence bundle is identified by SHA-256:

`baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

See `RAW_EVIDENCE-v0.8.json` for scenario-level archive hashes and storage provenance.

## Post-hoc descriptive note

This note is descriptive only and does not alter any predeclared gate.

Because N1/N2 fall back to N0 when provenance is absent, some declared cells are computationally duplicate after provenance removal. Across the 108 declared cells there are 60 effective distinct mode behaviors under that equivalence, with 13 feasible and 47 infeasible.

The declared 108-cell matrix remains the canonical denominator because its dimensions and gates were frozen before execution.

## What v0.8 supports

Within this synthetic benchmark:

1. an unrepresented source can be accepted as a represented synthetic person;
2. some false matches can have scores comparable to ordinary accepted true matches;
3. abstention can reduce forced-choice false attribution in some contexts without eliminating useful known-case attribution;
4. that tradeoff is not broadly feasible across the declared matrix;
5. candidate narrowing can either improve or worsen the privacy/usefulness tradeoff depending on context;
6. thresholds calibrated in one population did not transfer safely under the declared transfer gates.

## What v0.8 does not establish

v0.8 does not establish:

- that any deployed watermark identifies a real person;
- that any named AI provider performs this attribution chain;
- access to provider logs or user accounts;
- real-user re-identification capability;
- a real-world false-accusation prevalence;
- anonymity after rejection;
- authorship, ownership, responsibility, guilt or intent;
- legal or operational authority to resolve identity;
- a universal attribution or privacy law.

The experiment remains synthetic evidence about compositional attribution mechanics and open-set failure modes.
