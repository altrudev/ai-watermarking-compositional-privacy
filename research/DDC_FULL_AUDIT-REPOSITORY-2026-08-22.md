# DDC Full Repository Audit — 2026-08-22

**Repository:** `altrudev/ai-watermarking-compositional-privacy`  
**Audit basis:** canonical `main` at `959172facc56db3a7048caf58c6b082523389f4c`  
**Canonical v0.8 experiment:** `7cbb6d8b3e76fdd7a3bbce6db92d34442d025c5e`  
**Authority:** Root Human Authority instruction: `Run repo through ddc`  
**Audit scope:** repository-level authority, lineage, code boundary, experiment maturity, evidence custody, publication separation, licensing, branch governance, reproducibility, and next-program authority  
**Research boundary:** synthetic-only

## Executive decision

**DDC repository result: `PASS FOR CONTINUED RESEARCH USE — GOVERNANCE HARDENING REQUIRED`.**

The repository's canonical research state is internally coherent at the audited head. v0.8 is correctly recorded as a completed synthetic experiment, its adverse results remain visible, v0.9 is not implementation-authorized, publication objects are distinguished from the active research program, and the executable research code does not expose an observed network/provider/credential execution path in the reviewed repository surface.

The repository is **not** classified as fully governance-hardened because canonical-branch protection is disabled and merged/stale working branches remain available as alternate repository states. The research process is documented and was followed for v0.8, but GitHub currently does not enforce all of those transition rules at the repository-control layer.

This audit does not change the v0.8 classification, authorize v0.9, validate a deployed provider, or create identity-resolution authority.

## DDC transition model

### Authority

The user authorized a repository-level DDC audit. This authorizes inspection and recording of the audit result. It does not by itself authorize production identity-resolution work, real-person datasets, provider access, external credentials, v0.9 execution, or broad repository-security setting changes.

**PASS.**

### Intent

Determine whether the repository's current canonical state preserves authority, claim maturity, experimental lineage, adverse evidence, privacy boundaries, reproducibility evidence, and governance controls without silently turning research artifacts into production authority.

**PASS.**

### Preconditions

At audit start:

- `main` = `959172facc56db3a7048caf58c6b082523389f4c`;
- canonical v0.8 experiment = `7cbb6d8b3e76fdd7a3bbce6db92d34442d025c5e`;
- the only commit after the canonical experiment is the documentation-only lineage synchronization;
- no open pull requests were observed;
- v0.9 is present only as a candidate-scope research document.

**PASS.**

## 1. Canonical lineage and state separation

The machine-readable lineage identifies v0.1-v0.8 as experimental history and records v0.8 as:

- `experimental-open-set-false-attribution-benchmark`;
- classification `CONTEXT_DEPENDENT_OPEN_SET_CONTROL`;
- 108 core cells;
- 13 calibration-feasible cells;
- 95 calibration-infeasible cells;
- threshold transfer unsupported;
- synthetic-only lineage effect.

It also keeps `pre_execution_programs` empty and v0.9 in `candidate_research_queue` with `implementation_authorized: false`.

The public README agrees with that state and explicitly states that v0.9 requires a new Root Human Authority instruction plus a new predeclared, DDC-audited protocol.

**PASS.**

Standing distinction preserved:

> Published research object != active research program != protocol != implementation != tested result != validated invariant != production authority.

## 2. v0.8 adverse-result retention

The current result record does not optimize the narrative around the successful cells. It preserves the dominant adverse result:

- 95/108 cells were `CALIBRATION_INFEASIBLE`;
- only 13/108 cells were feasible;
- 0/36 S3 cells were feasible;
- 0/72 transformed-state cells were feasible;
- both threshold-transfer pairs failed;
- false-attribution cell-events are retained but explicitly treated as repeated measures rather than independent incidents.

The README also warns that the frozen matrix-wide false-attribution alarm not firing must not be paraphrased as `no risk` or `safe`.

**PASS.**

## 3. Claim maturity and authority boundaries

The following distinctions are consistently present in the current research method, README, result records, and candidate-scope material:

- Detection != Provenance != Attribution != Identity Resolution != Authority.
- Watermark signal != attribution evidence.
- Candidate reduction != evidence creation.
- Best match != sufficient match.
- Confidence != identity proof.
- Correlation != authorization.
- Failed re-identification != proven anonymity.
- Synthetic evidence != deployed-provider evidence.
- Experiment result != validated invariant.
- Provenance != authorship != ownership != responsibility.

No current repository record authorizes real-person attribution, private account data, provider logs, production watermark detectors, provider APIs, credentials, or identity-resolution operations.

**PASS.**

## 4. Executable research boundary

