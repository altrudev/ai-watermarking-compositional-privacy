# Detector-Oracle Protocol Amendment v0.9.4 — Evidence Contract and Conservative Mitigation Boundary

**Status:** frozen post-implementation-audit repair; canonical execution has not occurred  
**Trigger:** `research/DDC_IMPLEMENTATION_AUDIT-v0.9-detector-oracle-initial.md`  
**Precedence:** supplements v0.9-v0.9.3. It does not alter the hidden detector, populations, disclosure mappings, query policies, classifier, open-set thresholds, utility function, or positive inference materiality thresholds.  
**Post-observation rule:** this amendment may narrow or invalidate candidate claims but may not introduce a new favorable threshold after noncanonical implementation previews were observed.

## D1. Mitigation claim is not evaluable in v0.9

The phrase `D3 clean detection utility` in v0.9.1 A9 was never assigned a frozen mathematical metric before implementation preview.

Defining that metric now would create a post-observation degree of freedom.

Therefore, for v0.9:

- `MITIGATION_REDUCES_LEAKAGE` is **disabled** and must be reported as `NOT_EVALUABLE_UNDER_V0.9`;
- D6 information gain, class accuracy, false-attribution rate, rate-limit behavior, and content-utility retention remain reportable descriptive measurements;
- D6 may be compared numerically with D3/D4, but no confirmatory mitigation-success label may be emitted;
- no differential-privacy, anonymity, safety, or production mitigation claim is allowed.

A future detector-mitigation experiment must predeclare an exact detection-utility metric before any result is observed.

This change can only narrow v0.9 claims.

## D2. M5 must be retained exactly as already frozen

For every represented holdout artifact under the same scenario/disclosure/budget/state:

`removal_advantage = QF_final_score - QA_REMOVE_final_score`

`spoof_advantage = QA_SPOOF_final_score - QF_final_score`

The canonical comparison record retains per-artifact values and scenario medians.

M5 is descriptive/security evidence only and cannot trigger `MATERIAL_INFERENCE_GAIN`, `BINARY_ORACLE_LEAKAGE_OBSERVED`, or `ADAPTIVE_ADVANTAGE_OBSERVED`.

Auxiliary evidence E0/E3 is irrelevant to M5 because E is applied after detector observation; M5 must therefore be calculated once per scenario/disclosure/budget/state rather than duplicated across E conditions.

## D3. Canonical per-artifact evidence record

Every represented or unknown holdout artifact evaluated in the canonical core must produce a deterministic evidence record containing:

- scenario;
- true synthetic K class;
- artifact ID;
- artifact state;
- disclosure;
- policy;
- query budget;
- evidence condition;
- starting hidden detector score before query edits;
- final hidden detector score;
- detector call count;
- emitted-response SHA-256 over canonical response serialization;
- complete chosen edit path as ordered P labels;
- utility;
- posterior over K1-K4 in canonical K order;
- predicted represented class;
- correctness for represented artifacts;
- posterior entropy;
- information gain;
- candidate-set size;
- for unknown artifacts, open-set accepted/rejected status, accepted class if any, top posterior, and margin.

Exact hidden scope-instance identifiers may remain in artifact custody IDs, but detector responses themselves must remain redacted as previously required.

## D4. Canonical condition summary

Every condition summary must include:

- existing aggregate metrics;
- number of artifact evidence records;
- SHA-256 of the sorted canonical per-artifact evidence records for that condition;
- `status = EVALUATED` or `status = INVALID`;
- if invalid, a stable reason code.

Aggregate summaries do not replace per-artifact evidence.

## D5. Canonical matched-comparison record

For each confirmatory represented condition compared with its frozen baseline, retain a comparison record containing:

- comparison family key;
- scenario;
- tested condition identity;
- matched baseline identity;
- information-gain delta;
- accuracy delta;
- candidate-size reduction (`baseline median candidate size - tested median candidate size`);
- utility status;
- materiality pass/fail for that scenario;
- cross-scenario family replication status after all three scenarios are available.

For QA conditions, also retain matched QF information/accuracy deltas.

For D1 binary leakage, the baseline must be matched D0/QF at the same budget/state/E as frozen in v0.9.2.

## D6. Protocol-invalid vs programming-error handling

The following expected protocol-domain failures may be retained as deterministic `INVALID` condition records rather than destroying all other adverse evidence:

- posterior normalization underflow;
- E3 combination normalization underflow;
- observation/template vector-length mismatch;
- missing matched baseline caused by a previously retained invalid baseline.

Each receives a stable reason code.

Unexpected exceptions, malformed constants, unknown disclosure/policy/state/evidence identifiers, or truth-boundary failures remain fail-closed programming/control errors and abort canonical classification.

No invalid condition may be silently dropped from denominators.

The existing rule remains: no matrix-wide positive inference label may emit if more than 20% of comparable confirmatory families are invalid.

## D7. Complete deterministic replay control

C8 is satisfied only by complete canonical bundle replay, not by equality of one policy run or one selected condition.

The implementation must expose deterministic canonical serialization sufficient to execute the entire candidate reference twice from identical bytes/seeds and compare:

- complete summary hash;
- represented evidence hash;
- unknown evidence hash;
- comparison-record hash;
- complete manifest hash.

All must be byte-identical between the two exact-byte runs.

Focused policy/condition replay tests remain useful subcontrols but cannot substitute for C8.

## D8. Same-detector disclosure parity

C3 must cover all disclosure conditions:

- D1 threshold derives from the same hidden scalar `s`;
- D2 bands derive from the same `s`;
- D3 equals rounded `s`;
- D4 scalar component equals rounded `s` and its bins use only the frozen `alpha[K] * z` contribution rule;
- D5 scalar component equals rounded `s`, with the frozen distance band and active-dimension rule;
- D6 begins from the same `s` and differs only through the frozen query-index deterministic noise, banding, and rate limit.

## D9. Exploratory coverage disclosure

The v0.9 canonical confirmatory result may proceed without budgets 1/8 or states A2/A3 because v0.9.1 excluded them from confirmatory aggregate labels.

If they are not executed, the final result must explicitly state:

`EXPLORATORY_SENSITIVITY_MATRIX_NOT_EXECUTED`.

No language such as “full v0.9 matrix” may imply those exploratory conditions were run.

## D10. Summary label after this amendment

Overall precedence becomes:

1. `CONTROL_FAILED` if a mandatory control fails;
2. `DETECTOR_MEDIATED_INFERENCE_OBSERVED` if any still-authorized confirmatory inference label (`MATERIAL_INFERENCE_GAIN`, `BINARY_ORACLE_LEAKAGE_OBSERVED`, `ADAPTIVE_ADVANTAGE_OBSERVED`) emits;
3. `FALSE_ATTRIBUTION_ONLY_OBSERVED` if no confirmatory inference label emits but false scope-class attribution occurs;
4. `NO_PREDECLARED_EFFECT_ESTABLISHED` otherwise.

D6 mitigation cannot affect the overall summary label in v0.9.

## DDC boundary

This amendment repairs evidence custody and narrows an underdefined claim. It does not use preview values to select a new threshold, does not expand to real people/providers, and does not authorize canonical execution until the repaired implementation passes a second implementation audit.
