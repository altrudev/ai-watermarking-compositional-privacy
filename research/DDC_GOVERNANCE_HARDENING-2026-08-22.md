# DDC Governance Hardening — 2026-08-22

**Repository:** `altrudev/ai-watermarking-compositional-privacy`  
**Predecessor audit:** `research/DDC_FULL_AUDIT-REPOSITORY-2026-08-22.md`  
**Starting canonical head:** `b04a976da3f3a99df345ec3e4c4d089accf482df`  
**Governance-hardening merge:** `9d446fa8f943b7ec29ed8ade133653a5340e45a0`  
**Authority:** Root Human Authority instruction: `Fix it`  
**Research scope:** unchanged; synthetic-only

## Purpose

Remediate the repository-governance findings from the full repository DDC audit without altering frozen experiment semantics, v0.8 results, licensing grants, publication text, or v0.9 authority.

## Changes made

1. Added `research/BRANCH_CANONICALITY.md` defining `main` as the sole active canonical head and `archive/` branches as noncanonical historical evidence.
2. Added `.github/PULL_REQUEST_TEMPLATE.md` with the DDC authority, lineage, verification, adverse-evidence, and claim-maturity checklist.
3. Added `.github/CODEOWNERS` to route repository review ownership to `@altrudev`.
4. Added `research/REPRODUCIBILITY.md` and declared a prospective supported runtime floor of Python 3.11+.
5. Added the runtime/exact-head rule to `research/RESEARCH_METHOD.md`.
6. Hardened `research/EXTERNAL_REVIEW_LOG.md`: future source URL/access-date/snapshot provenance is required where available; the historical 2026-08-22 LinkedIn entries are explicitly marked as paraphrases whose exact URLs were not retained and could not be recovered. No source URL was invented.
7. Added `research/EVIDENCE_CUSTODY-v0.8.md` with exact reference/bundle/raw-archive hashes and recovery rules.
8. Updated `research/README.md` to index these governance records.
9. Performed branch-state cleanup after the hardening merge and recorded it in `research/BRANCH_CLEANUP-2026-08-22.md`.
10. Created issue #18 to track the three host/external proof gates that cannot be completed through the connected tool surface.

## Finding disposition

| ID | Prior finding | Current disposition |
|---|---|---|
| R1 | `main` unprotected | **OPEN — HOST ACTION REQUIRED.** Normative PR/CODEOWNERS/canonicality controls are installed. The connected GitHub actions do not expose branch-protection/ruleset writes. Tracked in issue #18. |
| R2 | stale v0.9 transition wording | **CLOSED.** |
| R3 | stale/merged working branches | **CLOSED FOR ACTIVE-STATE AMBIGUITY.** Old working refs were moved to the canonical hardening head; unique/rejected history was preserved under explicit `archive/` refs where needed. See `BRANCH_CLEANUP-2026-08-22.md`. |
| R4 | no fresh clean exact-head whole-repo run | **OPEN — EXECUTION ENVIRONMENT REQUIRED.** Sandbox DNS prevents a fresh GitHub clone. Exact commands/runtime contract are now frozen. Tracked in issue #18. |
| R5 | external-review source provenance incomplete | **HARDENED / HISTORICAL GAP EXPLICIT.** Future capture rule added; unavailable historical URLs are disclosed rather than invented. |
| R6 | Python runtime undeclared | **CLOSED.** Supported runtime floor is Python 3.11+; governance-hardening environment observed Python 3.13.5, without misrepresenting that observation as a whole-repo regression run. |
| R7 | v0.8 evidence bundle external-only custody | **PARTIAL — SECOND DURABLE BYTE STORE REQUIRED.** Exact recovery/custody contract added. Tracked in issue #18. |

## R1 host-enforcement target

When the GitHub host setting is available, `main` should be protected without introducing GitHub Actions:

- require pull requests before merge;
- block force pushes to `main`;
- block deletion of `main`;
- restrict direct pushes to the minimum admin/Root Human Authority set;
- use CODEOWNERS review routing where supported;
- do **not** add GitHub Actions status-check requirements.

Until this is enabled, repository practice is hardened but host enforcement is not complete.

## R4 exact-head verification target

From a clean checkout of the then-current canonical head using Python 3.11+:

```bash
python -m py_compile lab/*.py tests/*.py
python -m unittest discover -s tests -v
```

Record exact head, Python version, compile outcome, test count, failures/errors, and runtime. A clean-checkout claim must require an actual clean checkout.

## R7 evidence durability target

The existing bundle remains cryptographically anchored as:

`baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

A future archival transition should place the exact bytes, or the complete reconstructable raw archives, into an independent durable research-data store or authenticated GitHub release asset. Recompression/re-export creates a new artifact and must not silently reuse this checksum.

## DDC decision

**`PASS FOR CONTINUED RESEARCH USE — INTERNAL REPOSITORY HARDENING SUBSTANTIALLY COMPLETE; HOST/EXTERNAL PROOF GATES R1/R4/R7 REMAIN OPEN`.**

No experiment code, tests, v0.8 thresholds/results, evidence identities, publication text, licensing grant, real-person scope, provider access, or v0.9 implementation/execution authority is changed by this transition.

Standing distinction:

> **Documented governance != host-enforced governance != executed proof.**
