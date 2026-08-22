# Full DDC Audit — Multi-Scope Repository Licensing

**Audit date:** 2026-08-22  
**Base repository head:** `29204692e748f19f506ed29f10e1d9c7a7e5874f`  
**Audited content head:** `3023cdd8ce3ae1a3fffab5ec752643e306f5bde1`  
**Branch:** `ddc/licensing-scope-20260822`  
**Change class:** licensing / documentation / rights-scope governance  
**Executable code changed:** no  
**Tests changed:** no  
**Historical experimental results changed:** no  
**Frozen v0.8 protocol or claim gates changed:** no

The audit record itself is evidence-only and is created after the audited content head. It does not alter the licensing rules it evaluates.

## Executive result

**DDC result: `PASS FOR MERGE`**

The branch replaces an ambiguous universal root MIT presentation with a deterministic multi-scope licensing map while preserving historical license-state evidence and leaving executable/research-result state unchanged.

The resulting current-state model is:

- software: MIT;
- designated machine-readable synthetic evidence/data and metadata: CC BY 4.0;
- active research documentation: CC BY-NC 4.0;
- designated formal publication text: CC BY-NC-ND 4.0;
- Altru.dev branding and source-identifying marks: not granted by those licenses.

The transition explicitly does not purport to revoke permissions previously granted for earlier repository versions under the former root MIT notice.

---

## 1. Authority audit

The repository owner explicitly approved the proposed licensing model in the active conversation.

Authorized transition:

> clarify and change the current repository's license scopes without changing research results or executable behavior.

No additional authority was inferred from research need or public availability.

**PASS.**

Standing rule:

> Need != Authority.

> Public availability != public-domain status.

---

## 2. Intent preservation

The requested intent was to preserve open software/reproducible data while retaining stronger control over research prose, canonical publication integrity, and branding.

Implemented mapping matches that intent:

- `lab/**`, `tests/**` -> MIT;
- designated machine-readable evidence/metadata -> CC BY 4.0;
- research prose/governance -> CC BY-NC 4.0;
- canonical papers/formal publication text -> CC BY-NC-ND 4.0;
- marks/branding -> excluded.

**PASS.**

---

## 3. Transition-boundary audit

Comparison of base `main` to audited content head shows changes only to licensing, citation/publication metadata, repository indexes, and the licensing transition record.

No files under `lab/` or `tests/` changed.

No historical `RESULTS-*`, reference report, holdout matrix, transfer matrix, diagnostic evidence, v0.8 protocol, v0.8 amendment, v0.8 claim register, or program execution state changed.

**PASS.**

DDC distinction:

> License-state change != research-result change != experiment authorization.

---

## 4. Scope determinism audit

`LICENSING.md` defines explicit precedence:

`explicit per-file notice > specific path/file mapping > directory default > repository administrative default`

The current top-level repository classes are covered:

- `lab/`;
- `tests/`;
- `research/` prose;
- `research/` machine-readable result/evidence files;
- `docs/`;
- `paper.md`;
- `publications/` formal text;
- publication/citation metadata and checksum files;
- root/research/publication indexes;
- license notices;
- branding/marks.

Future unmapped files are instructed not to inherit a license by guesswork.

**PASS.**

---

## 5. MIT scope audit

The former root `LICENSE` was a standard MIT grant whose phrase "software and associated documentation files" created ambiguity in a mixed research repository.

The new root notice no longer presents MIT as a universal repository license.

`LICENSES/MIT-CODE.txt` retains the standard MIT grant for designated software and explicitly binds scope back to `LICENSING.md`.

This prevents the software license from silently overriding separately mapped research/publication material.

**PASS.**

---

## 6. Creative Commons reference audit

The repository includes scoped reference notices for:

- `CC-BY-4.0`;
- `CC-BY-NC-4.0`;
- `CC-BY-NC-ND-4.0`.

Each notice records:

- the exact license name;
- SPDX identifier;
- official Creative Commons license page;
- official legal-code URI;
- repository-specific scope without attempting to rewrite the Creative Commons legal code.

The legal code is incorporated by reference rather than copied into repository prose, reducing the risk of a locally modified or incomplete license text being mistaken for the standard license.

**PASS.**

---

## 7. Publication-rights audit

The formal publication mapping now grants CC BY-NC-ND 4.0 for the identified Version 1.0 works.

