# Full DDC Audit — Repository Research-State Update

**Audit date:** 2026-08-22  
**Base repository head:** `459e49c296cf77c737098115468e35b52061c041`  
**Audited content head:** `5a6e570e837d0c7e41a102de71ecf32d63bc84d8`  
**Review vehicle:** pull request #12  
**Change class:** documentation / research-governance / lineage only  
**Executable code changed:** no  
**Historical result files changed:** no  
**Frozen v0.8 protocol or claim gates changed:** no

The audit record itself is added after the audited content head and is evidence-only. It does not change the research method, experiment protocol, implementation, tests, or result state described below.

## Executive result

**DDC result for this repository update: `PASS FOR MERGE`**

The change repairs the public repository state, documents the research method exposed by the recent technical discussion, records external criticism without promoting it into evidence, extends experiment lineage through the current v0.8 pre-execution state, and records the v0.9 direction as a non-authorized candidate only.

The update does **not** authorize a v0.8 canonical reference run and does **not** authorize v0.9 implementation.

One pre-existing licensing-scope ambiguity is retained as an advisory because resolving it would change legal/licensing state beyond the authorized research-documentation transition.

---

## 1. Authority

The authorized intent was to update the repository based on the current watermarking discussion while using DDC methodology and performing a full audit.

Permitted transition:

- improve research documentation;
- preserve and expose current experiment lineage;
- record external challenge provenance;
- formulate future synthetic research questions;
- correct stale public status.

Not implicitly authorized:

- real-person research;
- access to private provider data;
- secret-key acquisition;
- production identity resolution;
- rewriting historical experimental results;
- skipping the v0.8 execution gate;
- turning public comments into evidence or endorsement.

**Result: PASS.**

## 2. Intent preservation

The repository's central proposition remains unchanged: a provenance signal can be non-identifying in isolation and still participate in a broader identifying system.

The update does not strengthen that proposition into a claim that a deployed provider performs user attribution. Instead, it adds two narrower research questions:

1. what marginal attribution value does provenance add under different auxiliary-evidence conditions;
2. how do key scope and architectural auditability change the privacy analysis.

**Result: PASS.**

## 3. Finding F-01 — public README was behind the actual research state

**Severity:** medium / public-state integrity.  
**Observed state:** the root README described experiments only through v0.5 while canonical results existed through v0.7 and the v0.8 protocol had already passed a full pre-execution audit.

**Repair:** README now distinguishes:

- completed experimental lineage v0.1-v0.7;
- v0.8 as the current governed pre-execution program;
- v0.9 as a candidate research direction only.

No historical result file was rewritten.

**Result: repaired.**

## 4. Finding F-02 — experiment-sequence leap risk

**Severity:** high / lineage-governance.  
**Risk:** the new discussion could have been turned immediately into a v0.9 implementation even though v0.8 is only implementation-authorized and has no canonical reference result.

**Repair:** `ATTRIBUTION_BOUNDARY-v0.9-CANDIDATE.md` explicitly states:

- not a protocol;
- implementation not authorized;
- canonical execution not authorized;
- v0.8 must be closed or explicitly superseded through a separate governed transition first.

**DDC rule:** question != protocol != implementation != result.

**Result: repaired.**

## 5. Finding F-03 — external criticism could be misclassified as evidence

**Severity:** high / research-provenance and claim-maturity.  
**Risk:** technically useful comments from Elton Willis and Guillaume Meyer could be presented as validation, endorsement, or empirical support.

**Repair:** `EXTERNAL_REVIEW_LOG.md` classifies the discussion as **hypothesis-generating input, not experimental evidence** and records the exact research consequence of each challenge.

The log explicitly does not claim endorsement, deployed-provider behavior, user-specific keying, or public-detector identity disclosure.

**Result: repaired.**

## 6. Finding F-04 — marginal provenance contribution was not isolated

**Severity:** medium-high / causal interpretation.  
**Challenge:** if stronger telemetry already determines attribution, the watermark may contribute little additional evidence.

**Repair:** the future candidate scope requires comparisons between otherwise identical evidence states with and without provenance. The primary future question becomes the **marginal contribution** of provenance rather than only the final combined attribution rate.

No result is claimed before a future predeclared experiment.

**DDC rule:** combined success != causal contribution of each signal.

**Result: research question repaired; evidence pending.**

## 7. Finding F-05 — key secrecy and architectural secrecy were conflated

**Severity:** medium-high / privacy-auditability.  
**Challenge:** a public detector can expose less information than the internal key architecture distinguishes, while publishing the secret key may weaken some watermark designs.

**Repair:** the repository now preserves:

- **Key secrecy != architectural secrecy.**
- **Detector behavior != internal watermark architecture.**
- **Provider assertion != independently verified privacy property.**

The v0.9 candidate proposes separate synthetic conditions for key scope and separate transparency conditions for documented or verifiable architecture without assuming secret-key publication.

No claim is made that a deployed provider uses any synthetic key scope.

**Result: repaired.**

## 8. Finding F-06 — machine-readable lineage stopped at v0.5

**Severity:** medium / provenance integrity.  
**Observed state:** `EXPERIMENT_LINEAGE-v0.1-v0.5.json` was a correct historical snapshot but no newer lineage object connected v0.6, v0.7, and the v0.8 pre-execution program.

**Repair:** added `EXPERIMENT_LINEAGE-v0.1-v0.8.json` while preserving the v0.1-v0.5 file unchanged.

The new lineage records:

- v0.6 local mechanism classification;
- v0.7 negative replication classification and its narrowing effect on v0.6;
- v0.8 as pre-execution rather than a completed experiment;
- v0.9 as a candidate queue item rather than an experiment.

