# Full DDC Audit — v0.8 Open-Set / False-Attribution Protocol

**Status:** full pre-execution audit with required protocol repair  
**Audited canonical protocol head:** `7ed99ac13e39946b2853c2b4e4ddf4193728bce9`  
**Canonical harness checked:** `lab/transformation_chain_lab.py`, blob `30b9bde830eaa8f00771957d50ed78d21979fa49`  
**Normative repair:** `research/TEST_PLAN-v0.8-AMENDMENT-1.md`  
**Claim repair:** `research/CLAIM_REGISTER-v0.8-AMENDMENT-1.md`  
**Result status during audit:** no v0.8 implementation/reference result existed

## Executive result

The original v0.8 protocol is **inside the authorized synthetic research boundary** and its central research question is valid, but the initial protocol-only audit was not sufficient for execution authorization.

The full audit found multiple pre-result methodological defects that could create ambiguous or misleading outcomes. None requires authority expansion, real data, new privileges, external provider access, or a change to the research purpose. They are safe pre-execution protocol repairs.

**Full DDC result before repair:** `NOT EXECUTION-AUTHORIZED`  
**Full DDC result with Amendment 1 applied:** `PASS FOR IMPLEMENTATION, SUBJECT TO EXACT IMPLEMENTATION/TEST AUDIT BEFORE REFERENCE EXECUTION`

The experiment may not generate a canonical v0.8 result from the base protocol alone.

---

## 1. Governed transition audit

### Authority

Root Human Authority authorized publication closure and the next synthetic research phase. This authority covers protocol design, synthetic implementation, deterministic test execution, and evidence recording inside the existing repository boundary.

**PASS.**

### Intent

Test whether a synthetic attribution matcher can distinguish represented from unrepresented synthetic sources, abstain when evidence is insufficient, and expose false-attribution behavior under different evidence/narrowing conditions.

**PASS.**

### Preconditions / assumptions

The base protocol assumes:

- K/U-cal/U-test person separation;
- known calibration and known holdout artifacts;
- canonical six-channel scoring semantics;
- deterministic candidate narrowing;
- score/margin abstention;
- threshold calibration isolated from holdout results.

The full audit found that not all of these assumptions were operationally specified.

**FAIL before repair; PASS with Amendment 1.**

### Execution boundary

Synthetic people/accounts/sessions/generations/artifacts only. No real people, provider logs, private conversations, scraped identity corpora, production detectors, proprietary APIs, credentials, or external identity resolution.

**PASS.**

### Proposed transition

Move from protocol-only state to implementation and test generation while preserving rules-before-results.

**BLOCKED before repair; permitted after Amendment 1 becomes canonical.**

### Affected state / resources

Research code, tests, machine-readable synthetic evidence, claim register, validation records, and later H/R Native research lineage only.

No production identity authority or execution privilege is affected.

**PASS.**

### Verification boundary

Implementation must prove protocol identity, cohort isolation, scorer parity, deterministic replay, negative controls, evidence retention, and no holdout leakage before a reference result is accepted.

**PASS after repair.**

### Commit / recovery

If implementation violates the base protocol plus Amendment 1, the candidate must not merge and any generated result is non-canonical. Recovery is to the last canonical pre-result protocol state, not threshold retuning.

**PASS.**

---

## 2. Authority and privacy checks

### Need ≠ Authority

The research need does not grant access to real identity systems.

**PASS.**

### Detection ≠ Provenance ≠ Attribution ≠ Identity Resolution ≠ Authority

The protocol preserves these transitions as distinct.

**PASS.**

### Candidate narrowing ≠ authority

Filtering simulated candidates is an analytical operation only.

**PASS.**

### Confidence ≠ identity proof

The protocol treats score/margin as decision evidence, not proof.

**PASS.**

### Unknown rejection ≠ anonymity

Explicitly preserved.

**PASS.**

### Synthetic evidence ≠ deployed-provider evidence

Explicitly preserved.

**PASS.**

### Correlation ≠ authorization

Explicitly preserved.

**PASS.**

No authority/privacy expansion was found.

---

## 3. Harness-to-protocol compatibility audit

The canonical harness defines:

- `Generation`: person/account/session/generation IDs, provider, model, created minute, watermark family, topic, text;
- `Artifact`: target generation ID, text, published minute, `provider_hint`, `watermark_family`;
- watermark family as the synthetic string `provider:model`;
- historical scorer channels: lexical, semantic, style, watermark, provider, timing;
- `paraphrase_stage` and `multi_model_edit_stage` remove provider/watermark provenance.

### Finding F8-01 — protocol named a separate model field that Artifact does not contain

**Severity:** medium / execution-ambiguity.  
**Class:** safe local protocol repair.

The base N1 wording referred to provider/model provenance, while the canonical artifact exposes only `provider_hint` and `watermark_family`. The model is encoded inside watermark family rather than stored separately.

