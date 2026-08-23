# DDC Governance Hardening — 2026-08-22

**Repository:** `altrudev/ai-watermarking-compositional-privacy`  
**Predecessor audit:** `research/DDC_FULL_AUDIT-REPOSITORY-2026-08-22.md`  
**Starting canonical head:** `b04a976da3f3a99df345ec3e4c4d089accf482df`  
**Authority:** Root Human Authority instruction: `Fix it`  
**Research scope:** unchanged; synthetic-only

## Purpose

Remediate the repository-governance findings from the full repository DDC audit without altering frozen experiment semantics, v0.8 results, licensing grants, publication text, or v0.9 authority.

## Changes made in this transition

1. Added `research/BRANCH_CANONICALITY.md` defining `main` as the sole active canonical head and `archive/` branches as noncanonical historical evidence.
2. Added `.github/PULL_REQUEST_TEMPLATE.md` with the DDC authority, lineage, verification, adverse-evidence, and claim-maturity checklist.
3. Added `.github/CODEOWNERS` to route repository review ownership to `@altrudev`.
4. Added `research/REPRODUCIBILITY.md` and declared a prospective supported runtime floor of Python 3.11+.
5. Added the runtime/exact-head rule to `research/RESEARCH_METHOD.md`.
6. Hardened `research/EXTERNAL_REVIEW_LOG.md`: future source URL/access-date/snapshot provenance is required where available; the historical 2026-08-22 LinkedIn entries are explicitly marked as paraphrases whose exact URLs were not retained and could not be recovered. No source URL was invented.
7. Added `research/EVIDENCE_CUSTODY-v0.8.md` with exact reference/bundle/raw-archive hashes and recovery rules.
8. Updated `research/README.md` to index these governance records.

## Finding disposition

| ID | Prior finding | Disposition after this transition |
|---|---|---|
| R1 | `main` unprotected | **OPEN — host enforcement unavailable through connected GitHub actions.** Normative PR/CODEOWNERS/canonicality controls added; actual branch-protection setting still must be enabled at GitHub host level. |
| R2 | stale v0.9 transition wording | **CLOSED** in predecessor audit transition. |
| R3 | stale/merged working branches | **IN REMEDIATION.** Canonical/archive semantics now explicit. Merged ephemeral refs may be neutralized after this hardening merge while preserving unique history under `archive/` where necessary. |
| R4 | no fresh clean exact-head whole-repo run | **OPEN.** Sandbox DNS still prevents a fresh GitHub clone. The repository now specifies the exact regression/compile commands and prohibits calling a reconstruction a clean checkout. |
| R5 | external-review source provenance incomplete | **HARDENED / HISTORICAL GAP EXPLICIT.** Future capture rule added; unavailable historical URLs are disclosed rather than invented. |
| R6 | Python runtime undeclared | **CLOSED.** Supported runtime floor is Python 3.11+; governance-hardening environment observed Python 3.13.5, without misrepresenting that observation as a whole-repo regression run. |
| R7 | v0.8 evidence bundle external-only custody | **PARTIAL.** Exact recovery/custody contract added. Actual second independent durable byte store remains open because the connected GitHub interface exposes no binary release/local-file upload operation. |

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

**`PASS FOR GOVERNANCE-HARDENING MERGE — HOST/EXTERNAL PROOF GATES REMAIN OPEN`.**

No experiment code, tests, v0.8 thresholds/results, evidence identities, publication text, licensing grant, real-person scope, provider access, or v0.9 implementation/execution authority is changed by this transition.

Standing distinction:

> **Documented governance != host-enforced governance != executed proof.**