The canonical `lab/` tree contains the synthetic v0.1-v0.8 research modules and the canonical `tests/` tree contains corresponding historical and v0.8 tests.

Repository search during this audit found no occurrences of:

- `import requests`;
- `urllib`;
- `socket`;
- `subprocess`;
- `os.environ`;
- `API_KEY`;
- `BEGIN PRIVATE KEY`.

The v0.8 implementation uses deterministic local synthetic population generation, local scoring, threshold calibration, candidate filtering, and JSON/hash operations. Candidate filtering uses declared synthetic artifact metadata and does not use the truth label as a ranking input; the v0.8 controls include truth-label isolation.

**PASS BY CODE/STRUCTURE INSPECTION.**

This is not a proof that arbitrary future code cannot access external resources. It is a statement about the audited repository head.

## 5. Whole-repository execution verification

The repository documents the full-suite command:

`python -m unittest discover -s tests -v`

A network clone of the exact current head was attempted in the audit environment and failed because the sandbox could not resolve `github.com`. Therefore a fresh whole-repository test execution at `959172f...` was **not** produced in this audit environment.

Risk is reduced, but not eliminated, by the fact that the only repository transition after canonical v0.8 changes four documentation/status files and no `lab/` or `tests/` bytes. Existing v0.8 exact-byte focused execution/determinism evidence remains applicable to those unchanged experiment bytes.

**OPEN VERIFICATION GATE — MEDIUM.**

Required closure evidence:

1. clean local checkout at exact current head;
2. record Python runtime/version;
3. execute `python -m unittest discover -s tests -v`;
4. retain pass/fail count and command output digest;
5. do not use GitHub Actions as a substitute for this repository's standing local-test directive.

## 6. Evidence integrity and custody

`research/RAW_EVIDENCE-v0.8.json` records:

- exact source/test Git blobs;
- complete-reference SHA-256;
- two byte-identical reference executions;
- 44,928 raw synthetic artifact records;
- per-scenario raw/gzip hashes;
- complete bundle SHA-256 `baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`.

The evidence bundle itself is held in connected Adobe Creative Cloud asset storage rather than as a repository or immutable-public archive object.

Integrity is therefore strongly anchored by Git-recorded hashes, but availability/custody is less self-contained than the source repository.

**PASS FOR INTEGRITY; OPEN DURABILITY GATE — MEDIUM.**

Recommended closure:

- publish the exact bundle, unchanged, in an independently durable archive or release artifact;
- record its stable URL/DOI and SHA-256 in the evidence manifest;
- preserve the Adobe copy as an additional custody location rather than the only retrievable copy.

Artifact availability != artifact integrity.

## 7. Publication / active-research separation

The repository identifies the Zenodo v1.0 paper as an immutable published research object and keeps later experimental lineage in the evolving repository. The continuation publication is separately identified rather than silently rewriting the original paper.

The current README describes v0.8 as repository research state, not as retroactive content of the original v1.0 publication.

**PASS.**

## 8. Licensing and copyright

The repository has a path-specific multi-license map:

- `lab/**`, `tests/**` -> MIT;
- designated machine-readable synthetic evidence -> CC BY 4.0;
- active research prose/audits/protocols -> CC BY-NC 4.0;
- canonical publication text -> CC BY-NC-ND 4.0;
- branding rights not granted.

`LICENSE` points to `LICENSING.md`, and current citation metadata identifies Valentyn Rukhaylo / Altru.dev and the publication license. The license record explicitly distinguishes copying/adaptation permissions from authorship, endorsement, evidence maturity, and authority.

**PASS.**

## 9. External-review provenance

`research/EXTERNAL_REVIEW_LOG.md` correctly classifies public criticism as `hypothesis-generating input, not experimental evidence` and records the assumptions/research consequences separately from experimental results.

However, the current review entries name public participants and paraphrase their challenges without recording a source URL, immutable snapshot reference, or source-content hash.

This is not a claim-maturity violation, because the comments are not used as empirical evidence. It is a provenance-completeness weakness for a file whose stated purpose is research-direction provenance.

**FINDING R5 — LOW/MEDIUM.**

Recommended remediation: retain a public source URL plus access date and, where practical, an immutable snapshot/hash or local evidence reference. Paraphrase must remain distinguished from quotation.

## 10. Candidate v0.9 authority

`research/ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md` correctly states:

- candidate research direction only;
- implementation authorization: NO;
- reference execution authorization: NO;
- synthetic-only scope;
- no claim that deployed providers use user/session/cohort-specific keying.

A stale closing sentence still says the permitted next transition is the already-authorized v0.8 implementation path, even though v0.8 is now completed.

This does not grant v0.9 authority, but it contradicts current repository state.

**FINDING R2 — MEDIUM. REPAIR AUTHORIZED AS LINEAGE CORRECTION.**

