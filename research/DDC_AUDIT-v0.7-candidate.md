# DDC Audit — v0.7 Cross-Family Replication Candidate

**Status:** pre-merge candidate audit  
**Protocol:** `786ebb3d097d999e15f72cbfce536e59566206a1`  
**Canonical predecessor:** `c29b40db9000d3e0a49c2c25fadab215d3084480`

## Authority and scope

The v0.7 continuation is authorized only inside the synthetic research envelope established by H/R Native's `RESEARCH_CONTINUATION-20260820` program.

No real people, real accounts, provider logs, private conversations, scraped identity datasets, production watermark detectors, proprietary model APIs, production credentials, destructive operations, or new authority capabilities are introduced by this candidate.

## DDC distinctions preserved

- Published research object ≠ active research program ≠ experiment ≠ experimental result ≠ validated invariant.
- Privacy transformation ≠ privacy evidence.
- Failed re-identification ≠ proven anonymity.
- Synthetic benchmark mechanism ≠ deployed-provider mechanism.
- Replication failure ≠ permission to tune the protocol after observing results.
- Experimental evidence ≠ H/R Native constitutional authority.

## Rules-before-results check

PASS.

The v0.7 protocol and thresholds were merged separately at `786ebb3d097d999e15f72cbfce536e59566206a1` before the v0.7 implementation/reference execution branch was produced.

The candidate implementation embeds the exact protocol commit and the predeclared claim thresholds:

- holdout predictive: `r >= 0.70`;
- transfer supported: `r >= 0.50`;
- replicated aggregate: `H >= 42`, `T >= 15`, required medians and coverage;
- not replicated: `H < 30` or `T < 9` after controls/parity pass.

No post-result threshold change is authorized.

## Candidate architecture review

The implementation is additive relative to the canonical predecessor. Historical v0.1-v0.6 experiment/result files are not rewritten by the branch.

The candidate uses:

- two new four-transform families;
- five frozen adversary policies;
- six frozen population/seed scenarios;
- deterministic SHA-256 calibration/holdout partitioning;
- calibration-only pairwise estimation;
- holdout-only primary full-path evaluation;
- three frozen cross-scenario transfer pairs;
- historical scorer parity;
- a multi-policy optimized scorer with explicit parity checks;
- commuting lowercase/whitespace controls.

## Finding DDC-v0.7-01 — incomplete T2/T8 pairwise evidence record

**Severity:** merge-blocking evidence defect, not a scoring defect.  
**Classification:** safe additive repair inside the authorized protocol.

The initial candidate's `pairwise_effects_all` record included text-difference fraction, metadata equality, policy-level person/generation order effects, and the directional effect map used by the predictor. It did **not** record all predeclared T2 evidence fields:

- lexical feature divergence;
- semantic feature divergence;
- style feature divergence;
- single-channel person-attribution deltas;
- largest changed evidence channel.

This meant the headline replication result could be computed, but the package did not yet satisfy the complete evidence contract declared before execution.

### Repair

An additive module, `lab/cross_family_replication_diagnostics.py`, now computes those missing fields from the same frozen transformations, calibration partitions, historical feature vectorizers, single-signal policies, and scorer semantics.

The repair intentionally does **not** modify:

- the v0.7 adversary policies;
- scenario definitions;
- partition rule;
- pairwise predictor;
- full-path observed outcomes;
- transfer calculation;
- aggregate claim thresholds;
- historical experiment files.

Therefore the repair may add evidence but may not change the declared replication classification by construction.

A focused diagnostics test file was also added. This repair is not considered verification-complete until those exact final candidate bytes are executed and the resulting diagnostics are included in the reference evidence package.

## Negative-result preservation

The previously generated exact-candidate reference matrix produced `MECHANISM_NOT_REPLICATED` with:

- holdout predictive cells: **5 / 60**;
- transfer-supported cells: **3 / 30**;
- median holdout Pearson `r`: **0.0**;
- median transfer Pearson `r`: **0.0**;
- family/scenario coverage: **not satisfied**;
- policy-transfer coverage: **not satisfied**;
- required controls/parity: **passed**.

This result must remain adverse evidence. The evidence-layer repair above is not authority to alter transformations, weights, seeds, thresholds, partitions, or claim interpretation to obtain a more favorable outcome.

## Remaining merge gates

The candidate is **not yet merge-authorized** at this audit checkpoint. Before merge it must still demonstrate on the final exact bytes:

1. Python compilation PASS;
2. original v0.7 focused regression suite PASS;
3. new diagnostics regression suite PASS;
4. historical scorer parity PASS in every scenario;
5. multi-policy scorer parity PASS in every scenario;
6. all commuting controls PASS;
7. complete 60-cell holdout matrix retained;
8. complete 30-cell transfer matrix retained;
9. complete T2 pairwise diagnostic set retained;
10. two full final-candidate reference executions serialize byte-identically after key sorting;
11. exact tested Git blobs equal the proposed merge blobs;
12. branch remains additive over the frozen predecessor and protocol.

## Current maturity

- Protocol designed/predeclared: **yes**.
- Candidate implementation: **yes**.
- Initial scorer/result execution: **yes, negative replication result preserved**.
- Final evidence repair implemented: **yes**.
- Final exact-byte verification after evidence repair: **pending**.
- Merge-authorized: **no, pending final verification**.
- Real-world validated: **no**.
- Production-authorized: **no**.
