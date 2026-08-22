# Validation v0.8 — Open-Set / False-Attribution Experiment

**Scope:** synthetic-only  
**Aggregate classification:** `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`  
**Validation state:** complete candidate validation pending canonical merge

## Governing lineage

- base protocol: `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`
- amended/audited protocol: `0a3f970beb200be97e04b9bc86b56584021e040a`
- implementation specification: `87a01c30b4d7ea1185fbaba48966f8786a6b60a7`
- pre-reference implementation audit: commit `ccd9de0553e065c65ef42e44ec5eda69d02b9605`

The protocol, claim boundaries, full protocol DDC audit and deterministic implementation choices all predate the first complete reference result.

## Exact source identities

- historical scorer `lab/transformation_chain_lab.py`: `30b9bde830eaa8f00771957d50ed78d21979fa49`
- v0.8 core `lab/open_set_attribution_v08.py`: `9f9d82e6a560c7fa62f0ccf716e63b8f0bccada0`
- core tests: `044f77aee05eb253cc2d9b2d95613ed0387db372`
- reference wrapper: `32eca12b0671841cb19de34c6a6a15f2a65736c0`
- reference tests: `0e6341da4543c32c447758c43776c2173644acc4`
- raw-evidence exporter: `f6152684dbe13274ce1a60b286acb10b26289d4c`
- raw-evidence tests: `26cd2c3737e44a78a5405c29106d24983ecd53ae`

The historical scorer and all v0.8 source/test files above were reconstructed from GitHub into the execution environment and verified with local Git object hashing before final reference validation.

## Focused test validation

Exact core/reference focused suite:

**16 / 16 PASS**

Raw-evidence exporter suite:

**3 / 3 PASS**

Python compilation of the exact v0.8 implementation/test files:

**PASS**

Coverage includes:

- protocol/spec identity binding;
- declared matrix dimensions and threshold grids;
- K/U-cal/U-test person isolation;
- unknown generations absent from candidate data;
- deterministic cohort assignment;
- immutable known calibration/holdout partition;
- malformed provenance fail-closed behavior;
- provenance-absent fallback semantics;
- zero/single-candidate abstention;
- truth-label score independence;
- canonical historical scorer parity;
- C1–C7 negative controls;
- deterministic calibration;
- calibration feasibility gate;
- threshold-evidence digest retention;
- result classification precedence;
- forced-choice and score-separation evidence;
- complete raw-record field retention.

## Controls

All required controls passed:

- C1 no-candidate control: PASS
- C2 candidate-exclusion control: PASS
- C3 score independence from truth labels: PASS
- C4 deterministic replay control: PASS
- C5 single-candidate comparator control: PASS
- C6 partial-provenance fail-closed control: PASS
- C7 partition immutability control: PASS

Historical scorer parity passed across every declared scenario × artifact state × evidence policy combination.

## Complete reference determinism

Two independent complete 108-cell executions were assembled in the frozen canonical order from exact candidate bytes.

Both serialized compact sorted JSON objects were 223,416 bytes and byte-identical.

SHA-256:

`8e0d60322528d44eccf42801caaf5af24e48848d6b75e875b23a59f0a9feca43`

**Determinism: PASS.**

## Complete raw-evidence validation

A result-level DDC audit found that the initial reference object did not retain every per-artifact raw score row required by the protocol. This was treated as an evidence-retention defect, not permission to modify scoring, thresholds, populations, results or classification.

A separate deterministic exporter now retains 44,928 per-artifact records.

### S1

- records: 10,368
- JSON SHA-256: `557b41f07aefc6bbb71318dfe15249a8e8e854a8c00089c73cdb7a38c37c4335`
- gzip SHA-256: `d5ade57c0db81e02f4c6830428fd953f3e322434034e30ed7c993957835b45e5`
- independent exports byte-identical: PASS

### S2

- records: 13,824
- JSON SHA-256: `815e60e254f6126627caa90f568a3f14c7022860456a94246305e75376856ac0`
- gzip SHA-256: `229940087f273bf75e1c880b77798b0dd6be010eb56610fa436ef4983d9717c8`
- independent exports byte-identical: PASS

### S3

- records: 20,736
- JSON SHA-256: `acbdd76105db034954569f33360dd336c3d1027f586b2ef6b8d836bbb973057b`
- gzip SHA-256: `94557ab84c117f01a252dbee649b679e36058e4c45ead37c74f494804d45f141`
- independent exports byte-identical: PASS

S3 was executed in deterministic state shards because a monolithic raw export exceeded the local process window. Every shard reproduced identically and was assembled in the frozen state order.

The evidence bundle containing all three raw archives, the complete reference result, report and manifest is:

`AI-Watermarking-v0.8-Open-Set-Evidence-Bundle.zip`

SHA-256:

`baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

The connected GitHub interface does not expose binary attachment upload. The exact bundle is therefore retained as a connected Adobe Creative Cloud asset and identified in `RAW_EVIDENCE-v0.8.json`. This storage fact is provenance metadata, not experimental authority.

## Matrix validation

- declared core cells: 108
- calibration-feasible: 13
- calibration-infeasible: 95
- S1 feasible: 10/36
- S2 feasible: 3/36
- S3 feasible: 0/36
- published-derivative feasible: 13/36
- provenance-removed feasible: 0/36
- post-transform-chain feasible: 0/36

No infeasible cell was removed or converted into a successful result.

## Transfer validation

S1→S2:

- source threshold unavailable in 26/36 matching cells;
- median evaluated destination UFIR 21.875%;
- median KCAR 69.2708%;
- median KWAR 16.6667%;
- transfer acceptable: **false**.

S2→S3:

- source threshold unavailable in 33/36 matching cells;
- median evaluated destination UFIR 36.8056%;
- median KCAR 34.7222%;
- median KWAR 12.5%;
- transfer acceptable: **false**.

## Aggregate gate validation

`CONTROL_FAILED`: not emitted — controls/parity pass.

`FALSE_ATTRIBUTION_RISK_OBSERVED`: not emitted under the frozen matrix-wide trigger, although cell-level false attribution is present.

`OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX`: not emitted — calibration infeasibility and failed transfer alone prevent it.

`CONTEXT_DEPENDENT_OPEN_SET_CONTROL`: **emitted**.

The classification was calculated from the frozen rules; no post-result threshold or label adjustment occurred.

## Residual limitations

1. Synthetic benchmark only.
2. Deterministic transparent transforms are not deployed model/provider behavior.
3. S1/S2/S3 vary population size and seed together.
4. Score+margin abstention is one strategy, not proof of an optimal open-set detector.
5. Artifact/cell observations are repeated measures, not independent population trials.
6. Provenance-absent N1/N2 fallbacks create computationally duplicate declared cells; the frozen 108-cell denominator remains canonical.
7. No full real-world artifact→generation→session→account→person chain is modeled.
8. No production identity-resolution authority is created by this experiment.

## Validation conclusion

**PASS FOR RESULT-LEVEL DDC REVIEW AND CLEAN CANONICALIZATION, PROVIDED BRANCH/BASE DRIFT AND EVIDENCE-MANIFEST HASHES REMAIN CLEAN AT MERGE TIME.**

Validation proves the declared synthetic computation and evidence package. It does not promote the result to a validated real-world invariant or production authorization.
