# Validation Record v0.6

**Candidate:** `lab/noncommutativity_lab.py`  
**Exact candidate Git blob:** `f0269836e2b4d611b1aff6eee2f85a5c7b9013a3`

## DDC transition

- Authority: bounded travel-program execution delegated by Root Human Authority.
- Intent: remove execution-time bottleneck without changing research semantics.
- Preconditions: canonical research head unchanged; no open PR conflict; v0.6 test plan predeclared.
- Execution boundary: caching/performance only; no population, transformation, scoring, threshold, privacy boundary, or claim expansion.
- Transition: cache artifact features, per-candidate component scores, and completed evaluations.
- Verification: canonical scorer parity, focused tests, commuting control, deterministic repeated reference run.
- Evidence: exact Git blob, deterministic report hash, reference result.
- Consequence: v0.6 becomes eligible for PR/merge review; result remains experimental synthetic evidence.

## Verification evidence

- focused v0.6 tests: **7/7 PASS**
- exact reference parameters: persons `12`, seed `41`, artifact seed `7000`, generations `144`
- all six unordered transform pairs evaluated in both orders
- all 24 complete four-transform paths evaluated
- cached evaluator parity: **PASS**
- commuting negative control: **PASS**
- Pearson correlation: `0.9282921071911276`
- emitted status: `PAIRWISE_MECHANISM_PREDICTIVE_FOR_DECLARED_TEST`
- repeat sorted-JSON equality: **PASS**
- sorted reference JSON SHA-256: `9ffa255849d49d611503fe3b69c568d594775eb68cd1af5225119047c009e7ad`

## Evidence maturity

- Designed: **yes**
- Implemented: **yes**
- Focused-tested: **yes**
- Exact candidate reference executed: **yes**
- Deterministic repeat: **yes**
- Recovery-proven: **not applicable / not claimed**
- Production-authorized: **no**
- External deployment validated: **no**

## Remaining boundaries

This validation is limited to the declared synthetic experiment and exact source candidate. It does not establish external validity, production privacy guarantees, legal anonymity, or behavior of any deployed provider.
