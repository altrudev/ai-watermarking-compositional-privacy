# Licensing and Rights Scope

**Copyright:** © 2026 Valentyn Rukhaylo / Altru.dev  
**Effective for current repository state:** August 22, 2026

This repository contains multiple classes of material. They are not licensed as one work.

## License-resolution rule

When determining the license for a file, use this order:

1. an explicit license notice inside the file;
2. a specific file/path rule in this document;
3. the applicable directory default below;
4. the repository administrative default.

A more specific rule overrides a broader rule.

## Scope map

| Material | Path / file pattern | License |
|---|---|---|
| Research software | `lab/**` | MIT |
| Test software | `tests/**` | MIT |
| Synthetic machine-readable evidence and result data | `research/*.json`, `research/*.json.gz.b64` | CC BY 4.0 |
| Active research prose, protocols, audits, claim registers, validation records, methodology, review logs | `research/*.md` | CC BY-NC 4.0 |
| Governance/program records | `docs/**` | CC BY-NC 4.0 |
| Original canonical paper text | `paper.md` | CC BY-NC-ND 4.0 |
| Formal continuation publication text | `publications/Beyond_Model_Provenance_v1.0.md` | CC BY-NC-ND 4.0 |
| Publication/citation metadata and checksums | `CITATION.cff`, `publications/*.cff`, `publications/*.sha256` | CC BY 4.0 |
| Publication index | `publications/README.md` | CC BY-NC 4.0 |
| Repository/research indexes and explanatory documentation | `README.md`, `research/README.md`, `LICENSING.md` | CC BY-NC 4.0 |
| License notices | `LICENSE`, `LICENSES/**` | May be reproduced as needed to communicate the applicable license terms; each referenced standard license retains its own terms |

If a future file does not match a specific rule, it must not silently inherit a license by guesswork. Add it to this map or place an explicit license notice in the file before publication.

## Software — MIT

The MIT License applies only to files designated as MIT by the scope map or by an explicit per-file notice.

The standard MIT phrase “software and associated documentation files” refers only to documentation accompanying the MIT-licensed software itself. It does not expand the MIT grant to research papers, research protocols, experimental evidence, publication records, or other files separately mapped here.

Reference: [`LICENSES/MIT-CODE.txt`](LICENSES/MIT-CODE.txt).

## Synthetic evidence and data — CC BY 4.0

Machine-readable synthetic experimental evidence and designated metadata are offered under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

This allows copying, redistribution, adaptation, and commercial reuse subject to the license's attribution and other conditions.

Reference: [`LICENSES/CC-BY-4.0-DATA.txt`](LICENSES/CC-BY-4.0-DATA.txt).

Synthetic evidence remains synthetic evidence. Licensing the data does not promote it into evidence about deployed providers or real people.

## Active research documentation — CC BY-NC 4.0

Research notes, protocols, audits, claim registers, validation records, methodology, external-review records, and related prose designated above are offered under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

This permits sharing and adaptation for non-commercial purposes subject to attribution and the other license conditions.

Reference: [`LICENSES/CC-BY-NC-4.0-RESEARCH.txt`](LICENSES/CC-BY-NC-4.0-RESEARCH.txt).

## Formal publications — CC BY-NC-ND 4.0

The designated canonical paper text and formal publication text are offered under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0)**.

This allows non-commercial redistribution of the unmodified work with attribution, subject to the license conditions. It does not grant permission to distribute modified versions as the licensed publication.

Reference: [`LICENSES/CC-BY-NC-ND-4.0-PUBLICATIONS.txt`](LICENSES/CC-BY-NC-ND-4.0-PUBLICATIONS.txt).

### Existing publication objects

As of August 22, 2026, the copyright holder additionally offers the following identified works under CC BY-NC-ND 4.0:

1. **From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking**, Version 1.0, August 18, 2026, including the repository text in `paper.md` and the identified published research object referenced by `CITATION.cff`.
2. **Beyond Model Provenance: Continued Experimental Research on Watermark Linkability, Identification, and Compositional Privacy**, Version 1.0, August 20, 2026, including the repository publication text and the canonical PDF identified in `publications/Beyond_Model_Provenance_v1.0.md` by its recorded SHA-256 checksum.

Earlier copies may contain an “All Rights Reserved” notice. This later license grant does not alter those historical bytes or checksums; it grants additional permissions for the identified works from the effective date above.

## Branding and marks

The licenses above do **not** grant rights in:

- the Altru.dev name;
- Altru.dev logos;
- project logos or visual identity marks;
- trade dress;
- other source-identifying branding.

Ordinary nominative reference, citation, and legally permitted fair use are not restricted by this statement. No permission is granted to imply sponsorship, endorsement, official status, or affiliation.

## Authorship, provenance, and authority

A content license is a permission grant. It is not an attribution decision or authority grant.

Standing distinctions:

> License to copy != transfer of authorship.

> License to adapt != endorsement.

> Public availability != public-domain status.

> Provenance != authorship != ownership != responsibility != authority.

> Research reuse != authority to represent modified material as an official Altru.dev publication.

## Historical versions

Before this multi-scope transition, the repository root contained a general MIT license. This document does not purport to revoke permissions already granted for earlier versions made available under that license.

For historical material, the repository's commit history is the evidence of what notice existed at that time. For the current version and future versions, this scope map controls unless a file explicitly says otherwise.

## Third-party material

Nothing in this repository's licensing notices grants rights the copyright holder does not possess. Third-party quotations, referenced materials, trademarks, or externally sourced works remain subject to their own rights and applicable law.

## No warranty / no legal or factual endorsement

The applicable standard licenses contain their own terms and warranty limitations. No license granted here converts experimental findings into validated real-world claims, production authorization, legal conclusions, or identity-resolution authority.
