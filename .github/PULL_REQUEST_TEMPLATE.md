# DDC Pull Request Checklist

## Authority and scope

- [ ] Root/maintainer authority for this transition is identified.
- [ ] This PR does not infer new authority from data, credentials, branch access, or prior execution.
- [ ] Research scope is stated (`synthetic-only` unless separately authorized otherwise).
- [ ] Real-person data, provider logs, private conversations, credentials, or production identity-resolution capability are not introduced unless an explicit separately governed transition authorizes them.

## Lineage

- [ ] Base commit is recorded and current.
- [ ] Governing protocol/specification is identified where applicable.
- [ ] Historical experiment/result files are not rewritten to make later evidence cleaner.
- [ ] New result files identify exact candidate/canonical source lineage.
- [ ] Negative, failed, or narrowing evidence is retained.

## Rules before results

For experiment implementation/result PRs:

- [ ] Population, evidence channels, transforms, partitions, metrics, thresholds, controls, failure gates, and claim boundaries were frozen before canonical execution.
- [ ] Post-result tuning is either absent or explicitly separated into a new future protocol.
- [ ] Calibration data is separated from holdout/test data where required.

## Verification

- [ ] Python/runtime version is recorded.
- [ ] Exact test command and result count are recorded.
- [ ] Result-critical source/blob identities match the bytes tested.
- [ ] Deterministic replay is recorded where required.
- [ ] External evidence artifacts have cryptographic identities and custody records.

## Claim maturity

- [ ] Synthetic evidence is not described as deployed-provider evidence.
- [ ] Detection is not promoted to provenance, attribution, identity, authorship, ownership, responsibility, or authority without separate evidence/authority.
- [ ] Local findings are not promoted to broad invariants when replication does not support that step.
- [ ] Public summaries preserve material adverse results and denominator context.

## Repository governance

- [ ] `main` is treated as the sole active canonical head.
- [ ] This branch is temporary or explicitly `archive/` noncanonical history.
- [ ] Base/head drift is rechecked immediately before merge.
- [ ] No GitHub Actions dependency is introduced.

**Standing rule:** Published research object != active research program != protocol != implementation != tested result != validated invariant != production authority.
