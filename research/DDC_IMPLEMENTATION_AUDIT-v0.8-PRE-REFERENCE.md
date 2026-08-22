# DDC Implementation Audit — v0.8 Pre-Reference Candidate

**Status:** pre-reference implementation audit  
**Research scope:** synthetic-only  
**Canonical main at audit start:** `459e49c296cf77c737098115468e35b52061c041`  
**Base protocol:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Amended/audited protocol head:** `0a3f970beb200be97e04b9bc86b56584021e040a`  
**Implementation specification:** `87a01c30b4d7ea1185fbaba48966f8786a6b60a7`  
**Reference-result status at audit time:** no complete v0.8 reference matrix had been generated from this final candidate

## Executive result

The final v0.8 implementation tree is additive over canonical `main`, contains no historical v0.1-v0.7 experiment/result edits, and implements the repaired open-set/false-attribution protocol inside the synthetic-only boundary.

**Implementation candidate result:** `PASS FOR CANDIDATE REFERENCE EXECUTION`.

A candidate reference matrix may now be generated from the exact final v0.8 source/test bytes. It is not merge-authorized merely because it runs. Before a canonical result is merged, the generated evidence must still pass deterministic replay, result-level DDC review, complete evidence-retention review, exact-source verification and branch/base-drift review.

## Exact candidate source identities

- `lab/open_set_attribution_v08.py`: `9f9d82e6a560c7fa62f0ccf716e63b8f0bccada0`
- `tests/test_open_set_attribution_v08.py`: `044f77aee05eb253cc2d9b2d95613ed0387db372`
- `lab/open_set_reference_v08.py`: `32eca12b0671841cb19de34c6a6a15f2a65736c0`
- `tests/test_open_set_reference_v08.py`: `0e6341da4543c32c447758c43776c2173644acc4`
- unchanged canonical historical scorer dependency `lab/transformation_chain_lab.py`: `30b9bde830eaa8f00771957d50ed78d21979fa49`

The four v0.8 candidate blobs above match the exact locally executed Git object identities.

## Branch/base integrity

Comparison against canonical `main` at `459e49c296cf77c737098115468e35b52061c041`:

- branch status: ahead only;
- behind by: 0;
- final tree changes: five additive files;
- historical source/result deletions: 0;
- historical experiment modifications: 0;
- authority/runtime/production files changed: 0.

One malformed intermediate reference-wrapper commit occurred on the implementation branch and was repaired before testing or result generation. It is not evidence and must not be preserved as a canonical implementation state. Final integration should use a squash/clean-tree transition so only the final audited tree is promoted.

## DDC transition review

### Authority

Root Human Authority authorized proceeding with v0.8 after the full DDC protocol audit.

**PASS.**

### Intent

Test whether the declared synthetic matcher can distinguish represented from unrepresented synthetic sources, abstain when evidence is insufficient, and expose false-attribution behavior without turning matching evidence into identity authority.

**PASS.**

### Preconditions

The implementation binds itself to the exact base protocol, audited amendment and implementation specification. The deterministic K/U-cal/U-test assignment, known calibration/holdout split, threshold grid, calibration gate, candidate modes and aggregate label precedence are fixed before the complete reference matrix.

**PASS.**

### Execution boundary

Synthetic people/accounts/sessions/generations/artifacts only. No real people, real accounts, provider logs, private conversations, scraped profiles, production watermark detectors, proprietary APIs, credentials or external identity-resolution systems are accessed.

**PASS.**

### Proposed transition

Generate the first complete 108-cell candidate reference matrix under the frozen protocol.

**PERMITTED, subject to the verification limitations below.**

## Control and leakage verification

Exact candidate focused tests: **16 / 16 PASS**.

Python compilation of the four exact v0.8 candidate files: **PASS**.

The test boundary covers:

- exact protocol/spec identities;
- 108-cell matrix dimensions and frozen threshold grids;
- K/U-cal/U-test person disjointness;
- unknown generations absent from the candidate database;
- deterministic SHA-256 cohort assignment;
- immutable `-gen-0` known calibration / `-gen-1` known holdout partition;
- complete/absent provenance semantics;
- partial provenance fail-closed behavior;
- absent-provenance N1/N2 fallback semantics;
- zero-candidate abstention;
- single-candidate `INSUFFICIENT_COMPARATORS` abstention;
- truth-label score independence;
- historical scorer ranking parity across all 3 scenarios × 3 states × 4 policies on representative known samples;
- all C1-C7 negative controls;
- deterministic calibration and frozen feasibility gate;
- calibration provenance digest retention;
- false/wrong attribution evidence fields;
- score-separation and forced-choice evidence retention even when calibration is infeasible;
- aggregate classification precedence;
- narrowing differential evidence.

## Historical scorer dependency limitation

The audit environment cannot clone or fetch a complete checkout over the network. The local execution uses a reconstructed local copy of the inspected canonical historical scorer semantics. Its local Git blob is not byte-identical to canonical `30b9bde8...` because unrelated historical functions/formatting are omitted, although the functions exercised by v0.8 were reconstructed from the canonical source and the v0.8 parity tests pass against that reconstruction.

GitHub independently confirms that the implementation branch still references the unchanged canonical dependency blob `30b9bde830eaa8f00771957d50ed78d21979fa49`.

Therefore:

- the four new v0.8 source/test files have exact-byte execution evidence;
- canonical dependency non-modification is proven by Git object identity;
- a clean-checkout execution against the byte-exact canonical dependency is **not** proven in this environment.

This limitation must remain attached to any locally generated reference matrix. A locally generated matrix is a **candidate reference result** until reproduced in an environment executing the canonical dependency bytes.

## Rules-before-results verification

The following all predate the complete reference matrix:

1. base v0.8 protocol;
2. Claim Register predeclaration;
3. DDC Amendment 1;
4. Claim Amendment 1;
5. full protocol DDC audit;
6. deterministic implementation specification;
7. exact candidate implementation and tests;
8. this pre-reference implementation audit.

No v0.8 threshold, scenario, population size, seed, evidence policy, transformation state, narrowing mode, classification threshold or claim boundary may be changed after the first complete reference execution begins.

## Standing distinctions preserved

- Detection ≠ Provenance ≠ Attribution ≠ Identity Resolution ≠ Authority.
- Best match ≠ sufficient match.
- Candidate reduction ≠ evidence creation.
- Confidence ≠ identity proof.
- Unknown rejection ≠ anonymity.
- False attribution in this benchmark ≠ real-world accusation prevalence.
- Synthetic evidence ≠ deployed-provider evidence.
- Correlation ≠ authorization.
- Candidate result ≠ validated invariant.

## Pre-reference authorization

**PASS FOR CANDIDATE REFERENCE EXECUTION.**

The next permitted transition is exactly:

1. execute the complete reference matrix twice from the same final candidate source;
2. serialize both results with stable sorted compact JSON;
3. require byte-identical output and record SHA-256;
4. preserve all feasible/infeasible/adverse cells and synthetic false-attribution events;
5. apply only the frozen aggregate classification;
6. run a result-level DDC audit before merge or H/R Native integration.

Failure of determinism, controls, scorer parity, evidence retention or source identity blocks canonical promotion and must not be repaired by tuning the observed result.
