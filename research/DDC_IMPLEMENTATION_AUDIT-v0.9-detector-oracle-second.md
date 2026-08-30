# DDC Implementation Audit — v0.9 Detector Oracle (Second Pass)

**PR:** #23  
**Implementation head audited:** `c714e89a88b9e5ed6d3ef4aa891c949e1ccf13da`  
**Canonical base:** `9301a74301e8ab3e11306225773c0f551d03055d`  
**Prior implementation audit:** `research/DDC_IMPLEMENTATION_AUDIT-v0.9-detector-oracle-initial.md` — `FAIL_IMPLEMENTATION_PROTOCOL_INCOMPLETE`  
**Evidence-contract amendment:** `3b0bfb712f41a3112fbb1d3c3019ceff89f63713`  
**Evidence-contract DDC audit:** `59374595c41e4c3732d5eb5b1a117c9623884075` — `PASS_FOR_IMPLEMENTATION_REPAIR`  
**Scope:** synthetic-only  
**Decision:** **FAIL — THREE REPAIRS REMAIN BEFORE EXACT-HEAD EXECUTION**

## Audit question

Does the repaired implementation now enforce the frozen DDC transition strongly enough that a future exact-head run cannot acquire canonical status through incomplete replay, incomplete adverse-cell accounting, or execution of code other than the state reviewed by this audit?

**Answer: not yet.** The v0.9.4 evidence-custody repair closes the major defects from the first implementation audit, but three control gaps remain.

## Finding S1 — C8 replays the candidate bundle, not the finalized canonical bundle — BLOCKING

`replay_gate()` builds the complete candidate reference twice and compares:

- `summary.json` while its classification is still `PENDING_EXACT_EXECUTION_GATE`;
- represented evidence;
- unknown evidence;
- comparisons;
- M5;
- the candidate manifest.

Only after that replay passes does `finalize_reference()` mutate the summary to add:

- C8 `PASS`/`FAIL`;
- `exact_execution_gate`;
- final classification;
- exact Git identity;
- Python/runtime identity;
- compile/regression/replay proof;
- a new summary hash.

The final bundle containing those canonical fields is then written only once.

v0.9.4 D7 requires **complete canonical bundle replay**. A deterministic precursor is strong evidence but is not the same object as the finalized canonical result.

### Required repair

Separate the two concepts explicitly:

1. `REFERENCE_REPLAY` — the experimental reference/evidence payload is generated twice and must be byte-identical;
2. `CANONICAL_BUNDLE_REPLAY` — after runtime proof/identity are fixed, construct the finalized canonical bundle twice from the same reference + execution proof and require byte-identical summary/component/manifest hashes before C8 can become `PASS`.

The compile/regression commands do not need to be executed twice. Their already-recorded proof can be supplied identically to both finalization passes. What must be replayed is the **canonical serialization that will be published as evidence**.

Until then:

`C8_COMPLETE_REPLAY != proven complete canonical replay`.

## Finding S2 — invalid-family accounting undercounts adaptive-comparison invalidity — BLOCKING

`_replication_labels()` builds `invalid_scenarios` only from `DETECTOR_VS_D0` comparison rows.

An `ADAPTIVE_VS_QF` row can be invalid because the matched QF condition is invalid even when the adaptive tested condition and its D0 baseline remain evaluable. In that case the adaptive comparison is not counted in the global `invalid_family_ratio`.

This can make the matrix appear more complete than it is and, in a sufficiently adverse matrix, permit positive labels while more than 20% of the actual confirmatory comparison families are unusable.

### Required repair

Track invalidity for each confirmatory comparison domain separately or over the union of all predeclared confirmatory families:

- detector-vs-D0 material-inference families;
- D1-vs-D0 binary-oracle families;
- QA-vs-QF adaptive families.

The >20% invalidity gate must be calculated from the actual comparable family set relevant to the label being emitted. An invalid adaptive family must never disappear merely because its detector-vs-D0 comparison is valid.

## Finding S3 — execution is not bound to the implementation state reviewed by DDC — BLOCKING GOVERNANCE

`exact_tree_identity()` correctly records `HEAD`, requires a clean worktree, records Git blob hashes, and verifies that the tree is unchanged after execution.

However, `execute()` does not require that `HEAD` equals a human/DDC-authorized implementation head. Any clean future commit containing a syntactically valid version of these files can pass the runner's identity test and potentially receive `canonical: true`, even if result-critical code changed after the last implementation audit.

