# DDC Implementation Audit — v0.9 Detector Oracle (Initial)

**PR:** #23  
**Implementation head audited:** `040c89fff6ccb8fad49d1509c304e49ea15ec4b4`  
**Implementation source blob:** `48b4f41a85e77d4b0975cf1e5a165c5f17174ed4`  
**Test source blob:** `7e3e724a50dec435a0f03279f6ef4f4355d32bc0`  
**Protocol audit authority:** `ecee93170bfa4f8099e6eb9d1c844ef85f27a19a`  
**Decision:** **FAIL — REPAIR BEFORE EXACT-BYTE EXECUTION**

## Audit purpose

Review the committed implementation against the frozen protocol after the protocol passed DDC but before any exact committed-byte execution is accepted as canonical evidence.

This audit is intentionally separate from runtime testing. Static conformance defects can invalidate a future run even if every unit test passes.

## Findings

### I1 — canonical evidence bundle is incomplete — BLOCKING

The protocol requires the result record to retain, at minimum, starting/final detector score where applicable, emitted responses or deterministic hashes, chosen edit path, utility, candidate-set sizes, inference metrics, false-attribution events, invalid/adverse cells, exact lineage, and complete-result hash.

The committed `candidate_reference()` retains aggregate condition summaries and false-attribution events, but it does not preserve a result-critical per-artifact record containing the starting score, response hash, edit path, and inference record.

**Consequence:** a future aggregate could be reproducible while the transition path that produced it is not independently inspectable.

**Repair:** add a canonical per-artifact evidence record/generator and a deterministic bundle writer or equivalent complete serialization contract. Aggregate summaries must reference evidence hashes rather than replace the evidence.

### I2 — M5 spoof/removal optimization metric is not reported — BLOCKING

v0.9.2 B7 freezes:

- removal advantage = `QF_final_score - QA_removal_final_score`;
- spoof advantage = `QA_spoof_final_score - QF_final_score`.

The committed harness computes final scores but does not calculate or retain M5 comparison summaries.

**Repair:** implement M5 exactly as frozen. Keep it separate from `MATERIAL_INFERENCE_GAIN` as required.

### I3 — mitigation preservation criterion remains underdefined — BLOCKING PROTOCOL DEFECT

v0.9.1 A9 states that `MITIGATION_REDUCES_LEAKAGE` requires D6 to retain at least `80%` of **D3 clean detection utility**. The committed implementation substitutes `median_utility >= 0.80`, which is the content/semantic utility function, not a defined detector-utility measure.

The protocol never froze a separate mathematical definition of “clean detection utility.” Defining one now after noncanonical candidate previews have been observed would create a post-observation degree of freedom.

**Conservative repair:** do **not** invent a detector-utility metric after preview. Amend v0.9 so `MITIGATION_REDUCES_LEAKAGE` is `NOT_EVALUABLE_UNDER_V0.9` and D6 mitigation remains descriptive only. A future separately predeclared experiment may test detector-utility/privacy tradeoffs with an exact metric frozen before results.

This repair can only narrow claims; it cannot create a new positive v0.9 result.

### I4 — complete deterministic replay is not a mandatory implementation control — MATERIAL

`controls()` labels C8 using equality of one repeated `PolicyRun`. The test suite repeats one selected condition. The frozen protocol C8 requires repeated **complete execution** with byte-identical canonical serialization.

The implementation gate already requires an external complete replay, so this is not necessarily a model defect, but the code should expose a deterministic complete-result serialization and replay verifier so the gate can be tested directly.

**Repair:** expose canonical serialization/hash over the complete summary and evidence manifest; add a complete replay comparison entry point. Exact committed-byte execution must still run it twice.

### I5 — invalid/adverse cell retention is incomplete — BLOCKING

The protocol requires invalid/adverse cells to be retained. Current underflow/vector mismatch/control exceptions abort execution rather than becoming explicit invalid-cell evidence.

**Repair:** condition execution must return a deterministic invalid record with reason for protocol-defined invalid states. Unexpected programming errors may still fail closed, but protocol-invalid cells must not disappear or abort all adverse evidence.

### I6 — same-detector parity control is too narrow — MATERIAL

C3 currently checks D1 and D3 against the hidden scalar. It does not assert D2/D4/D5 mappings from that same scalar, nor D6’s separation into the same scalar plus only the predeclared deterministic noise transformation.

**Repair:** strengthen C3/tests to cover every disclosure mapping.

### I7 — marginal metrics are derivable but not explicitly retained — MATERIAL

M2 candidate reduction and M7 marginal compositional attribution gain are inferable from condition tables, but the canonical report does not retain explicit matched deltas/family comparison records.

**Repair:** produce deterministic comparison records containing matched baseline identity, information-gain delta, accuracy delta, candidate-size delta, M5 optimization delta where applicable, and family replication status.

### I8 — v0.9 exploratory conditions are not executed by the current reference — NONBLOCKING FOR CONFIRMATORY CORE

Budgets 1/8 and states A2/A3 are identified as exploratory sensitivity conditions in v0.9.1 but are not included in `candidate_reference()`.

Because v0.9.1 explicitly excludes them from confirmatory aggregate labels, this does not block the confirmatory v0.9 core. It must, however, be disclosed as **not executed** rather than silently implied complete.

## Positive conformance observations

The static review found the following aligned with the frozen protocol:

- exact K0-K7 base/alpha coefficients;
- exact state offsets and utility constants;
- exact P1-P5 vectors;
- exact SHA-256 first-8-byte mapping;
- D0-D6 disclosure shapes and D6 8-call informative limit;
- one edit per query/call accounting;
- QF and QA policy mappings;
- K1-K4 represented classifier and K0/K5-K7 unknown control semantics;
- calibration indices 0-3 and holdout 8-11;
- K1-K4 template posterior temperature `0.05`;
- E3 true-class weak prior only for represented classes;
- top posterior/margin open-set thresholds;
- same-family cross-scenario replication repair;
- false-attribution constraint included in the D6 comparison;
- candidate preview remains explicitly noncanonical in the implementation gate.

## DDC decision

**`FAIL_IMPLEMENTATION_PROTOCOL_INCOMPLETE`**

No exact-byte execution should be promoted to canonical evidence until I1-I7 are repaired and the resulting branch passes a second implementation audit.

This finding does not invalidate v0.8 and does not make any deployed-provider claim. It only prevents v0.9 implementation convenience from outrunning its own evidence contract.
