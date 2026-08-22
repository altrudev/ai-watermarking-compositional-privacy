# Claim Register v0.8 — Predeclared Open-Set Attribution / False-Attribution Study

**Status:** pre-result claim boundary  
**Protocol:** `research/TEST_PLAN-v0.8.md`  
**Research scope:** synthetic-only

This register is committed before v0.8 implementation/reference results. It constrains what later evidence may be said to establish.

## C8.1 — Closed-set top-1 success does not establish open-set reliability

**Maturity before experiment:** derived methodological statement.  
**Permitted interpretation:** A closed-set matcher always operates under the assumption that the true source is represented; v0.8 separately tests unknown-source rejection.  
**Not permitted:** claiming any specific false-attribution rate before execution.

## C8.2 — An unknown synthetic source can be falsely assigned to a represented synthetic person

**Maturity before experiment:** hypothesis.  
**Promotion rule:** May be marked experimentally supported only if the frozen v0.8 acceptance rule produces one or more retained U-test false-attribution events and all leakage/parity/negative controls pass.  
**Boundary:** synthetic benchmark only.

## C8.3 — Provenance-assisted candidate narrowing can alter false-attribution risk

**Maturity before experiment:** hypothesis.  
**Promotion rule:** May be marked experimentally supported only when N1/N2 produce a reproducible holdout UFIR difference from N0 under otherwise identical scenario/state/policy conditions. Direction must be reported from evidence; it is not pre-assumed.  
**Not permitted:** claiming provenance necessarily increases or decreases false attribution.

## C8.4 — Abstention can reduce forced-choice false attribution without collapsing useful known-case attribution

**Maturity before experiment:** hypothesis.  
**Promotion rule:** Requires the frozen calibration procedure, separate U-test evaluation, and reported KCAR/KWAR tradeoff. Reject-everything behavior cannot satisfy this claim.  
**Boundary:** declared synthetic matrix only.

## C8.5 — Threshold calibration transfers across changed populations

**Maturity before experiment:** hypothesis.  
**Promotion rule:** Requires the predeclared S1→S2 and S2→S3 transfer tests. Re-calibration in the destination does not count as transfer evidence.

## C8.6 — `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`

**Maturity before experiment:** possible aggregate result label, not a claim.  
**Required evidence:** every condition in T9 of the predeclared protocol must pass.  
**Not permitted:** translating this label into anonymity, real-world safety, or production authorization.

## C8.7 — `FALSE_ATTRIBUTION_RISK_OBSERVED`

**Maturity before experiment:** possible aggregate result label, not a claim.  
**Required evidence:** one of the frozen T9 false-attribution thresholds must be satisfied after all controls/parity pass.  
**Interpretation:** evidence of false attribution in the declared synthetic model.  
**Not permitted:** estimating real false-accusation prevalence from this label.

## C8.8 — `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`

**Maturity before experiment:** possible aggregate result label, not a claim.  
**Interpretation:** neither the broad control gate nor the broad false-attribution-risk gate is satisfied; cell-level conditions determine the result. All adverse cells remain reportable.

## Explicit nonclaims

v0.8 does **not** claim or attempt to establish:

- that any deployed watermark identifies a person;
- that Anthropic, OpenAI, Google, LinkedIn, or another provider performs this attribution chain;
- access to or knowledge of provider logs;
- real-user re-identification capability;
- authorship, ownership, responsibility, guilt, or intent;
- legal authority to obtain identity data;
- anonymity after an abstention decision;
- that watermark removal guarantees privacy;
- that provenance-assisted narrowing always increases false attribution;
- that synthetic false-attribution rates are population estimates for real systems.

## Standing DDC distinctions

- **Detection ≠ Provenance ≠ Attribution ≠ Identity Resolution ≠ Authority.**
- **Best match ≠ sufficient match.**
- **Confidence ≠ identity proof.**
- **Candidate membership ≠ identity truth.**
- **Candidate narrowing ≠ authority.**
- **Unknown rejection ≠ anonymity.**
- **Synthetic evidence ≠ deployed-provider evidence.**
- **Experiment result ≠ validated invariant.**
- **Correlation ≠ authorization.**

## Publication rule

Whatever v0.8 produces, the result must be published or documented with its adverse cells intact. A negative, mixed, or falsifying outcome is not permission to alter the frozen thresholds, populations, transformations, evidence policies, or narrowing rules after the reference run begins.
