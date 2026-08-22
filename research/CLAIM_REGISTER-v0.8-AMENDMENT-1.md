# Claim Register v0.8 — DDC Amendment 1

**Status:** normative pre-result claim amendment  
**Base claim register:** `research/CLAIM_REGISTER-v0.8-PREDECLARED.md`  
**Base protocol commit:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Protocol amendment commit:** `bc1422d89cb1c5faab77fb708a48575db65d10e9`  
**Research scope:** synthetic-only  
**Result status:** no v0.8 implementation/reference result existed when this amendment was committed

This file narrows claim promotion rules identified as ambiguous during the full DDC audit. It does not weaken the original nonclaims.

## C8.3 amendment — provenance-assisted narrowing

A reproducible N1/N2 versus N0 difference may support only a bounded synthetic statement about candidate filtering under the declared harness.

Any interpretation must report together:

- UFIR difference;
- KCAR difference;
- KWAR difference;
- true-person filter-exclusion difference;
- candidate-count difference.

A change in accepted attribution caused solely by candidate exclusion must not be described as stronger identity evidence.

## C8.4 amendment — abstention effectiveness

Primary open-set acceptance requires at least two surviving candidates. Zero- and single-candidate cases are abstentions in the primary metric and remain separate narrowing diagnostics.

A reduction in forced-choice false attribution may support C8.4 only together with the frozen known-case utility/error measures. Reject-all or comparator-removal behavior is not open-set control.

## C8.5 amendment — threshold transfer

Threshold calibration may be described as transfer-supported only if **both** frozen transfer pairs satisfy all of:

- median destination UFIR <= 10%;
- median destination KCAR >= 30%;
- median destination KWAR <= 10%.

Low transferred UFIR produced by near-total rejection is not transfer success.

## C8.6 amendment — positive aggregate result

`OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX` is permitted only if:

1. every original positive-control condition is satisfied;
2. both transfer pairs satisfy the amended transfer-usefulness gate;
3. no `FALSE_ATTRIBUTION_RISK_OBSERVED` condition is triggered;
4. all controls, including Amendment-1 controls C5-C7, pass.

The label remains a bounded synthetic benchmark result, not identity proof, anonymity, operational safety certification, or production authorization.

## C8.7 amendment — false-attribution aggregate result

`FALSE_ATTRIBUTION_RISK_OBSERVED` takes precedence over a positive aggregate label when controls pass and any frozen risk trigger is satisfied.

The amended risk triggers are:

- any core cell UFIR >= 20%; or
- at least 20% of core cells UFIR >= 10%; or
- at least 10% of core cells HS-UFIR >= 5%.

A single retained false-attribution event may still support the narrow existential C8.2 statement, but a single event does not by itself establish the aggregate risk label unless one of these predeclared matrix gates is met.

## C8.9 — Person-level exposure is distinct from artifact-level error

**Maturity before experiment:** derived methodological statement.  
**Permitted interpretation:** repeated artifacts from one synthetic person are correlated observations; v0.8 therefore reports UPER and per-person error/acceptance distributions in addition to artifact-level rates.  
**Not permitted:** treating artifact counts as independent real-world population observations.

## C8.10 — Candidate reduction is not evidence creation

**Maturity before experiment:** derived DDC statement.  
**Permitted interpretation:** filtering can change the comparison set and therefore the decision surface without adding new identity evidence.  
**Not permitted:** describing a larger score margin created by removal of comparators as stronger provenance or identity proof.

## Aggregate classification order

The only permitted aggregate classification order is:

1. `CONTROL_FAILED`;
2. `FALSE_ATTRIBUTION_RISK_OBSERVED`;
3. `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`;
4. `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`.

Exactly one aggregate label may be emitted.

## Standing nonclaims retained

All nonclaims in the base claim register remain in force, including:

- no deployed-provider identity claim;
- no real-user re-identification capability claim;
- no provider-log access claim;
- no authorship/ownership/responsibility/guilt claim;
- no legal authority claim;
- no anonymity claim;
- no real-world prevalence estimate;
- no promotion of correlation into authority.