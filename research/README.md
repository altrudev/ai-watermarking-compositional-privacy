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
| v0.8 | pre-execution | protocol audited; implementation allowed; canonical reference run not yet authorized |
| v0.9 candidate | question scope only | no protocol, implementation, or result authorization |

## Current lineage

- [`EXPERIMENT_LINEAGE-v0.1-v0.8.json`](EXPERIMENT_LINEAGE-v0.1-v0.8.json) — current machine-readable lineage.
- [`EXPERIMENT_LINEAGE-v0.1-v0.5.json`](EXPERIMENT_LINEAGE-v0.1-v0.5.json) — historical lineage snapshot retained unchanged.

Historical lineage files are snapshots, not mutable aliases.

## Research governance

- [`RESEARCH_METHOD.md`](RESEARCH_METHOD.md) — DDC-governed research process.
- [`EXTERNAL_REVIEW_LOG.md`](EXTERNAL_REVIEW_LOG.md) — material external criticism recorded as hypothesis-generating input, not evidence.
- [`DDC_AUDIT-v0.1-v0.5.md`](DDC_AUDIT-v0.1-v0.5.md) — historical program audit.
- [`DDC_FULL_AUDIT-v0.8-PROTOCOL.md`](DDC_FULL_AUDIT-v0.8-PROTOCOL.md) — full v0.8 pre-execution audit.
- [`DDC_LICENSE_TRANSITION-2026-08-22.md`](DDC_LICENSE_TRANSITION-2026-08-22.md) — governed licensing transition record.

## Current governed program — v0.8

The v0.8 open-set / false-attribution program is governed by:

- [`TEST_PLAN-v0.8.md`](TEST_PLAN-v0.8.md)
- [`TEST_PLAN-v0.8-AMENDMENT-1.md`](TEST_PLAN-v0.8-AMENDMENT-1.md)
- [`CLAIM_REGISTER-v0.8-PREDECLARED.md`](CLAIM_REGISTER-v0.8-PREDECLARED.md)
- [`CLAIM_REGISTER-v0.8-AMENDMENT-1.md`](CLAIM_REGISTER-v0.8-AMENDMENT-1.md)
- [`DDC_FULL_AUDIT-v0.8-PROTOCOL.md`](DDC_FULL_AUDIT-v0.8-PROTOCOL.md)
- [`../docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json`](../docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json)

The protocol is implementation-authorized, but no canonical v0.8 implementation/reference result is present yet. The reference run remains blocked until the exact implementation candidate passes its own audit gate.

## Next research question — not yet a protocol

[`ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md`](ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md) records the next candidate questions around marginal provenance contribution, key scope, and architectural auditability.

It does not modify v0.8 and does not authorize v0.9 implementation.

## Licensing

Research prose in this directory is licensed under **CC BY-NC 4.0** unless a file states otherwise. Machine-readable synthetic evidence and result data in designated JSON / compressed-JSON files are licensed under **CC BY 4.0**.

The authoritative scope map is [`../LICENSING.md`](../LICENSING.md). Licensing does not change the maturity, evidentiary meaning, or authority of any research result.

## Standing boundary

**Published research object != active research program != protocol != implementation != tested result != validated invariant != production authority.**

Synthetic findings remain synthetic. External criticism can refine the next test, but it does not become experimental evidence merely because it is persuasive.
