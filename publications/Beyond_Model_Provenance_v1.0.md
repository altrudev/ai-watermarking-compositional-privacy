# Beyond Model Provenance

## Continued Experimental Research on Watermark Linkability, Identification, and Compositional Privacy

**Author:** Valentyn Rukhaylo · Altru.dev  
**Publication date:** August 20, 2026  
**Version:** 1.0  
**Document type:** Continued Research Paper / Experimental Privacy Analysis  
**Copyright:** © 2026 Valentyn Rukhaylo  
**License:** CC BY-NC-ND 4.0, effective August 22, 2026; see `../LICENSING.md`

## Relationship to the original paper

This paper is a continuation of:

> Valentyn Rukhaylo. *From Model Provenance to Human Attribution: The Compositional Privacy Risk of AI Text Watermarking.* Altru.dev Technical Research Note, Version 1.0, August 18, 2026.

The original paper remains the canonical published threat-model foundation. This continuation does not replace or rewrite it. It records the experimental program that followed: synthetic attribution/unlinkability tests, transformation-chain experiments, path-dependence tests, robustness analysis, pairwise mechanism analysis, and independent cross-family/cross-policy replication/falsification.

## Central research question

A provenance signal can contain no personal identity and still participate in an identifying system. The continuing research asks how far such a signal can contribute to attribution when combined with text-derived evidence, timing, provider/model context, retained generation relationships, and other auxiliary evidence - and where those mechanisms fail.

The operational distinction remains:

> **Detection ≠ Provenance ≠ Attribution ≠ Identity Resolution ≠ Authority.**

## Research maturity represented in this paper

The paper discusses experimental results through the v0.7 program while preserving the following boundaries:

- synthetic benchmark evidence ≠ deployed-provider evidence;
- model attribution ≠ user attribution;
- failed re-identification ≠ anonymity;
- a strong local mechanism ≠ a general mechanism;
- experimental implication ≠ constitutional or production policy;
- correlation ≠ authorization.

The v0.6 experiment produced a strong local pairwise non-commutativity result. The independently predeclared v0.7 experiment then failed to broadly replicate or transfer that mechanism across new transformation families, adversary policies, populations, seeds, and holdout conditions. The continuation paper treats that negative replication result as evidence that narrows the claim rather than as a reason to retune the experiment.

## Licensing record

As of August 22, 2026, the copyright holder offers this identified Version 1.0 work under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0)**.

An earlier copy or archived PDF may contain an All Rights Reserved notice. This later grant provides additional permissions for the identified work without modifying the historical bytes, title, version, or checksum. The authoritative repository scope record is `../LICENSING.md`.

The license does not grant trademark rights, transfer authorship, imply endorsement, or authorize modified material to be represented as an official Altru.dev publication.

## Canonical PDF artifact

Filename:

`Beyond_Model_Provenance_Continued_Research_Valentyn_Rukhaylo_v1.0.pdf`

SHA-256:

`b08acf081752022cfe9602d518b372b6ff3b03e386d82d7f07a5f2a33f2fb96b`

The exact PDF was rendered and visually checked across all 12 pages before this publication record was created. A storage copy is retained outside Git history; the checksum above is the canonical artifact identity for later repository/Zenodo/site attachment.

## Suggested citation

Rukhaylo, Valentyn. *Beyond Model Provenance: Continued Experimental Research on Watermark Linkability, Identification, and Compositional Privacy.* Altru.dev Continued Research Paper, Version 1.0, August 20, 2026.

## Repository lineage

Research repository:

`https://github.com/altrudev/ai-watermarking-compositional-privacy`

Canonical research state immediately before this publication record:

`43e9b1d591d0339dd5d94c74f8dd441873c5b20d`

This record is publication metadata. It does not alter historical experiment results or promote any experimental finding to a validated invariant.
