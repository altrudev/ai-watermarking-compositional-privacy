# DDC Audit — v0.9.4 Evidence-Contract Amendment

**Amendment audited:** `3b0bfb712f41a3112fbb1d3c3019ceff89f63713`  
**Triggering implementation audit:** `d85fbbd0cf2f76bd923e9c9d78f89e5b886749c8`  
**Scope:** synthetic-only  
**Decision:** **PASS FOR IMPLEMENTATION REPAIR**

## Audit question

Does v0.9.4 use knowledge from the noncanonical candidate preview to make a favorable result easier to obtain, or does it only close evidence gaps and narrow underdefined claims?

**Decision:** it only closes evidence gaps and narrows claims.

## Review

### Mitigation boundary

The original protocol never froze a mathematical definition of `D3 clean detection utility`. v0.9.4 does not invent one after preview. It disables the confirmatory mitigation-success label for v0.9 and keeps D6 descriptive.

This cannot turn a null result into a positive result.

**PASS — conservative narrowing.**

### M5

v0.9.4 merely requires reporting the exact M5 equations already frozen in v0.9.2. No threshold or positive aggregate label is added.

**PASS — evidence completion, no result tuning.**

### Evidence records and hashing

Starting/final score, response hash, path, posterior, utility, false-attribution decision, condition evidence hash, matched comparisons, and complete replay hashes are evidence-custody requirements. They do not change the underlying detector, policy, populations, posterior, or thresholds.

**PASS.**

### Invalid-cell retention

Retaining protocol-domain invalid cells can only preserve adverse evidence that the current implementation might otherwise abort or lose. It cannot increase a positive denominator or silently remove failures.

**PASS.**

### C3/C8 strengthening

Expanding same-detector parity across D1-D6 and requiring complete replay strengthens controls. It does not grant new authority or make positive labels easier.

**PASS.**

### Exploratory sensitivity matrix

Explicitly permitting the confirmatory result to state that budgets 1/8 and A2/A3 were not executed preserves the v0.9.1 distinction between confirmatory and exploratory work. It prevents an incomplete sensitivity study from being described as a full matrix.

**PASS.**

## DDC invariant check

- Rules before canonical results — PASS. No canonical v0.9 execution has occurred.
- Adverse evidence retention — strengthened.
- Post-observation tuning — avoided by disabling, not redefining, the ambiguous mitigation label.
- Synthetic evidence != deployed-provider evidence — unchanged.
- Detection != attribution != identity resolution != authority — unchanged.
- Candidate preview != canonical result — unchanged.

## Authorized repair

Implementation may now be changed only to conform to v0.9.4 by:

1. adding canonical per-artifact evidence records and deterministic bundle hashing/serialization;
2. adding exact M5 comparison records;
3. adding matched comparison records for M2/M7 and adaptive comparisons;
4. retaining protocol-invalid conditions with stable reason codes;
5. strengthening C3 and complete-replay support;
6. disabling the v0.9 mitigation-success label and marking it `NOT_EVALUABLE_UNDER_V0.9`;
7. explicitly recording unexecuted exploratory sensitivity conditions.

No other result-critical changes are authorized by this audit.

**Final decision:** `PASS_FOR_IMPLEMENTATION_REPAIR`.