**Repair:** Amendment A2 binds narrowing to the actual schema and forbids invented external model data.

**Status:** repaired pre-result.

---

## 4. Calibration / holdout integrity audit

### Finding F8-02 — known calibration/holdout split was undefined

**Severity:** critical / merge-blocking reproducibility defect.  
**Class:** safe protocol repair.

The base protocol uses “known calibration artifacts” and “known holdout artifacts” but never specifies how K artifacts are partitioned. Different implementations could therefore produce different thresholds and outcomes while claiming protocol compliance.

**Repair:** Amendment A1 freezes `-gen-0` as known calibration and `-gen-1` as known holdout, with all K generations still present in the candidate database and explicit per-person partition assertions.

**DDC rule:** Calibration ≠ validation; undefined partition ≠ reproducible evidence.

**Status:** repaired pre-result.

---

## 5. Abstention semantics audit

### Finding F8-03 — single-candidate margin created synthetic confidence from comparator removal

**Severity:** high / merge-blocking validity defect.  
**Class:** safe protocol repair.

The base protocol defined a one-candidate margin as top-1 score against implicit zero. Candidate narrowing could therefore increase the margin simply by deleting all competitors, causing comparison-set reduction to masquerade as stronger evidence.

**Repair:** Amendment A3 requires primary abstention for candidate counts 0 or 1. Raw single-candidate score remains a diagnostic but cannot satisfy the primary acceptance rule.

**DDC rules:** Candidate reduction ≠ evidence creation; Best match ≠ sufficient match.

**Status:** repaired pre-result.

---

## 6. Candidate-filter evidence audit

### Finding F8-04 — target presence after filtering was not retained

**Severity:** medium-high / attribution-causality ambiguity.  
**Class:** safe evidence repair.

The base record says whether the target person belongs to K but not whether narrowing removed the true person/generation. Without that evidence, a known-case failure could be misclassified as scorer failure or threshold rejection when the candidate filter made success impossible.

**Repair:** Amendment A4 adds target-presence-after-filter fields and true-person/generation filter-exclusion rates.

**Status:** repaired pre-result.

---

## 7. Provenance fail-open audit

### Finding F8-05 — partial/inconsistent provenance behavior was unspecified

**Severity:** medium-high / fail-open ambiguity.  
**Class:** safe protocol repair.

The historical harness normally removes provider and watermark together, but the protocol did not define behavior if only one provenance field were present or the pair were inconsistent. A silent fallback to N0 would widen the search space after malformed provenance.

**Repair:** Amendment A2 defines complete/absent provenance and requires `CONTROL_FAILED` for partial or inconsistent synthetic provenance. Amendment C6 tests fail-closed behavior.

**DDC rule:** Invalid evidence state ≠ authority to broaden execution.

**Status:** repaired pre-result.

---

## 8. Transfer-validation audit

### Finding F8-06 — transfer gate allowed reject-everything success

**Severity:** critical / aggregate-claim defect.  
**Class:** safe claim/protocol repair.

The base transfer test reports UFIR/KCAR/KWAR but the positive aggregate gate used only transferred median UFIR. A threshold transferred to a new scenario could therefore reject nearly everything, produce low UFIR, and still satisfy the transfer portion of the positive claim.

**Repair:** Amendment A6 requires both transfer pairs to satisfy median destination UFIR <=10%, KCAR >=30%, and KWAR <=10%.

**DDC rule:** Reject everything ≠ open-set success.

**Status:** repaired pre-result.

---

## 9. Aggregate-classification audit

### Finding F8-07 — positive and risk labels could overlap

**Severity:** high / claim ambiguity.  
**Class:** safe claim repair.

The base T9 does not define precedence if broad control conditions and the high-score false-attribution condition are simultaneously satisfied.

**Repair:** Amendment A7 makes labels mutually exclusive with precedence:

`CONTROL_FAILED > FALSE_ATTRIBUTION_RISK_OBSERVED > OPEN_SET_CONTROL_SUPPORTED_FOR_DECLARED_MATRIX > CONTEXT_DEPENDENT_OPEN_SET_CONTROL`.

**Status:** repaired pre-result.

### Finding F8-08 — high-score aggregate trigger had an unstable denominator

**Severity:** high / small-count amplification defect.  
**Class:** safe metric repair.

The base trigger used the fraction of accepted false events that were high-score. If exactly one false event occurred and it was high-score, the fraction would be 100%, potentially promoting a matrix-level risk label from one event.

**Repair:** Amendment A5 defines HS-UFIR over all U-test artifacts per cell and uses a matrix-coverage trigger: at least 10% of core cells with HS-UFIR >=5%.

Individual high-score false events remain fully retained.

**Status:** repaired pre-result.

---

## 10. Repeated-measures / evidence-population audit

