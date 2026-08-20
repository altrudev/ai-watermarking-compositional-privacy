# DDC Research-Chain Audit — v0.1 through v0.5

**Audit date:** 2026-08-20  
**Canonical research head audited:** `43d4b97a1c9b53a73de079ac166134fba663f494`  
**Scope:** synthetic research artifacts v0.1–v0.5 only  
**Purpose:** evaluate claim/evidence boundaries, transition lineage, validation semantics, experimental controls, and promotion risk without rewriting historical experiment records.

## DDC framing

This audit applies the transition chain:

`Authority → Intent/Requirement → Preconditions/Assumptions → Execution Boundary → Proposed Transition → Affected State/Resources → Execution → Verification → Invariant Preservation → Evidence → Consequences/Lineage → Commit or Recovery`

Standing distinctions retained throughout:

- **Published research object ≠ active research program ≠ experiment ≠ experimental result ≠ validated invariant**
- **Privacy transformation ≠ privacy evidence**
- **Failed re-identification ≠ proven anonymity**
- **Intermediate unlinkability ≠ end-to-end unlinkability**
- **Transformation set ≠ transformation history ≠ privacy outcome**
- **Single benchmark result ≠ robust system property**
- **Synthetic closed-set attribution ≠ real-world identity resolution**
- **Test command recorded ≠ complete test-suite evidence unless execution scope is proven**

## Executive finding

The v0.1–v0.5 chain is internally coherent as a **synthetic, closed-set, progressively strengthened privacy/linkability research program**. Each successive experiment narrows or challenges an earlier interpretation rather than silently upgrading it into a universal claim. Negative results are retained, and v0.5 includes a commuting-order negative control and an explicit failure condition (`strength_0.50`).

The audit does **not** identify evidence that the repository claims real-person attribution, proprietary watermark reverse engineering, deployed-provider behavior, or universal anonymity.

The audit does identify evidence-description and robustness limitations that must remain explicit before stronger promotion.

## Canonical experiment lineage

| Experiment | Canonical merge/accepted commit | Primary maturity |
|---|---|---|
| v0.1 abstract unlinkability | `808f070c3896ce60a8a309054a6149fbdab0ad65` | experimental synthetic benchmark |
| v0.2 actual synthetic text | `e9d84a5558824644f3f1b03720e43cca0da7c670` | experimental synthetic-text benchmark |
| v0.3 transformation-chain persistence | `c560299e9cbd5c4c34dcbf146cc65bc0e497265d` | experimental synthetic-text benchmark |
| v0.4 path dependence | `b88eb87eb4a1d814c177e61d2147daed0a95e6d0` | experimental synthetic path-order benchmark |
| v0.5 robustness matrix | `43d4b97a1c9b53a73de079ac166134fba663f494` | experimental synthetic robustness benchmark |

The immutable publication in Zenodo and the evolving GitHub experiment lineage are separate objects. These commit identities describe the active research program, not revisions of the original published paper.

## Findings

### A1 — Historical validation transcript scope is ambiguous

**Severity:** evidence-description / medium  
**Disposition:** preserve history; clarify prospectively

Some historical validation records print a command equivalent to:

`python -m unittest discover -s tests -v`

while the reported count corresponds to a version-focused suite (for example 12/12 or 15/15). As the repository accumulates additional test modules, the literal command text alone must not be treated as proof that every test existing at the later canonical head was executed in that historical run.

DDC interpretation:

> **Recorded command ≠ proven execution scope.**

The historical validation files should not be rewritten to manufacture stronger evidence. Their correct maturity is **focused exact-source/version validation unless an archived execution transcript proves broader scope**.

Future validation records should distinguish explicitly:

- focused version suite;
- dependency regression slice;
- whole current repository suite;
- clean-checkout reproduction.

### A2 — No single current cross-version whole-suite evidence record is canonical

**Severity:** validation completeness / medium

The program has good additive version-level validation, including v0.3→v0.4 dependency regression and v0.5 predecessor parity. However, there is not yet one canonical evidence record demonstrating an independently executed whole-current-repository suite across all experiment versions from one exact checkout.

This does not invalidate version-level results. It limits the maturity of the **integrated repository** claim.

Required future evidence:

1. exact canonical commit;
2. clean checkout or equivalent exact-source materialization;
3. discovered test-file count;
4. executed test count;
5. pass/fail result;
6. Python version/environment;
7. report hash or preserved transcript where practical.

### A3 — All current identity attribution is closed-set forced-choice

**Severity:** claim-boundary / high if omitted, acceptable while explicit

Every current experiment evaluates an artifact against a known synthetic candidate population. The correct interpretation is **closed-set attribution**. The benchmark does not test:

- whether the true person is absent from the candidate set;
- abstention/rejection thresholds;
- open-set identification;
- unknown-person handling;
- population prevalence;
- calibration against unrelated background corpora.

Therefore:

> **Closed-set top-1 attribution ≠ open-set human identification.**

This boundary should be retained in all future summaries and H/R Native ingestion.

### A4 — v0.1 `false_attribution_rate` is a closed-set person error rate

**Severity:** terminology / medium

