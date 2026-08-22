# DDC Result Audit — v0.8 Final Candidate

**Status:** final result-level audit before canonical merge  
**Research scope:** synthetic-only  
**Canonical main at final integration start:** `29204692e748f19f506ed29f10e1d9c7a7e5874f`  
**Clean integration candidate:** `cedbeca45fe4fa694e2feb32fdb4e856434c8355`  
**Base protocol:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Amended/audited protocol head:** `0a3f970beb200be97e04b9bc86b56584021e040a`  
**Implementation specification:** `87a01c30b4d7ea1185fbaba48966f8786a6b60a7`

## Executive decision

The v0.8 open-set / false-attribution experiment satisfies the declared pre-execution, implementation, determinism, evidence-retention and result-interpretation gates within the synthetic-only boundary.

**Final DDC result decision: `PASS FOR CLEAN CANONICAL MERGE`.**

This decision authorizes promotion of the exact audited synthetic experiment and its evidence records into the repository's experimental lineage. It does **not** promote any v0.8 finding into a production invariant, real-person attribution capability, provider claim, identity-resolution authority or deployment authorization.

The frozen aggregate classification is:

**`CONTEXT_DEPENDENT_OPEN_SET_CONTROL`**

The classification must be read together with the dominant adverse result: **95 of 108 cells were calibration-infeasible**. Only 13 cells produced a threshold satisfying the predeclared calibration constraints. All 13 feasible cells were in the `published_derivative` state; neither transformed state produced a feasible open-set threshold. Scenario S3 produced 0/36 feasible cells.

## 1. Authority

Root Human Authority explicitly authorized proceeding with v0.8 after the full protocol audit and subsequently authorized completion of the final closure/merge sequence.

No experiment component creates or delegates identity-resolution authority.

**PASS.**

## 2. Intent

The declared intent is to test whether a synthetic attribution matcher can distinguish represented from unrepresented synthetic sources, abstain when evidence is insufficient, expose false-attribution behavior, and measure transfer/narrowing effects.

The experiment is not intended to identify real people or reproduce a deployed provider watermark.

**PASS.**

## 3. Rules-before-results lineage

The following existed before the complete v0.8 reference result:

1. `research/TEST_PLAN-v0.8.md`;
2. `research/CLAIM_REGISTER-v0.8-PREDECLARED.md`;
3. `research/TEST_PLAN-v0.8-AMENDMENT-1.md`;
4. `research/CLAIM_REGISTER-v0.8-AMENDMENT-1.md`;
5. `research/DDC_FULL_AUDIT-v0.8-PROTOCOL.md`;
6. `research/IMPLEMENTATION_SPEC-v0.8.md`;
7. exact implementation/test candidate;
8. `research/DDC_IMPLEMENTATION_AUDIT-v0.8-PRE-REFERENCE.md`.

No scenario, seed, population size, transformation state, evidence policy, narrowing mode, threshold grid, calibration gate, transfer gate or aggregate label threshold was changed after reference execution began.

**PASS.**

## 4. Exact source identities

The clean integration commit reuses the exact previously audited Git blobs rather than replaying intermediate branch history:

- `lab/open_set_attribution_v08.py`: `9f9d82e6a560c7fa62f0ccf716e63b8f0bccada0`
- `lab/open_set_reference_v08.py`: `32eca12b0671841cb19de34c6a6a15f2a65736c0`
- `lab/open_set_raw_evidence_v08.py`: `f6152684dbe13274ce1a60b286acb10b26289d4c`
- `tests/test_open_set_attribution_v08.py`: `044f77aee05eb253cc2d9b2d95613ed0387db372`
- `tests/test_open_set_reference_v08.py`: `0e6341da4543c32c447758c43776c2173644acc4`
- `tests/test_open_set_raw_evidence_v08.py`: `26cd2c3737e44a78a5405c29106d24983ecd53ae`
- unchanged historical scorer dependency `lab/transformation_chain_lab.py`: `30b9bde830eaa8f00771957d50ed78d21979fa49`

The final integration was rebuilt from current `main` and these exact blobs. Intermediate malformed or superseded implementation commits are not promoted as canonical implementation states.

**PASS.**

## 5. Test and control verification

Focused v0.8 tests cover:

- protocol/spec identity binding;
- 108-cell matrix dimensions;
- deterministic cohort assignment;
- K/U-cal/U-test person disjointness;
- unknown generations absent from candidate database;
- immutable known calibration/holdout partition;
- malformed provenance fail-closed behavior;
- absent-provenance fallback semantics;
- zero-candidate abstention;
- single-candidate `INSUFFICIENT_COMPARATORS` abstention;
- truth-label independence;
- historical scorer parity across declared scenario/state/policy combinations;
- deterministic calibration;
- calibration evidence retention;
- false/wrong attribution evidence retention;
- score-separation retention for calibration-infeasible cells;
- classification precedence;
- raw-record schema coverage and raw-evidence determinism.

