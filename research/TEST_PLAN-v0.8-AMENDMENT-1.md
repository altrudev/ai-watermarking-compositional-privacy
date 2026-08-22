# v0.8 Test Plan — DDC Amendment 1

**Status:** normative pre-execution amendment  
**Applies to:** `research/TEST_PLAN-v0.8.md`  
**Base protocol commit:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Research scope:** synthetic-only  
**Result status at amendment time:** no v0.8 implementation/reference result exists

This amendment is additive. It does not rewrite the original predeclared protocol. It closes methodological ambiguities identified by the full DDC audit before any v0.8 result is generated. Where this amendment conflicts with the base protocol, this amendment governs.

## A1 — Deterministic known-artifact calibration/holdout split

The base protocol names known calibration and known holdout artifacts but does not define their split. v0.8 therefore freezes the following split before implementation:

- candidate database: **all generations belonging to K**;
- known calibration artifacts: generations whose `generation_id` ends in `-gen-0`;
- known holdout artifacts: generations whose `generation_id` ends in `-gen-1`.

Under the historical generator this yields exactly six calibration and six holdout generations per known synthetic person. The implementation must assert that every K person has at least one artifact in both partitions and that no artifact appears in both. Failure emits `CONTROL_FAILED`; the split may not be repaired after results by moving artifacts.

U-cal and U-test remain person-disjoint cohorts as defined in the base protocol.

## A2 — Provenance presence and narrowing semantics

The canonical `Artifact` schema contains `provider_hint` and `watermark_family`; it does not contain a separate model field. For v0.8:

- **complete simulated provenance** means both `provider_hint` and `watermark_family` are non-null and `watermark_family` begins with `provider_hint + ":"`;
- **absent provenance** means both fields are null;
- exactly one field present, or an inconsistent provider/watermark pair, is a synthetic harness inconsistency and emits `CONTROL_FAILED`.

N1 `provider_model_narrowed` therefore matches candidates on both:

- `candidate.provider == artifact.provider_hint`; and
- `candidate.watermark_family == artifact.watermark_family`.

The watermark-family value carries the synthetic provider/model pair. No separate model value may be invented from outside the canonical harness.

N2 applies the same complete-provenance rule and then the predeclared time window. When provenance is absent, N1/N2 fall back to N0 exactly as already declared.

## A3 — Zero- and single-candidate behavior

The base protocol defined a one-candidate margin against an implicit zero comparator. That can manufacture a large margin merely because narrowing removed every competing candidate.

Primary open-set acceptance is amended as follows:

- candidate count = 0 → `UNKNOWN / ABSTAIN`, reason `NO_CANDIDATE`;
- candidate count = 1 → `UNKNOWN / ABSTAIN`, reason `INSUFFICIENT_COMPARATORS`;
- candidate count >= 2 → apply the frozen `tau_score` and `tau_margin` rule.

For count 0 or 1, retain raw candidate count, top-1 score when present, and the forced-choice diagnostic outcome. These cases remain evidence about narrowing behavior, but they cannot be counted as accepted person attribution in the primary safety-control metric.

This amendment prevents candidate reduction itself from being treated as evidence strength.

## A4 — Filter-exclusion evidence

Every known-artifact result must additionally retain:

- `target_person_present_after_filter`;
- `target_generation_present_after_filter`;
- `filter_excluded_true_person`;
- `filter_excluded_true_generation`.

Known-case failure must therefore be separable into:

1. candidate-filter exclusion;
2. scoring/ranking error;
3. threshold rejection.

The provenance/narrowing differential must report true-person filter-exclusion rate in addition to KCAR/UFIR/KWAR/precision/candidate count.

## A5 — High-score false-attribution reference

`HIGH_SCORE_FALSE_ATTRIBUTION` is defined using **correctly accepted known calibration artifacts in the same scenario × artifact_state × evidence_policy × narrowing cell**.

The reference value is the median accepted top-1 score of those correctly accepted known calibration artifacts and is frozen before U-test evaluation.

A feasible calibration cell must have at least one correctly accepted known calibration artifact; otherwise it is `CALIBRATION_INFEASIBLE`.

Add:

