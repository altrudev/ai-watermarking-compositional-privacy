# v0.9 Detector-Oracle Implementation Gate

**Status:** IMPLEMENTED — CANONICAL EXECUTION BLOCKED PENDING EXACT-BYTE REGRESSION PROOF  
**Base `main`:** `9301a74301e8ab3e11306225773c0f551d03055d`  
**Protocol final audit:** `ecee93170bfa4f8099e6eb9d1c844ef85f27a19a` — `PASS_FOR_IMPLEMENTATION`  
**Implementation commit:** `73f3644bb213ba12e789a4ff14d8a153f6bfc03b`  
**Implementation blob:** `48b4f41a85e77d4b0975cf1e5a165c5f17174ed4`  
**Focused-test commit:** `a6d8b8c987a5c79f3247696bcbbf94289f32dc83`  
**Focused-test blob:** `7e3e724a50dec435a0f03279f6ef4f4355d32bc0`

## Purpose

Record the difference between implementation progress and canonical experimental evidence. This gate intentionally refuses to treat tests executed against a semantically equivalent local prototype as proof that the exact committed branch bytes have passed the repository's required regression/execution gates.

## Completed transition evidence

1. The v0.9 detector-oracle protocol was predeclared before implementation.
2. The initial DDC adversarial audit failed the protocol as underspecified.
3. Result-critical functions, mappings, partitions, thresholds, edit policies, inference rules, utility semantics, open-set boundaries, and claim gates were frozen through amendments v0.9.1-v0.9.3.
4. The second DDC audit passed the repaired protocol for implementation only.
5. The synthetic implementation and focused unit-test suite are committed on the bounded branch `agent/detector-oracle-v0.9`.
6. The branch remains based exactly on `main` commit `9301a74301e8ab3e11306225773c0f551d03055d` with no base drift at the time this gate was recorded.

## Local development evidence — NOT exact-head proof

During implementation development, a semantically equivalent local prototype was compiled and exercised before the cleaned repository implementation was committed.

Observed local-development evidence:

- Python compile gate: PASS;
- focused detector-oracle unit tests after the aggregate-family repair: 17/17 PASS;
- complete candidate matrix executed twice with byte-identical serialized output;
- candidate matrix size: 684 represented-condition summaries plus 456 unknown/open-set control summaries;
- candidate preview summary classification: `DETECTOR_MEDIATED_INFERENCE_OBSERVED`;
- candidate preview flags: material inference, binary-oracle leakage, adaptive advantage, mitigation effect, and synthetic false scope-class attribution were all observed under the prototype;
- same-family replication logic was repaired before repository implementation was committed;
- mitigation evaluation was repaired to include the frozen false-attribution constraint before repository implementation was committed.

This evidence is useful implementation-development evidence only.

> **Semantic equivalence != exact-byte test evidence.**

> **Candidate preview != canonical experimental result.**

The preview classification and its counts must not be cited as the canonical v0.9 result until the exact committed implementation bytes pass the complete execution gate.

## Exact-byte gates still open

The final protocol audit requires all of the following on the exact implementation bytes before canonical execution/interpretation:

- [ ] compile `lab/*.py` and `tests/*.py` at the exact candidate head;
- [ ] run the focused v0.9 unit-test suite at the exact candidate head;
- [ ] run the complete historical v0.1-v0.8 repository regression suite at the exact candidate head;
- [ ] run mandatory protocol/control tests at the exact candidate head;
- [ ] run the complete v0.9 candidate reference twice and verify deterministic complete-result SHA-256 equality;
- [ ] record Python version, command output, pass/fail count, candidate commit, source blobs, and complete-result hash.

## Environment blocker

The available local execution environment cannot currently obtain a clean GitHub checkout because outbound repository resolution fails with:

`Could not resolve host: github.com`

The repository's existing reproducibility policy explicitly prohibits relabeling a reconstruction or locally equivalent implementation as a clean exact-head run.

Therefore the historical whole-repository regression and exact committed-byte v0.9 replay remain **NOT PROVEN**, rather than being inferred from the local prototype.

## DDC decision

**`IMPLEMENTED_BUT_CANONICAL_EXECUTION_BLOCKED`**

Allowed next work:

- static/adversarial review of the branch implementation against the frozen protocol;
- exact-byte execution when a suitable environment is available;
- fixes for implementation defects discovered before canonical execution, provided the protocol is not changed silently;
- draft PR review with this gate visible.

Not allowed yet:

- merge as a completed/canonical v0.9 experiment;
- publish the candidate preview numbers as validated v0.9 evidence;
- reinterpret synthetic scope-class results as real-user, real-provider, key-recovery, authorship, ownership, or identity evidence;
- loosen the execution gate because the candidate preview looks favorable.

## Standing distinction

**Implementation != execution evidence != canonical result != deployed-provider claim.**
