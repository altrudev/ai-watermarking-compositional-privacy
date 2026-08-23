# Research Program Index

This directory contains the governed experimental lineage for the AI watermarking compositional-privacy research program.

## Status map

| Phase | Status | Canonical interpretation |
|---|---|---|
| v0.1 | completed | synthetic abstract unlinkability benchmark |
| v0.2 | completed | synthetic-text linkage/unlinkability benchmark |
| v0.3 | completed | transformation-chain persistence; non-monotonic privacy result |
| v0.4 | completed | transformation path-dependence result |
| v0.5 | completed | robustness matrix for path dependence |
| v0.6 | completed | strong local pairwise non-commutativity mechanism result |
| v0.7 | completed | broader replication failed; local v0.6 result not promoted |
| v0.8 | completed | open-set / false-attribution control is context-dependent in the declared synthetic matrix |
| v0.9 candidate | question scope only | no protocol, implementation, or result authorization |

## Current lineage

- [`EXPERIMENT_LINEAGE-v0.1-v0.8.json`](EXPERIMENT_LINEAGE-v0.1-v0.8.json) — current machine-readable lineage.
- [`EXPERIMENT_LINEAGE-v0.1-v0.5.json`](EXPERIMENT_LINEAGE-v0.1-v0.5.json) — historical lineage snapshot retained unchanged.

Historical lineage files are snapshots, not mutable aliases.

Canonical v0.8 experiment commit: `7cbb6d8b3e76fdd7a3bbce6db92d34442d025c5e`.

## Research governance

- [`RESEARCH_METHOD.md`](RESEARCH_METHOD.md) — DDC-governed research process.
- [`EXTERNAL_REVIEW_LOG.md`](EXTERNAL_REVIEW_LOG.md) — material external criticism recorded as hypothesis-generating input, not evidence.
- [`DDC_AUDIT-v0.1-v0.5.md`](DDC_AUDIT-v0.1-v0.5.md) — historical program audit.
- [`DDC_FULL_AUDIT-v0.8-PROTOCOL.md`](DDC_FULL_AUDIT-v0.8-PROTOCOL.md) — full v0.8 pre-execution protocol audit.
- [`DDC_IMPLEMENTATION_AUDIT-v0.8-PRE-REFERENCE.md`](DDC_IMPLEMENTATION_AUDIT-v0.8-PRE-REFERENCE.md) — exact implementation gate before reference execution.
- [`DDC_RESULT_AUDIT-v0.8-FINAL.md`](DDC_RESULT_AUDIT-v0.8-FINAL.md) — final result-level DDC audit and clean-merge authorization.
- [`DDC_FULL_AUDIT-REPOSITORY-2026-08-22.md`](DDC_FULL_AUDIT-REPOSITORY-2026-08-22.md) — repository-level authority, lineage, evidence, reproducibility, and governance audit after v0.8 closure.
- [`DDC_LICENSE_TRANSITION-2026-08-22.md`](DDC_LICENSE_TRANSITION-2026-08-22.md) — governed licensing transition record.

## Completed governed program — v0.8

The v0.8 open-set / false-attribution program is governed and recorded by:

- [`TEST_PLAN-v0.8.md`](TEST_PLAN-v0.8.md)
- [`TEST_PLAN-v0.8-AMENDMENT-1.md`](TEST_PLAN-v0.8-AMENDMENT-1.md)
- [`CLAIM_REGISTER-v0.8-PREDECLARED.md`](CLAIM_REGISTER-v0.8-PREDECLARED.md)
- [`CLAIM_REGISTER-v0.8-AMENDMENT-1.md`](CLAIM_REGISTER-v0.8-AMENDMENT-1.md)
- [`CLAIM_REGISTER-v0.8.md`](CLAIM_REGISTER-v0.8.md)
- [`IMPLEMENTATION_SPEC-v0.8.md`](IMPLEMENTATION_SPEC-v0.8.md)
- [`RESULTS-v0.8.md`](RESULTS-v0.8.md)
- [`VALIDATION-v0.8.md`](VALIDATION-v0.8.md)
- [`RAW_EVIDENCE-v0.8.json`](RAW_EVIDENCE-v0.8.json)
- [`DDC_FULL_AUDIT-v0.8-PROTOCOL.md`](DDC_FULL_AUDIT-v0.8-PROTOCOL.md)
- [`DDC_IMPLEMENTATION_AUDIT-v0.8-PRE-REFERENCE.md`](DDC_IMPLEMENTATION_AUDIT-v0.8-PRE-REFERENCE.md)
- [`DDC_RESULT_AUDIT-v0.8-FINAL.md`](DDC_RESULT_AUDIT-v0.8-FINAL.md)
- [`../docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json`](../docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json)

Frozen v0.8 classification: **`CONTEXT_DEPENDENT_OPEN_SET_CONTROL`**.

The declared 108-cell matrix produced 13 calibration-feasible cells and 95 calibration-infeasible cells. Both predeclared cross-population threshold-transfer pairs failed. The complete deterministic reference object reproduced byte-identically with SHA-256 `8e0d60322528d44eccf42801caaf5af24e48848d6b75e875b23a59f0a9feca43`.

These findings remain synthetic experimental evidence. Calibration infeasibility is not anonymity, observed synthetic false attribution is not real-world accusation prevalence, and successful matching does not create identity-resolution authority.

## Next research question — not yet a protocol

[`ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md`](ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md) records candidate questions around marginal provenance contribution, key scope, and architectural auditability.

v0.8 is closed. The v0.9 record remains question-scope only and does **not** authorize a v0.9 protocol, implementation, execution, real-person attribution research, or production identity-resolution capability.

## Licensing

Research prose in this directory is licensed under **CC BY-NC 4.0** unless a file states otherwise. Machine-readable synthetic evidence and result data in designated JSON / compressed-JSON files are licensed under **CC BY 4.0**.

The authoritative scope map is [`../LICENSING.md`](../LICENSING.md). Licensing does not change the maturity, evidentiary meaning, or authority of any research result.

## Standing boundary

**Published research object != active research program != protocol != implementation != tested result != validated invariant != production authority.**

Synthetic findings remain synthetic. External criticism can refine the next test, but it does not become experimental evidence merely because it is persuasive.
