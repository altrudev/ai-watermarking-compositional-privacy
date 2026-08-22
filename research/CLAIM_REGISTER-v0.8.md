# Claim Register v0.8 — Final Experimental Status

**Status:** post-result claim register  
**Scope:** synthetic-only  
**Frozen aggregate result:** `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`

This register applies the predeclared v0.8 claim boundaries to the completed evidence. It does not modify the protocol, thresholds, populations, policies, narrowing modes, transformation states or aggregate gates.

## C8.1 — Closed-set top-1 success does not establish open-set reliability

**Final status:** `SUPPORTED_AS_METHODological_DISTINCTION`.

The v0.8 experiment demonstrates why closed-set ranking and open-set acceptance are different tasks. Unknown-source artifacts can still receive a highest-ranked represented candidate when candidates survive filtering, while open-set acceptance requires an independent sufficiency/abstention decision.

**Permitted statement:** Best match is not sufficient match.

## C8.2 — An unknown synthetic source can be falsely assigned to a represented synthetic person

**Final status:** `EXPERIMENTALLY_SUPPORTED_FOR_DECLARED_SYNTHETIC_BENCHMARK`.

All leakage, parity and negative controls passed, and accepted U-test false-attribution events were retained under the frozen acceptance rule.

Across evaluated cells, 20 unique U-test target generations and 7 unique U-test persons experienced at least one accepted false attribution. Event counts across cells are repeated measures and must not be described as independent real-world accusations.

**Not permitted:** extrapolating a real-person or population false-accusation rate.

## C8.3 — Provenance-assisted candidate narrowing can alter false-attribution risk

**Final status:** `SUPPORTED_WITH_CONTEXT_DEPENDENT_DIRECTION`.

In S1 canonical conditions, provenance/model narrowing reduced UFIR by 9.375 percentage points while increasing KCAR. In S1 timing-heavy conditions, narrowing increased UFIR by 2.083 percentage points and KWAR by 2.083 points while also increasing KCAR.

**Permitted statement:** candidate narrowing changed the privacy/usefulness tradeoff in the declared synthetic benchmark.

**Not permitted:** claiming that narrowing inherently increases or inherently decreases false-attribution risk.

## C8.4 — Abstention can reduce forced-choice false attribution without collapsing useful known-case attribution

**Final status:** `LOCALLY_SUPPORTED_NOT_MATRIX_WIDE`.

Some feasible cells achieved low UFIR with useful KCAR. However only 13/108 declared cells were calibration-feasible, and no transformed-state cell was feasible under the frozen calibration constraints.

**Permitted statement:** the declared abstention procedure worked in limited contexts.

**Not permitted:** saying the procedure establishes broad open-set safety or robust identity rejection.

## C8.5 — Threshold calibration transfers across changed populations

**Final status:** `NOT_SUPPORTED`.

S1→S2 transfer failed with median destination UFIR 21.875%, KCAR 69.2708%, KWAR 16.6667%. S2→S3 failed with median UFIR 36.8056%, KCAR 34.7222%, KWAR 12.5%. Most source cells lacked a transferable threshold because source calibration was infeasible.

**Permitted statement:** calibrated confidence did not transfer reliably under the declared test.

## C8.6 — `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`

**Final status:** `NOT_EMITTED`.

The positive aggregate gate fails because the matrix contains 95 calibration-infeasible cells and both transfer pairs fail, among other unmet requirements.

## C8.7 — `FALSE_ATTRIBUTION_RISK_OBSERVED`

**Final status:** `NOT_EMITTED_AS_FROZEN_MATRIX_WIDE_LABEL`.

The formal aggregate trigger was not reached under its frozen denominator/threshold rules.

This does **not** mean false attribution was absent. Cell-level accepted false attributions and high-score false attributions were observed and are retained. The distinction between a formal aggregate label and observed cell-level events must remain explicit.

## C8.8 — `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`

**Final status:** `EMITTED`.

Controls/parity passed, while neither the positive broad-control gate nor the frozen matrix-wide false-attribution-risk gate was satisfied.

The label must be read together with the dominant adverse fact: **95/108 declared cells were calibration-infeasible.** It is not a shorthand for general safety.

## Descriptive finding D8.1 — Calibration infeasibility dominates the declared matrix

**Status:** `POST_HOC_DESCRIPTIVE_FINDING`, not a new predeclared aggregate label.

95/108 declared cells were calibration-infeasible. S3 had 0/36 feasible cells. `provenance_removed` and `post_transform_chain` each had 0/36 feasible cells.

This finding may be reported as a property of the completed declared matrix, but it may not be used to rewrite the frozen classification or thresholds.

## Descriptive finding D8.2 — Some false matches are high-score

**Status:** `EXPERIMENTALLY_OBSERVED_DESCRIPTIVE_FINDING`.

The evidence contains 18 high-score false-attribution cell-event instances corresponding to 6 unique target generations and 2 unique U-test persons. They occur in the S2 canonical condition and repeat across its three narrowing modes.

The repeated mode instances must not be presented as independent events.

## Descriptive finding D8.3 — Transformed-state infeasibility is not anonymity

**Status:** `INTERPRETATION_BOUNDARY`.

The absence of a feasible threshold in transformed states means the declared scorer/abstention rule could not achieve the frozen combination of unknown rejection and known attribution utility. It does not prove the transformed artifacts are anonymous or unlinkable against other adversaries.

## Standing nonclaims

v0.8 does not establish:

- real-person tracking capability;
- deployed-provider watermark behavior;
- access to provider logs, accounts, billing or login records;
- real-user re-identification;
- real-world false-accusation prevalence;
- anonymity;
- authorship, ownership, responsibility, guilt or intent;
- legal authority to perform identity resolution;
- that provenance narrowing always helps or harms privacy;
- that any synthetic threshold is safe for production use.

## Standing DDC distinctions

- Detection ≠ Provenance ≠ Attribution ≠ Identity Resolution ≠ Authority.
- Closed-set accuracy ≠ open-set reliability.
- Best match ≠ sufficient match.
- Candidate reduction ≠ evidence creation.
- Confidence ≠ identity proof.
- Unknown rejection ≠ anonymity.
- Calibrated confidence ≠ transferable confidence.
- Synthetic evidence ≠ deployed-provider evidence.
- Experiment result ≠ validated invariant.
- Correlation ≠ authorization.
