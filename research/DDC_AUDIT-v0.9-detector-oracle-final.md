# DDC Adversarial Protocol Audit — v0.9 Detector Oracle (Final)

**Protocol lineage audited:**  
- v0.9 draft `da81f93f7e275d2e87358c8e359a5dd529c7d98d`  
- initial FAIL audit `3a4dbe99b29b644c665748a8999e9d8813acf7d2`  
- v0.9.1 amendment `74bb5332031dbfe1ddfdb03fa827130f3be88599`  
- v0.9.2 final amendment `71709514e5e109aa947887a1dccdf5f0b28a98db`  
- v0.9.3 execution mapping `353ec2fc0073c574b6615465ccb02ac863941dd1`

**Scope:** synthetic-only  
**Decision:** **PASS FOR IMPLEMENTATION — CANONICAL EXECUTION STILL REQUIRES IMPLEMENTATION/TEST GATE**

## Repair verification

| Initial finding | Disposition |
|---|---|
| F1 hidden detector underdetermined | CLOSED — exact logit, coefficients, state offsets, hash mapping frozen |
| F2 inference method underdetermined | CLOSED — calibration templates, encoding, posterior temperature, entropy and candidate rules frozen |
| F3 detector disclosures incomplete | CLOSED — D1-D6 thresholds/bands/noise/rate-limit semantics frozen |
| F4 edit operators unspecified | CLOSED — P1-P5 and exact QF/QA policies frozen |
| F5 utility metric undefined | CLOSED — state utilities and per-edit penalty frozen |
| F6 spoof proxy could leak truth | CLOSED — A4 is fixed class-independent state offset; no hidden-label copying |
| F7 matrix oversized/repeated measures | CLOSED — confirmatory core separated from exploratory/unknown controls; repeated-measure interpretation explicit |
| F8 D0 ambiguity | CLOSED — D0 uses matched QF edit path, zero calls, budget preserved; D0/QA prohibited |
| F9 partition not concrete | CLOSED — artifact indices 0-3/4-7/8-11 frozen and instance assignment exact |
| F10 disjunctive materiality | CLOSED — information/accuracy required; candidate reduction descriptive only |
| F11 architecture inference wording broad | CLOSED — metric limited to synthetic scope-class inference and explicit nonclaims |
| F12 response-stability subtest incomplete | CLOSED — repeated-query control frozen |

## Additional audit checks

### Query-budget accounting

v0.9.2 closes a material ambiguity introduced by the v0.9.1 candidate-edit wording. One applied edit equals one detector call for D1-D6. QF/QA matched comparisons consume exactly the declared budget. D0 consumes zero calls but the same number of deterministic QF edits.

**PASS.**

### Adaptive policy authority

QA can observe only the previously disclosed detector response. It cannot inspect hidden score except where the rounded scalar is itself the declared D3-D5 response; it cannot inspect alpha, hidden K, unqueried candidates, or future outputs.

**PASS.**

### Unknown/open-set semantics

False attribution is now a synthetic scope-class confusion problem: K1-K4 represented; K0/K5-K7 unknown. The metric cannot be described as human identity resolution.

**PASS.**

### Auxiliary evidence construction

E3 deliberately contains a weak synthetic correlation with represented truth. That is not accidental leakage because it is the predeclared auxiliary channel being studied. Unknown classes receive no fabricated represented-class advantage. Detector marginal gain is always measured against the same E3 prior under D0.

**PASS WITH DISCLOSURE REQUIREMENT:** publications must state that E3 is synthetic correlated evidence, not observed platform metadata.

### K0 control

K0 base signal and zero alpha are frozen. Any systematic positive detection beyond artifact/state/noise effects remains visible as adverse detector behavior rather than silently reclassified.

**PASS.**

### D6 mitigation

D6 is not claimed to be differential privacy. It is a bounded-noise/coarsening/rate-limit synthetic mitigation condition only.

**PASS WITH NONCLAIM:** no DP guarantee may be stated.

### Result-label independence

The classification precedence permits positive, false-attribution, null, and control-failed outcomes. No preferred result is hard-coded by protocol semantics.

**PASS.**

## DDC invariant review

- Need != Authority — PASS.
- Data != Authority — PASS.
- Detection != Provenance != Attribution != Identity Resolution != Authority — PASS.
- Candidate reduction != evidence creation — PASS.
- Query leakage != key recovery — PASS.
- Watermark removal != anonymization — PASS.
- Synthetic evidence != deployed-provider evidence — PASS.
- Rules before results — PASS after amendments.
- Adverse evidence retention — REQUIRED by result bundle.
- Exact execution lineage — REQUIRED before canonical result.

## Implementation authorization

**AUTHORIZED:** implementation of the frozen synthetic v0.9 detector-oracle protocol on a bounded branch.

Implementation may optimize caching and serialization but may not alter result-critical constants, populations, thresholds, detector mappings, edit policies, utility function, posterior rule, partitions, or claim gates.

## Execution gate

Canonical synthetic execution remains unauthorized until all are satisfied on the exact implementation bytes:

1. Python compile gate passes;
2. focused v0.9 tests pass;
3. historical v0.1-v0.8 regression suite passes;
4. protocol/control tests demonstrate exact constants and truth-label independence;
5. deterministic replay test passes on a complete candidate run;
6. executed bytes/commit are recorded exactly.

**Final protocol decision:** `PASS_FOR_IMPLEMENTATION`.