`HS-UFIR = high-score accepted false U-test attributions / all U-test artifacts in the cell`.

The prior aggregate trigger based on the fraction of already-false events is replaced because a single false event could otherwise create a 100% high-score fraction. The high-score aggregate risk trigger is now:

- at least **10% of core cells** have `HS-UFIR >= 5%`.

All individual high-score false events remain retained regardless of whether this aggregate trigger is reached.

## A6 — Transfer must preserve usefulness as well as rejection

A transferred threshold must not be considered successful merely because it rejects everything in the destination population.

For each frozen transfer pair, across matching destination cells, report medians for:

- UFIR;
- KCAR;
- KWAR.

A transfer pair is considered acceptable only when all are true:

- median destination UFIR <= **10%**;
- median destination KCAR >= **30%**;
- median destination KWAR <= **10%**.

`OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX` requires **both** S1→S2 and S2→S3 to satisfy all three transfer conditions.

Claim C8.5 may be promoted only under the same transfer criteria.

## A7 — Aggregate classification precedence

Aggregate result labels are mutually exclusive and evaluated in this exact order:

1. `CONTROL_FAILED`;
2. `FALSE_ATTRIBUTION_RISK_OBSERVED`;
3. `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`;
4. `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`.

Therefore a matrix that satisfies the broad control metrics but also triggers a frozen false-attribution-risk condition must be labeled `FALSE_ATTRIBUTION_RISK_OBSERVED`, not the positive control label.

The false-attribution-risk conditions are:

- any core cell has UFIR >= 20%; or
- at least 20% of core cells have UFIR >= 10%; or
- at least 10% of core cells have HS-UFIR >= 5%.

## A8 — Person-level exposure metrics

Artifact-level rates are retained, but repeated artifacts from the same synthetic person are not independent observations.

For every core cell additionally report:

- **UPER** — unknown-person exposure rate: fraction of U-test persons with at least one accepted false attribution;
- median per-person UFIR across U-test persons;
- maximum per-person UFIR across U-test persons;
- median per-person KCAR across known holdout persons;
- minimum per-person KCAR across known holdout persons.

These are descriptive synthetic metrics. No artifact-level or cell-level percentage may be presented as an estimate of real-world population prevalence.

The percentages of the 108 core cells meeting a gate are **design-surface coverage measures**, not independent-trial probabilities or statistical significance tests.

## A9 — Threshold-calibration provenance

For every core cell retain a machine-readable calibration record containing:

- counts of known calibration and U-cal artifacts;
- every feasible threshold pair or an exact deterministic digest of the feasible set;
- selected `tau_score` and `tau_margin`;
- calibration UFIR/KCAR/KWAR for the selected pair;
- the frozen high-score reference median;
- calibration candidate-count distribution;
- calibration feasibility status.

U-test and known holdout outcomes must not appear in this calibration record.

## A10 — Protocol identity binding

The v0.8 implementation and tests must embed and report both:

- base protocol commit `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`;
- the canonical commit containing this amendment, once merged/fast-forwarded before implementation begins.

Tests must fail if the declared protocol identities do not match the canonical pre-result lineage used for the reference run.

Historical v0.1–v0.7 experiment/result files remain immutable inputs.

## A11 — Additional negative controls

Add the following controls to T8:

### C5 — single-candidate comparator control

Construct a case where filtering leaves exactly one candidate. The primary open-set decision must be `UNKNOWN / ABSTAIN` with `INSUFFICIENT_COMPARATORS`, irrespective of the candidate's score.

### C6 — partial-provenance fail-closed control

Construct an artifact with exactly one of `provider_hint` / `watermark_family` present. Candidate narrowing must not silently fall back to global search; the control must emit `CONTROL_FAILED`.

### C7 — partition immutability control

Verify that all K `-gen-0` artifacts are calibration-only and all K `-gen-1` artifacts are holdout-only, with no threshold-selection access to the latter.

## A12 — Updated execution gate

No v0.8 implementation/reference execution is valid unless it implements the base protocol **plus this amendment** and passes the full DDC audit closure record.

This amendment changes no real-data boundary, privilege, production authority, or external execution capability.