In v0.1, `false_attribution_rate` is calculated as `1 - person_top1`. Under forced-choice closed-set evaluation, that quantity is the **person top-1 error rate**. It is not a general false-attribution rate in the open-set/detection sense because there is no negative class or abstention decision.

Historical schema should remain stable, but future reports should label or annotate this field as closed-set person error.

### A5 — v0.5 robustness is scenario-weighted, not family-balanced

**Severity:** robustness interpretation / medium

The v0.5 headline `12/13 (92.31%)` counts declared scenarios equally. The declared matrix contains multiple policy variants and fewer instances of some other perturbation families. The result therefore supports exactly:

`ROBUST_IN_DECLARED_MATRIX`

It does not establish a family-balanced 92.31% robustness probability.

Future robustness work should additionally report:

- result by perturbation family;
- family-balanced summary;
- number of independent seeds/samples per family.

### A6 — Stress scenarios use a deterministic 18-artifact sample without uncertainty intervals

**Severity:** statistical/robustness limitation / medium

The v0.5 canonical parity case evaluates all 144 artifacts; stress scenarios use an evenly spaced deterministic sample of 18 artifacts while retaining the full candidate population. That is valid for the declared benchmark, but top-1 rates are correspondingly coarse and no resampling/uncertainty estimate is supplied.

Before promoting a quantitative effect-size claim beyond the declared matrix, add multiple predeclared artifact samples or an uncertainty procedure.

### A7 — Materiality threshold is an engineering benchmark threshold, not statistical significance

**Severity:** boundary confirmation / low

v0.5 defines materiality as:

`max(person_top1) - min(person_top1) >= 1 / persons`

The test plan correctly states this is not a statistical-significance or legal-anonymity definition. That distinction must be preserved.

### A8 — Provider-side source corpus and public-observer profile corpus must remain distinct

**Severity:** evidence-scope / medium

The text experiments compare artifacts against synthetic generation/profile material derived from the known candidate population. That is consistent with the declared provider/provider+publisher threat model. It would become evidence leakage if the same setup were later described as a public observer having only independently available profile evidence.

Any future public-observer experiment should create a separate profile/training corpus and a held-out publication corpus.

### A9 — v0.4/v0.5 demonstrate path effects but do not isolate mechanism

**Severity:** research gap / expected

v0.4 shows order-dependent outcomes. v0.5 demonstrates persistence across most of its declared matrix and includes a commuting negative control. This makes non-commutativity a plausible mechanism, but it does not yet identify which state/channel changes predict the privacy consequence.

A bounded v0.6 mechanism experiment is justified if it is designed before results are observed.

Recommended question:

> Can the privacy consequence of transform order be predicted from measurable non-commuting changes to lexical, semantic, style, timing, provenance, or artifact-state channels before running the full attribution attack?

### A10 — Exact lineage metadata is uneven across historical versions

**Severity:** provenance hygiene / low-medium

v0.5 records exact SHA-256 values for key result artifacts. Earlier versions retain canonical Git commits and validation documents but do not all expose the same uniform machine-readable experiment-manifest structure.

The additive `EXPERIMENT_LINEAGE-v0.1-v0.5.json` introduced alongside this audit records canonical experiment commits without altering historical result files.

### A11 — Experiment date and repository merge time are separate provenance dimensions

**Severity:** provenance semantics / low

Research documents use an August 18 experiment/publication date while some canonical repository merge commits occur later. This is not inherently contradictory. Future machine-readable records should use separate fields such as `experiment_date`, `record_created_at`, and `canonical_commit/merged_at` instead of overloading one date.

## Strengths confirmed by audit

1. Synthetic-only authority boundary is repeated in plans, code, claims, and results.
2. No proprietary watermark detector is represented as implemented.
3. Negative results are retained rather than tuned away.
4. v0.3 rejects a successful final unlinkability claim when attribution re-emerges.
5. v0.4 controls the transformation multiset and final metadata while varying order.
6. v0.5 includes exact predecessor parity before making a robustness claim.
7. v0.5 includes an equivalent/commuting-order negative control.
8. v0.5 preserves a non-material half-strength scenario instead of discarding it.
9. Result documents repeatedly distinguish synthetic benchmark evidence from deployed-provider behavior.
10. Claim registers explicitly reject universal anonymity and real-provider attribution claims.

## DDC promotion gate

Current research may be ingested into H/R Native as **experimental evidence with exact lineage**. It must not automatically become constitutional or executable policy.

Safe design implications to evaluate:

- privacy state may depend on ordered transformation lineage;
- privacy claims require perturbation/negative-control evidence before system-level promotion;
- closed-set attribution results require explicit candidate-set semantics;
- derived sensitivity may change after transformations even when final metadata is identical.

Not authorized by this audit:

- real-person testing;
- provider-log ingestion;
- proprietary detector use;
- universal anonymity claims;
- constitutional promotion;
- automated identity resolution.

## Next permitted research transition

If the integrated H/R Native audit finds no blocking authority/privacy defect, a v0.6 synthetic-only mechanism experiment may proceed under a **predeclared protocol** with commuting and non-commuting controls, exact-source validation, and preservation of negative results.
