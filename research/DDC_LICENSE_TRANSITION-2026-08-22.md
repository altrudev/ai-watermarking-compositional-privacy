# DDC Licensing Transition — 2026-08-22

**Status:** pre-change governed transition record  
**Authority:** explicit repository-owner approval in the active conversation  
**Scope:** repository licensing structure only  
**Executable code changes authorized:** no  
**Historical experimental results changes authorized:** no  
**Frozen v0.8 protocol/claim changes authorized:** no

## 1. Intent

Replace the ambiguous single-root-license presentation with an explicit multi-scope licensing model that separates software, synthetic evidence/data, active research documentation, formal publications, and branding.

The transition is intended to improve reproducibility and reuse of software/data while preserving scholarly authorship, publication integrity, non-commercial research-document use, and control of Altru.dev branding.

## 2. Current-state defect

The repository currently contains a root MIT license using the standard phrase "software and associated documentation files" while formal publication records separately state copyright and All Rights Reserved. Without an explicit scope map, readers could reasonably be uncertain whether the MIT grant applies to research papers, audit records, datasets, publication metadata, or only software.

DDC finding:

> Public availability != a single licensing state.

> Code openness != transfer of research authorship.

> License grant != authorship, endorsement, authority, or ownership of underlying claims.

## 3. Authorized target state

The repository will use the following default scopes:

1. **MIT** — executable research software in `lab/` and tests in `tests/`.
2. **CC BY 4.0** — machine-readable synthetic evidence, result data, checksums, lineage data, and citation metadata where specifically mapped.
3. **CC BY-NC 4.0** — active research documentation, methodology, audits, protocols, claim registers, explanatory repository documentation, and governance records.
4. **CC BY-NC-ND 4.0** — canonical paper text and formal publication text/records where specifically mapped.
5. **Reserved / not licensed by the above grants** — Altru.dev names, logos, marks, trade dress, and branding identity except for nominative citation/reference use allowed by law.

## 4. Scope-resolution rule

License resolution must be deterministic:

`explicit per-file notice > specific path/file mapping in LICENSING.md > directory default > repository administrative default`

A file must not inherit two conflicting default licenses.

## 5. Historical license preservation

This transition does not purport to revoke permissions already granted for earlier repository versions distributed under the MIT license. Earlier commits remain historical evidence of the license state under which those versions were made available.

The new scope map governs the current repository version and later versions unless a file contains an explicit overriding notice.

## 6. Publication transition

The copyright holder may offer existing authored publications under an additional license without rewriting historical bytes. Where a prior publication record or archived PDF contains an earlier All Rights Reserved notice, the repository licensing record may make a later CC BY-NC-ND 4.0 grant explicit for the identified work.

The transition must not change canonical PDF checksums unless a new PDF edition is deliberately generated and separately versioned.

## 7. Prohibited expansion

This licensing transition must not:

- change experimental numbers, claims, thresholds, protocols, or conclusions;
- change executable source or test behavior;
- imply transfer of authorship, endorsement, authority, or ownership of research findings;
- imply that Creative Commons licenses govern software code where MIT is mapped;
- imply that MIT governs formal papers where CC BY-NC-ND is mapped;
- revoke or rewrite historical license grants;
- grant trademark rights in Altru.dev branding;
- silently relicense third-party material not owned or controlled by the repository owner.

## 8. Verification requirements

Before merge, verify:

- root `LICENSE` is a scope notice rather than a misleading universal MIT grant;
- `LICENSING.md` covers every top-level repository class;
- each license reference file identifies the exact standard license and official legal-code URI;
- MIT scope is limited by the repository map to software/test paths;
- formal papers are mapped to CC BY-NC-ND 4.0;
- active research prose is mapped to CC BY-NC 4.0;
- machine-readable synthetic data is mapped to CC BY 4.0;
- branding is explicitly excluded from the grants;
- prior-rights/non-revocation language is retained;
- no executable files, result values, or frozen protocol files are changed by the licensing patch;
- README and publication/research indexes point readers to the licensing map.

## 9. Recovery

If any scope overlap, ownership ambiguity, or unintended executable/research mutation is discovered, the branch must not merge. Recovery is to the pre-transition `main` head, preserving this record as non-canonical branch evidence only.

## 10. Authorization gate

**Authorized:** create and audit a licensing-only branch implementing the target state above.  
**Not authorized:** change research conclusions, run new attribution experiments, alter canonical result records, or change executable behavior as part of this transition.