Core/reference focused suite: **16/16 PASS**.  
Raw-evidence focused tests: **PASS**, including the complete deterministic S1 raw-evidence test.  
Negative controls C1-C7: **all PASS**.  
Historical scorer parity: **PASS**.

A network clone of the clean integration branch could not be performed in the audit sandbox because outbound DNS/network access is unavailable. This is not treated as a clean-checkout proof. However, the clean integration commit reuses the exact Git blobs already executed locally, and the intervening canonical-main changes were documentation-only; no scorer or experiment dependency changed.

**PASS WITH DISCLOSED ENVIRONMENT LIMITATION.**

## 6. Deterministic reference execution

Two complete reference executions were serialized as stable sorted compact JSON.

Both complete evidence objects were byte-identical:

- bytes: **223,416**
- SHA-256: **`8e0d60322528d44eccf42801caaf5af24e48848d6b75e875b23a59f0a9feca43`**

The complete aggregate output, not merely the headline metrics, was compared.

**PASS.**

## 7. Raw artifact-level evidence retention

The first result-level audit identified a merge-blocking evidence defect: aggregate distributions and adverse events were retained, but the protocol also required per-artifact raw score outputs.

That defect was repaired through an evidence-only exporter. The scorer, thresholds, populations, policies, states, modes and classification were not changed.

The final raw evidence contains **44,928 per-artifact records** across S1-S3, retaining candidate count, top-1/top-2 score, margin, predicted synthetic IDs, correctness, candidate-survival and true-target filter-exclusion fields.

Deterministic raw archives:

- S1: 10,368 records; 320,558-byte gzip; SHA-256 `d5ade57c0db81e02f4c6830428fd953f3e322434034e30ed7c993957835b45e5`
- S2: 13,824 records; 452,195-byte gzip; SHA-256 `229940087f273bf75e1c880b77798b0dd6be010eb56610fa436ef4983d9717c8`
- S3: 20,736 records; 682,288-byte gzip; SHA-256 `94557ab84c117f01a252dbee649b679e36058e4c45ead37c74f494804d45f141`

Each scenario archive reproduced byte-identically on a second pass.

The complete external evidence bundle is 1,837,642 bytes with SHA-256:

`baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

The repository retains the cryptographic evidence manifest because the connected GitHub interface does not expose a binary release-asset upload path. The actual binary bundle is retained separately; checksum retention is not misrepresented as binary retention in Git.

**PASS.**

## 8. Aggregate result review

Declared matrix: **108 cells**.

Calibration status:

- feasible: **13/108**;
- infeasible: **95/108**;
- S1 feasible: **10/36**;
- S2 feasible: **3/36**;
- S3 feasible: **0/36**;
- `published_derivative` feasible: **13/36**;
- `provenance_removed` feasible: **0/36**;
- `post_transform_chain` feasible: **0/36**.

Among the 13 evaluated cells:

- median UFIR: **1.0417%**;
- maximum UFIR: **10.4167%**;
- median KCAR: **75%**;
- median KWAR: **0%**;
- maximum KWAR: **5.2083%**;
- median accepted precision: **96.5517%**;
- median UPER: **12.5%**;
- cells with UFIR >=10%: **1**;
- cells with UFIR >=20%: **0**;
- cells with HS-UFIR >=5%: **3**.

The formal matrix-wide `FALSE_ATTRIBUTION_RISK_OBSERVED` label does not fire under its frozen thresholds. That fact must not be paraphrased as "no false attribution risk" or "safe".

**PASS, with adverse evidence preserved.**

## 9. False-attribution concentration and repeated measures

Across evaluated cells there are:

- **46 false-attribution cell-event instances**;
- **20 unique unknown target generations** represented among those instances;
- **7 unique unknown synthetic people** represented among those instances;
- **18 high-score false-attribution cell-event instances**;
- **6 unique target generations** among high-score false events;
- **2 unique unknown synthetic people** among high-score false events.

There are also **17 accepted wrong-known cell-event instances**, representing 6 unique target generations and 4 unique known synthetic people.

These counts are repeated measures over the same synthetic artifacts across policies/modes/states. They are not independent real-world accusations and must not be reported as such.

**PASS.**

## 10. Candidate narrowing review

Only eight narrowing comparisons had evaluated metrics on both the global and narrowed sides because calibration infeasibility dominates the matrix.

Within those comparable cells, narrowing effects were context-dependent:

- delta UFIR ranged from **-9.375 percentage points** to **+2.083 percentage points**;
- median delta UFIR was **0**;
- delta KCAR ranged from **-2.083** to **+12.5 percentage points**;
- delta KWAR ranged from **0** to **+2.083 percentage points**;
- true-person filter exclusion did not increase in these comparable known-source cells.

Therefore candidate narrowing cannot be described as uniformly privacy-improving or uniformly privacy-worsening in this benchmark.

**PASS.**

## 11. Threshold-transfer review

Frozen transfer results:

### S1 -> S2

- source thresholds unavailable: **26/36**;
- median destination UFIR among evaluated transfers: **21.875%**;
- median destination KCAR: **69.2708%**;
- median destination KWAR: **16.6667%**;
- transfer acceptable: **false**.

### S2 -> S3

- source thresholds unavailable: **33/36**;
- median destination UFIR among evaluated transfers: **36.8056%**;
- median destination KCAR: **34.7222%**;
- median destination KWAR: **12.5%**;
- transfer acceptable: **false**.

The result does not support treating locally calibrated confidence as portable across populations.

**Threshold calibration != transferable safety.**

**PASS.**

## 12. Claim-boundary audit

### Supported within the declared synthetic benchmark

- Unrepresented synthetic artifacts can still receive accepted attribution to represented synthetic people under some feasible cells.
- Open-set calibration can reduce false acceptance in some local conditions without eliminating useful known-source attribution.
- Candidate narrowing changes attribution behavior, but the direction is context-dependent.
- Threshold transfer is not supported across the declared population changes.
- Calibration feasibility itself is highly context-dependent.

### Not supported

- real-person attribution prevalence;
- deployed-provider watermark behavior;
- identification of any real user;
- anonymity guarantees;
- universal false-attribution rate;
- universal protection from an abstention threshold;
- provider-specific privacy conclusions;
- a general rule that narrowing always improves or worsens privacy;
- production identity-resolution capability or authority.

**PASS.**

## 13. Aggregate label precedence

The frozen precedence is preserved:

1. `CONTROL_FAILED`
2. `FALSE_ATTRIBUTION_RISK_OBSERVED`
3. `OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`
4. `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`

Controls pass. The matrix-wide false-attribution label does not meet its frozen trigger. The positive broad-control label cannot pass because all 108 cells are not calibration-feasible and transfer gates fail.

Therefore the emitted classification is correctly:

**`CONTEXT_DEPENDENT_OPEN_SET_CONTROL`**

No post-result relabeling is authorized.

**PASS.**

## 14. DDC invariants preserved

- Detection != Provenance != Attribution != Identity Resolution != Authority.
- Best match != sufficient match.
- Candidate reduction != evidence creation.
- Confidence != identity proof.
- Calibration success != transferable safety.
- Calibration infeasibility != anonymity.
- Unknown rejection != anonymity.
- Synthetic false attribution != real-world accusation prevalence.
- Synthetic evidence != deployed-provider evidence.
- Experimental result != validated invariant.
- Correlation != authorization.
- Negative/adverse evidence != permission to tune after observation.

**PASS.**

## 15. Main-branch drift and clean-integration review

During v0.8 closure, canonical `main` advanced from `459e49c296cf77c737098115468e35b52061c041` to `29204692e748f19f506ed29f10e1d9c7a7e5874f` through a DDC-audited research-documentation update.

The intervening main changes affected README/research-governance/lineage documentation only. They did not modify the v0.8 scorer dependency, tests or experiment code.

The original implementation branch therefore diverged and is **not** merge-authorized directly.

A clean integration branch was created from current `main` and populated using only the exact final audited v0.8 Git blobs. This removes the malformed/superseded implementation history from the canonical transition.

Repository status/lineage documentation added by the intervening update still describes v0.8 as pre-execution. After canonical experiment merge and exact merge-SHA verification, those status records must be updated in a separate lineage/documentation transition to prevent stale public state. That documentation synchronization does not alter experiment results.

**PASS FOR CLEAN INTEGRATION; DIRECT MERGE OF THE OLD IMPLEMENTATION BRANCH IS DENIED.**

## 16. Final decision

The experiment has reached:

`Designed -> Implemented -> Tested -> Deterministically Reproduced -> Evidence-Retained -> Result-Audited`

It has **not** reached:

`Real-world validated -> Production-authorized -> Identity-resolution authorized`.

### Merge authorization

**`PASS FOR CLEAN CANONICAL MERGE`**

Authorized next transition:

1. compare the clean integration branch to current `main` and require an ahead-only additive result;
2. open a PR from the clean branch;
3. bind merge to the exact reviewed PR head SHA;
4. merge using a clean/squash transition;
5. read back canonical `main` and verify the exact resulting commit;
6. update repository status/lineage documentation to mark v0.8 completed and record the canonical experiment commit;
7. do not begin v0.9 implementation without separate Root Human Authority authorization.