Correct transition wording:

> v0.8 is closed. The next permitted v0.9 transition is protocol predeclaration only after a new Root Human Authority instruction; implementation and execution remain unauthorized until that protocol passes DDC.

## 11. Canonical branch enforcement

GitHub reports `main` as `protected: false` at the audited head.

This is the most important repository-governance defect found in this audit. The research method requires predeclaration, audit, evidence preservation, claim review, and lineage update, but an unprotected `main` permits repository changes outside those procedural controls.

A successful audited process != enforced repository governance.

**FINDING R1 — HIGH.**

Recommended repository rule, without GitHub Actions:

- require changes to `main` through pull requests;
- block force pushes;
- block branch deletion;
- restrict direct writes to the minimum Root Human Authority/admin set;
- optionally require signed commits/merges where operationally practical;
- do not require GitHub Actions status checks, consistent with the standing no-GitHub-Actions directive.

Authority documentation != authority enforcement.

## 12. Branch-state hygiene

The repository currently retains numerous historical working branches, including merged implementation, protocol, audit, publication, and canonicalization branches. Some are useful historical evidence; others are stale alternate heads after their canonical state has already merged.

Because at least one historical v0.8 working branch contained an invalid intermediate wrapper state before repair, keeping all working branches indefinitely increases the chance that a stale/noncanonical state is mistaken for an active research head.

**FINDING R3 — MEDIUM.**

Recommended remediation:

- retain `main` as the sole canonical active head;
- delete merged ephemeral working branches after their merge commits preserve history; or
- if branch retention is required for research history, rename/prefix retained branches as explicit `archive/` noncanonical states and document that convention.

Branch existence != canonical authority.

## 13. Runtime reproducibility declaration

The README states that the labs use the Python standard library but does not declare a supported/minimum Python runtime. Current source uses modern Python type syntax, so reproducibility depends on an unstated interpreter floor.

This audit does not infer a supported version merely from syntax.

**FINDING R6 — LOW/MEDIUM.**

Recommended remediation after a clean test run: record the tested Python version and minimum supported version in the README/research method.

## Findings register

| ID | Severity | Finding | Current consequence |
|---|---|---|---|
| R1 | HIGH | `main` is unprotected | DDC process is documented but not fully repository-enforced |
| R2 | MEDIUM | stale v0.9 closing transition sentence | lineage contradiction; no authority expansion |
| R3 | MEDIUM | numerous stale/merged working branches remain | alternate-state confusion / accidental stale-base risk |
| R4 | MEDIUM | no fresh whole-repo exact-head test in this audit environment | current whole-repo regression proof remains open |
| R5 | LOW/MEDIUM | external-review provenance lacks source URL/snapshot/hash | weaker independent verification of research-direction provenance |
| R6 | LOW/MEDIUM | supported Python runtime not declared | reproducibility environment assumption remains implicit |
| R7 | MEDIUM | raw evidence bundle is external-only custody | integrity anchored; long-term/public availability not self-contained |

## Positive controls / passes

- canonical experimental head is explicitly identified;
- post-v0.8 main change is documentation-only;
- no open pull requests observed during audit;
- v0.9 code is absent from the canonical `lab/` tree;
- v0.9 remains non-authorized;
- synthetic-only boundary is preserved;
- no observed network/provider/credential code path in repository search;
- v0.8 adverse evidence is retained;
- false-attribution events are not represented as independent real incidents;
- failed transfer is retained rather than tuned away;
- publication and active research are separated;
- external criticism remains non-evidence;
- license != authorship/authority is explicit;
- copyright/author attribution is consistent with Valentyn Rukhaylo / Altru.dev.

## Final DDC state

### Research content

**PASS.**

### Experimental lineage

**PASS**, subject to repairing R2 stale wording.

### Privacy / identity authority boundary

**PASS.**

### Evidence integrity

**PASS**, with R7 durability gate open.

### Reproducibility

**PARTIAL PASS**, with R4 and R6 open.

### Repository governance enforcement

**NOT FULLY HARDENED**, due primarily to R1 and secondarily R3.

### v0.9

**NOT AUTHORIZED.**

## Permitted next transitions

Under the authority that created this audit, only evidence/lineage corrections are implicit. The audit itself does not authorize broader security-setting changes or v0.9 execution.

Permitted without changing research semantics:

1. repair the stale v0.9 closing transition sentence;
2. link this repository-level audit from the research index;
3. run the full local test suite in a clean exact-head environment and append a verification record;
4. separately request/approve repository-governance hardening for branch protection and branch cleanup;
5. separately archive the v0.8 evidence bundle into durable independent storage.

A new v0.9 protocol requires a new Root Human Authority instruction.