**DDC rule:** historical snapshot != mutable current alias.

**Result: repaired.**

## 9. Publication immutability audit

The original `paper.md`, root `CITATION.cff`, and continuation publication files were not edited.

This is important because the new discussion changes the active research direction but does not retroactively change what the earlier papers said or what evidence existed when they were published.

**Result: PASS.**

## 10. Claim-maturity audit

The new files preserve the existing nonclaim discipline:

- no deployed-provider identity claim;
- no real-user re-identification claim;
- no provider-log knowledge claim;
- no secret-key disclosure claim;
- no authorship/ownership/responsibility inference from provenance;
- no claim that external reviewers endorse the project;
- no claim that a future v0.9 hypothesis is already supported.

The README also preserves the v0.7 adverse result rather than summarizing only v0.6's strong local result.

**Result: PASS.**

## 11. v0.8 protocol integrity audit

The following frozen v0.8 files are unchanged by this update:

- `research/TEST_PLAN-v0.8.md`;
- `research/TEST_PLAN-v0.8-AMENDMENT-1.md`;
- `research/CLAIM_REGISTER-v0.8-PREDECLARED.md`;
- `research/CLAIM_REGISTER-v0.8-AMENDMENT-1.md`;
- `research/DDC_FULL_AUDIT-v0.8-PROTOCOL.md`;
- `docs/programs/OPEN_SET_FALSE_ATTRIBUTION-v0.8.json`.

The existing program record still requires an exact implementation audit before any canonical reference run.

**Result: PASS.**

## 12. Executable/source security audit

This update changes no executable files.

Repository inspection confirmed the current lab surface is Python and uses local modules plus Python standard-library facilities in the inspected source. The repository root contains no dependency manifest requiring third-party package installation for the declared labs.

Static repository searches performed during this audit returned no matches for:

- `BEGIN PRIVATE KEY`;
- `api_key`;
- `subprocess`;
- `requests`;
- `eval(`;
- `exec(`;
- `socket`;
- `pickle`.

The inspected lab sources use deterministic/local computation patterns rather than network or shell execution paths.

**Important limitation:** these searches are a static repository check, not a substitute for a dedicated secret-scanning or SAST engine.

**Result: PASS for the documentation-only transition; no new executable attack surface introduced.**

## 13. Test and validation audit

The connected GitHub environment used for this update does not provide repository code execution. A separate local clone attempt was unavailable because the isolated execution environment could not resolve GitHub network access.

Therefore this audit does **not** falsely claim that the full Python suite was re-executed for this documentation patch.

Relevant preserved evidence:

- v0.7 validation records Python compilation PASS;
- focused v0.7 regression + diagnostics: **15/15 PASS**;
- historical scorer parity: PASS;
- matrix scorer parity: PASS;
- deterministic aggregate reproduction: PASS.

Because the audited change set modifies no `lab/` or `tests/` files, those executable bytes remain unchanged by this transition.

The absence of a fresh runtime execution does not authorize v0.8 execution; the v0.8 implementation gate remains fully active.

**Result: PASS for documentation merge, with explicit execution limitation retained.**

## 14. Data/privacy boundary audit

No real people, real accounts, private conversations, provider logs, production detector secrets, credentials, or external identity datasets were introduced into the change set.

Named participants appear only as attribution for their public technical criticism in the external review log. Their comments are not promoted into endorsement or experiment evidence.

**Result: PASS.**

## 15. Resource and operational audit

The update adds Markdown/JSON documentation only. It introduces no background workers, network calls, scheduled jobs, services, storage loops, external APIs, or runtime dependencies.

Operational resource effect is negligible.

**Result: PASS.**

## 16. Recovery / rollback audit

The update was developed on branch:

`ddc/research-method-attribution-boundary-20260822`

from exact base:

`459e49c296cf77c737098115468e35b52061c041`

The base remains a complete recovery point. The update does not require migration or destructive state change.

**Result: PASS.**

## 17. Pre-existing advisory — license scope ambiguity

**Severity:** medium advisory / legal-documentation clarity.  
**Status:** pre-existing; not created by this update.

The root `LICENSE` is MIT and refers to the software and associated documentation, while the continuation publication record states `Copyright © 2026 Valentyn Rukhaylo. All rights reserved.`

The intended scope between software licensing and authored publication/research text is therefore not fully explicit at repository root.

This audit does not change the license because doing so would alter legal/licensing state beyond the authorized documentation transition. The repository owner should make a separate explicit licensing decision if the intended split is MIT-for-code / separately copyrighted research publications.

**Result: OPEN ADVISORY; not a merge blocker for this documentation-only update.**

## 18. Final DDC gate

| Gate | Result |
|---|---|
| Human authority preserved | PASS |
| Intent preserved | PASS |
| Historical results unchanged | PASS |
| Publication artifacts unchanged | PASS |
| v0.8 protocol unchanged | PASS |
| v0.8 reference run remains blocked | PASS |
| v0.9 implementation remains blocked | PASS |
| External criticism separated from evidence | PASS |
| Negative v0.7 replication preserved | PASS |
| Current lineage exposed | PASS |
| No executable files changed | PASS |
| No new runtime/resource surface | PASS |
| Recovery point preserved | PASS |
| Licensing scope | OPEN ADVISORY — separate owner decision |

## Final authorization state

**This documentation/research-governance update is authorized for merge.**

It authorizes only the corrected repository state represented by this change set.

It does **not** authorize:

- a v0.8 canonical reference run;
- a v0.9 implementation;
- real-person attribution research;
- production identity resolution;
- any claim that a deployed watermark or provider performs user-level attribution.

The governed next experimental transition remains the exact v0.8 implementation candidate and its pre-reference DDC implementation audit.