### Finding F8-09 — artifact-level rates could be mistaken for independent population evidence

**Severity:** medium / interpretation defect.  
**Class:** safe reporting repair.

Each synthetic person contributes multiple correlated generations/artifacts, and the same artifacts are re-evaluated across policies and narrowing modes. Artifact rates and percentages of 108 cells are therefore not independent population trials.

**Repair:** Amendment A8 adds UPER, per-person UFIR/KCAR distributions, and explicitly classifies core-cell percentages as design-surface coverage rather than inferential probabilities.

**Status:** repaired pre-result.

---

## 11. Threshold provenance audit

### Finding F8-10 — calibration decision provenance was under-specified

**Severity:** medium / evidence traceability defect.  
**Class:** safe evidence repair.

The base protocol freezes a threshold grid and selection rule but does not require enough machine-readable calibration evidence to independently reconstruct why a specific threshold pair won.

**Repair:** Amendment A9 requires calibration counts, feasible-set evidence/digest, selected thresholds, selected calibration metrics, high-score reference, candidate-count distribution, and feasibility status, with no holdout outcomes in the calibration record.

**Status:** repaired pre-result.

---

## 12. Rules-before-results / lineage audit

### Finding F8-11 — implementation was not required to bind itself to the exact protocol lineage

**Severity:** medium-high / lineage-evidence defect.  
**Class:** safe test repair.

A later implementation could theoretically claim v0.8 compliance without recording which pre-result protocol bytes governed it.

**Repair:** Amendment A10 requires the implementation/tests to embed and report both the base protocol commit and the canonical Amendment-1 commit.

**DDC rule:** Protocol name ≠ protocol bytes.

**Status:** repaired pre-result.

---

## 13. Security / leakage audit

The base leakage guards are strong and are retained:

- K/U-cal/U-test person disjointness;
- unknown IDs absent from candidate database;
- target IDs prohibited from scoring features;
- person-disjoint U-cal/U-test;
- synthetic `syn-` namespace;
- truth-label score independence;
- candidate exclusion control;
- deterministic replay.

Amendment 1 adds:

- single-candidate comparator control;
- partial-provenance fail-closed control;
- known partition immutability control.

**PASS with amendment.**

---

## 14. Claim-maturity audit

The base claim register correctly prevents:

- deployed-provider attribution claims;
- real-user identity claims;
- provider-log knowledge claims;
- authorship/ownership/responsibility/guilt claims;
- legal authority claims;
- anonymity claims;
- real-world prevalence extrapolation.

Claim Amendment 1 additionally prevents:

- comparator removal being described as stronger evidence;
- transfer rejection being described as successful transfer;
- overlapping aggregate labels;
- artifact-level repeated measures being treated as real population evidence.

**PASS with amendment.**

---

## 15. Residual limitations accepted before implementation

The following remain legitimate limitations, not protocol defects:

1. synthetic-only benchmark; no real-world prevalence inference;
2. deterministic transparent transforms are not production LLM/provider behavior;
3. S1/S2/S3 vary size and seeds together, so pool-size observations are not pure causal estimates;
4. score+margin thresholding is one abstention strategy, not a claim of optimality;
5. the benchmark does not yet model the full artifact→generation→session→account→organization→person chain;
6. candidate database includes source generations for known cases, preserving historical closed-set scorer semantics rather than modeling every operational retention policy;
7. 108 core cells are a declared design matrix, not 108 independent statistical trials.

These limitations must remain in results and publication.

---

## 16. Final DDC gate

### Authority
PASS.

### Synthetic-only privacy boundary
PASS.

### No new identity-resolution authority
PASS.

### No real data / provider access
PASS.

### Rules before results
PASS, provided Amendment 1 is canonical before implementation/reference execution.

### Reproducible partitions
PASS with Amendment A1.

### Fail-closed malformed provenance
PASS with Amendment A2/C6.

### Abstention semantics
PASS with Amendment A3/C5.

### Candidate-filter causality evidence
PASS with Amendment A4.

### High-score risk metric
PASS with Amendment A5.

### Transfer utility gate
PASS with Amendment A6.

### Aggregate label exclusivity
PASS with Amendment A7.

### Repeated-measures interpretation
PASS with Amendment A8.

### Calibration provenance
PASS with Amendment A9.

### Exact protocol lineage binding
PASS with Amendment A10.

### Historical v0.1-v0.7 integrity
No historical experiment/result file change is required by this audit.

## Final authorization state

**The v0.8 base protocol alone is not execution-authorized.**

**The v0.8 base protocol + Amendment 1 + Claim Amendment 1 pass the full pre-execution DDC audit and may proceed to implementation.**

This authorization does not authorize a result claim. The exact implementation candidate must still undergo source review, leakage tests, scorer parity, deterministic controls, evidence-package verification, and exact-byte DDC audit before a canonical reference run is accepted.