This violates the intended transition:

`audited implementation -> authorized exact execution`

because the runner currently enforces only:

`clean implementation -> exact execution`.

### Required repair

The execution entry point must require an explicit expected/audited head and fail closed unless:

`git rev-parse HEAD == expected_authorized_head`.

The expected head must come from the governed execution authorization, not be inferred from whatever branch happens to be checked out.

Recommended implementation:

- require `--expected-head <sha>`;
- compare it against exact `HEAD` before compile/testing;
- record the expected head in the execution record;
- re-check exact `HEAD` after replay;
- final DDC implementation PASS should be recorded externally on PR #23 against the exact repaired head, so recording the approval does not itself move the audited branch head.

This preserves:

**Branch existence != authority.**  
**Clean tree != audited tree.**  
**Execution capability != execution authorization.**

## Repairs from the first implementation audit that are now CLOSED

### I1 — canonical evidence bundle incomplete

**CLOSED.** Per-artifact represented/unknown evidence now retains starting/final score, detector-call count, response hash, full edit path, utility, posterior, inference metrics, candidate size, and open-set decision fields. Condition summaries retain evidence counts and hashes.

### I2 — M5 missing

**CLOSED.** M5 now retains per-artifact removal/spoof advantage and scenario medians under the frozen equations.

### I3 — underdefined mitigation preservation criterion

**CLOSED CONSERVATIVELY.** v0.9.4 disables the confirmatory mitigation-success label rather than defining a favorable post-preview metric. D6 is descriptive only.

### I4 — complete replay not mandatory

**PARTIALLY CLOSED.** The implementation now has a full reference replay and correctly prevents the old lightweight policy-replay subcontrol from masquerading as C8. S1 remains because the finalized canonical bundle itself is not replayed.

### I5 — invalid/adverse cell retention

**CLOSED AT CONDITION LEVEL.** Protocol-domain underflow/vector mismatch conditions are retained with deterministic reason codes. S2 concerns aggregate invalid-family accounting, not loss of the underlying invalid records.

### I6 — same-detector parity too narrow

**CLOSED.** Full D1-D6 mapping checks now include D4 bins, D5 distance/active metadata, and D6 deterministic-noise derivation.

### I7 — marginal metrics not explicitly retained

**CLOSED.** Matched comparison records retain detector-vs-D0 and adaptive-vs-QF deltas plus family annotations.

### I8 — exploratory matrix incomplete

**CLOSED AS DISCLOSURE.** `EXPLORATORY_SENSITIVITY_MATRIX_NOT_EXECUTED` is explicit and the confirmatory run cannot be called a full v0.9 matrix.

## DDC invariant review

- **Need != Authority:** PASS. No external-provider or real-person scope expansion.
- **Data != Authority:** PASS in the detector/evidence layers; S3 must be repaired so checked-out code does not implicitly authorize itself.
- **Detection != Provenance != Attribution != Identity Resolution != Authority:** PASS.
- **Candidate reduction != evidence creation:** PASS.
- **Query leakage != key recovery:** PASS.
- **Watermark removal != anonymization:** PASS.
- **Synthetic evidence != deployed-provider evidence:** PASS.
- **Rules before results:** PASS at protocol level; execution remains blocked.
- **Adverse evidence retention:** PASS at artifact/condition level; aggregate invalid accounting requires S2 repair.
- **Exact lineage:** PARTIAL — recorded accurately, but S3 must bind execution to the audited state.
- **Complete deterministic replay:** PARTIAL — candidate/reference replay exists; finalized canonical replay requires S1 repair.

## Authority and transition decision

The current instruction authorizes **DDC review**, not canonical experiment execution.

Therefore:

- repair of S1-S3 is authorized on the bounded branch;
- exact-head execution remains unauthorized;
- candidate preview values remain noncanonical;
- PR #23 must remain draft/unmerged;
- no v0.9 detector-oracle finding may be published as validated repository evidence yet.

## Final decision

**`FAIL_SECOND_IMPLEMENTATION_AUDIT — REPAIR S1/S2/S3 BEFORE EXACT-HEAD EXECUTION`**

A third implementation audit should review only the repaired result-critical diff. If it passes, the approval should reference the exact branch head without modifying that head; exact execution must then require that approved SHA explicitly.
