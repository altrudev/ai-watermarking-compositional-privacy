# v0.8 Open-Set Study — Pre-Reference Implementation Specification

**Status:** normative implementation detail, frozen before canonical reference execution  
**Governing base protocol:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Governing amended/audited head:** `0a3f970beb200be97e04b9bc86b56584021e040a`  
**Research scope:** synthetic-only  
**Reference-result status at commit time:** no canonical v0.8 reference result exists

This specification resolves implementation choices that are not outcome-dependent. It does not alter thresholds, scenarios, evidence policies, artifact states, narrowing modes, aggregate gates, or the synthetic-only boundary.

## I1 — Person-to-cohort assignment

The scenario table freezes K/U-cal/U-test cohort sizes but not which generated person indices occupy each cohort. The canonical synthetic generator uses person index when selecting signatures, transitions, topics and provider/model patterns. Contiguous assignment could therefore create an avoidable cohort-index confound.

For each scenario, after generating the complete declared synthetic population, unique synthetic person IDs are sorted by the raw SHA-256 digest of:

`scenario_name + "|" + person_id`

The first declared K count becomes the known cohort, the next declared U-cal count becomes calibration-unknown, and the remaining declared U-test count becomes holdout-unknown.

The assignment uses no artifact text, score, attribution outcome, threshold, or holdout result. It is deterministic and frozen before reference execution.

## I2 — Unknown artifact use

All generations/artifacts belonging to U-cal persons are used for unknown threshold calibration. All generations/artifacts belonging to U-test persons are used for unknown holdout evaluation. Known artifacts remain split exactly by Amendment A1: `-gen-0` calibration and `-gen-1` holdout.

## I3 — Equal-prior accepted precision

The base protocol asks for accepted precision under an evaluation mixture with equal counts of known and unknown artifacts. Rather than outcome-dependent subsampling, v0.8 computes the mathematically equivalent equal-prior rate:

`KCAR / (KCAR + KWAR + UFIR)`

when the denominator is non-zero. If the denominator is zero, accepted precision is defined as 1.0 while the accompanying KCAR/KWAR/UFIR/KRR values make the reject-all state explicit. Reject-all behavior cannot satisfy the positive aggregate gate because KCAR requirements remain binding.

## I4 — Source-infeasible transfer cells

If a source scenario cell is `CALIBRATION_INFEASIBLE`, there is no source threshold to transfer. The matching transfer cell is recorded as `SOURCE_CALIBRATION_INFEASIBLE`. A transfer-pair summary is not acceptable if any matching source threshold is unavailable.

## I5 — Truth-label isolation

`Artifact.target_generation_id` is retained solely as experiment truth/provenance for evaluation. Candidate filtering and similarity scoring must not use it. The scorer cache key deliberately excludes `target_generation_id`; changing only the stored truth label must leave the complete candidate ranking byte-for-byte equivalent.

## I6 — Reference evidence additions

The canonical reference package must retain, in addition to the base protocol and Amendment 1 requirements:

- exact K/U-cal/U-test synthetic person-ID lists and deterministic digests for every scenario;
- candidate generation count for every scenario;
- forced-choice known person and generation top-1 rates;
- accepted wrong-known attribution events in synthetic-ID form;
- explicit N1/N2 versus N0 narrowing differentials;
- source-threshold-unavailable counts in transfer summaries.

## DDC boundary

These implementation choices create no new authority, real-data access, identity-resolution capability, provider access, production detector, external execution boundary or privilege. They exist only to make the predeclared synthetic study deterministic, auditable and less vulnerable to accidental structural bias.
