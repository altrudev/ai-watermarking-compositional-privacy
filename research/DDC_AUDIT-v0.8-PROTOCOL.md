# DDC Audit — v0.8 Open-Set / False-Attribution Protocol

**Status:** protocol-only pre-execution audit  
**Repository base:** `667672953250b0e1fefda7f47a5e832a7acff3ee`

## Governed transition

**Authority:** Root Human Authority instruction: proceed with publication closure and v0.8 protocol design.  
**Intent:** test whether the synthetic attribution layer can abstain when the true person is absent and quantify false attribution under provenance/correlation evidence.  
**Execution boundary:** protocol and claim predeclaration only; no v0.8 implementation or reference results in this transition.  
**Affected state:** additive research planning/evidence files only.  
**Production/identity authority:** unchanged.

## DDC checks

### Need ≠ Authority

PASS. The research need to understand false attribution does not grant access to real identities, provider logs, private conversations, scraped profiles, or production systems.

### Detection ≠ Identity Resolution

PASS. The protocol explicitly separates model/provenance evidence from person attribution and treats candidate narrowing as an analytical operation, not authority.

### Best Match ≠ Sufficient Match

PASS. v0.8 introduces an explicit `UNKNOWN / ABSTAIN` outcome and rejects the closed-set assumption that the highest score must identify someone.

### Calibration ≠ Validation

PASS. U-cal and U-test are person-disjoint. Thresholds may use U-cal but may not use U-test. Transfer tests freeze thresholds across scenarios.

### Reject Everything ≠ Open-Set Success

PASS. The calibration gate requires a minimum known correct-acceptance rate and limits known wrong acceptance; a trivial reject-all rule is infeasible.

### Candidate Narrowing ≠ Authority

PASS. Provider/model/time filtering is synthetic and explicitly does not represent legal or operational authority to access records.

### False Attribution ≠ Real-World Accusation Rate

PASS. The claim register prohibits population-level real-world extrapolation.

### Experiment ≠ Validated Invariant

PASS. Aggregate labels remain bounded to the declared synthetic matrix.

## Pre-result integrity

PASS.

The protocol freezes before implementation/reference results:

- three person-disjoint open-set scenarios;
- three artifact/transformation states;
- four adversary evidence policies;
- three candidate-narrowing modes;
- threshold grids and deterministic selection rule;
- UFIR/KCAR/KWAR/KRR and accepted-precision metrics;
- high-score false-attribution definition;
- negative controls;
- transfer pairs;
- aggregate interpretation thresholds;
- evidence-retention requirements;
- explicit nonclaims.

No observed v0.8 result exists at this checkpoint.

## Residual methodological limitations accepted before execution

1. Synthetic text/person generation cannot establish real-world error prevalence.
2. S1/S2/S3 change population size and seeds together, so pool-size comparisons are robustness observations rather than pure causal estimates.
3. Score/margin thresholding is one declared open-set strategy, not proof it is optimal.
4. Simulated provider/model/watermark labels are abstract provenance channels, not deployed watermark implementations.
5. The experiment tests attribution-layer abstention; it does not yet model the complete artifact → generation → session → account → person authority chain.

These limitations are part of the protocol and may not be removed after results are seen.

## Protocol authorization result

**PASS FOR PREDECLARATION.**

The protocol is inside the authorized synthetic research boundary, introduces no new privilege or real-identity access, and is sufficiently specified to prevent post-result threshold/claim tuning.

This audit authorizes only merging the protocol checkpoint. It does **not** by itself authorize claiming any v0.8 outcome.