For the continued paper, the publication record and CFF metadata both record the current license.

For the original paper, `CITATION.cff` records `CC-BY-NC-ND-4.0`, while `LICENSING.md` identifies the title/version and repository paper text.

The canonical continuation PDF checksum remains unchanged. No PDF bytes were rewritten.

The repository explicitly addresses earlier All Rights Reserved markings as historical distribution state and records a later additional license grant by the copyright holder.

**PASS.**

Standing distinction:

> Historical bytes != current permission record.

---

## 8. Historical-license preservation audit

The current notices state that the transition does not purport to revoke permissions already granted for earlier repository versions under the previous MIT notice.

Git history remains the evidence of prior license state.

This avoids a false claim of retroactive revocation.

**PASS.**

---

## 9. Authorship / authority / endorsement audit

The licensing map explicitly preserves these distinctions:

- license to copy != transfer of authorship;
- license to adapt != endorsement;
- provenance != authorship != ownership != responsibility != authority;
- research reuse != authority to represent modified material as an official Altru.dev publication.

No license is described as proof of authorship, ownership, identity, responsibility, or authority.

**PASS.**

---

## 10. Branding audit

Altru.dev names, logos, marks, trade dress, and source-identifying branding are explicitly excluded from the software/research/data/publication grants.

The notice preserves ordinary nominative reference and citation without granting endorsement or affiliation rights.

**PASS.**

---

## 11. Third-party-rights audit

`LICENSING.md` states that repository notices do not grant rights the copyright holder does not possess and that third-party quotations, referenced works, and trademarks remain subject to their own rights and applicable law.

This prevents repository-wide licensing language from being interpreted as an ownership claim over external material.

**PASS.**

---

## 12. Research-integrity audit

No experimental result, threshold, hypothesis classification, synthetic population, score, or reference checksum was changed by the licensing transition.

The publication checksum recorded for the continued paper remains:

`b08acf081752022cfe9602d518b372b6ff3b03e386d82d7f07a5f2a33f2fb96b`

The licensing transition changes permission state, not evidence state.

**PASS.**

---

## 13. Security / executable-surface audit

Changed-file inspection shows no executable source or test changes.

No credentials, network calls, dependencies, package-install instructions, remote execution hooks, workflow changes, or new runtime permissions were introduced.

No security test execution is required to validate executable behavior because executable bytes are outside the transition set. Existing test claims are not restated as fresh test execution.

**PASS for the declared licensing-only transition.**

---

## 14. Public discoverability audit

The scope is exposed through:

- root `LICENSE`;
- root `LICENSING.md`;
- root `README.md` licensing section;
- `research/README.md` licensing section;
- `publications/README.md` licensing section;
- CFF license metadata for both identified papers;
- scoped files in `LICENSES/`.

A reader no longer needs to infer whether the root MIT grant covers research papers.

**PASS.**

---

## 15. Residual legal limitations

The following are accepted limitations rather than merge-blocking defects:

1. this repository governance audit is not jurisdiction-specific legal advice;
2. enforceability and interpretation of license terms can depend on applicable law and facts;
3. Creative Commons legal code is referenced by official URI rather than vendored in full;
4. GitHub may no longer display a single automatic repository-license classification because the repository is intentionally multi-licensed;
5. prior recipients may retain rights in historical versions under earlier grants;
6. third-party material cannot be relicensed beyond rights actually held by the repository owner.

These limitations do not undermine the scope clarity of the current repository state.

---

## 16. Recovery audit

The licensing transition is isolated on a dedicated branch and can be reverted without reverting experimental code or historical results.

If later legal review requires different terms, the license map can be changed through a new explicit rights-state transition while preserving this commit history as evidence of the prior state.

**PASS.**

---

## Final DDC gate

- Human authority: **PASS**
- Intent preservation: **PASS**
- No executable expansion: **PASS**
- No research-result mutation: **PASS**
- Deterministic license scope: **PASS**
- Historical grants preserved: **PASS**
- Publication grant explicit: **PASS**
- Branding excluded: **PASS**
- Third-party rights bounded: **PASS**
- Public discoverability: **PASS**
- Recovery path: **PASS**

## Final authorization state

**`PASS FOR MERGE`**

The licensing branch may merge as a rights-scope/documentation transition. It does not authorize any new v0.8 execution, v0.9 implementation, real-person attribution work, or change to research claims.
