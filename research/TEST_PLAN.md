# Provenance Linkability / Unlinkability Test Plan v0.1

## Research purpose

The lab tests the inverse of the repository's original threat model: if multiple weak provenance and metadata signals can compose into identity linkage, which transformations are required to reduce that linkage, and how should residual risk be measured?

The purpose is **privacy research and defensive validation**. Version 0.1 is deliberately synthetic-only.

## DDC-governed research boundary

### Authority

The experiment is authorized only to generate and re-identify identities created by the harness itself.

### Prohibited expansion

v0.1 does not ingest real names, real account records, real conversations, provider logs, scraped social profiles, private datasets, or third-party identity corpora. A future expansion beyond synthetic subjects requires a separate research decision, privacy review, data authority, and test protocol.

### Evidence rule

**Privacy transformation ≠ privacy evidence.** A transformation is not considered successful because it ran. It is tested by attempting re-identification after the transformation.

**Failed re-identification ≠ proven anonymity.** Failure supports only a bounded claim for the declared adversary, dataset, evidence channels, metrics, and thresholds.

## Threat model

The synthetic lineage is:

```text
synthetic person
  -> synthetic account
  -> synthetic session
  -> synthetic generation
  -> published artifact
```

The lab models five linkage dimensions:

1. semantic similarity / generation fingerprint
2. style / stylometric similarity
3. simulated provider/model watermark family
4. provider hint
5. temporal correlation between generation and publication

The simulated watermark is an abstract experimental signal. It is **not** a Claude, SynthID, OpenAI, Gemini, or other deployed watermark detector.

## Adversary classes

| Class | Available evidence | Purpose |
|---|---|---|
| Public observer | person-level semantic/style profiles | Test public-corpus linkage |
| Detector operator | public profiles + simulated provider/model marker | Test whether provenance narrows identity candidates |
| AI provider | generation-level semantic/style records + marker/provider | Test provider-side output correlation |
| Provider + publisher | provider evidence + publication timing | Test cross-dataset composition |

## Test families

### T1 — Determinism and population integrity

- Same seed reproduces the same synthetic population.
- All identity-bearing IDs use the `syn-` namespace.
- Artifacts cannot target a generation outside the synthetic population.

### T2 — Baseline attribution

Measure untransformed generation, account, and person attribution for each adversary.

### T3 — Single-channel attribution

Measure semantic, style, watermark-family, and timing evidence independently.

### T4 — Compositional correlation

Combine weak channels and compute **correlation gain**:

```text
person attribution from combined evidence
- strongest person attribution from any single channel
```

A positive gain is direct experimental evidence that component-level privacy does not imply compositional privacy in the synthetic model.

### T5 — Single-channel removal

Remove or weaken one channel at a time:

- simulated provenance marker removal
- publication delay
- semantic generalization
- style normalization

The test explicitly checks whether substantial residual linkage remains.

### T6 — Composite privacy transformation

Apply all four transformations and rerun the strongest declared adversary.

### T7 — Utility measurement

Measure semantic and style retention. Privacy gains that destroy the artifact's intended utility must be visible rather than hidden behind an unlinkability score.

### T8 — Claim gate

The harness may emit only:

`SUPPORTED_FOR_DECLARED_TEST`

or

`NOT_SUPPORTED`

It does not emit `ANONYMOUS` or `UNTRACEABLE`.

## Metrics

- generation top-1 accuracy
- generation top-5 accuracy
- account top-1 accuracy
- person top-1 accuracy
- false-attribution rate
- mean target-generation rank
- mean near-best anonymity-set size
- correlation gain
- semantic retention
- style retention

## Reference acceptance conditions

The reference synthetic experiment is considered useful when:

1. combined evidence materially exceeds every single signal;
2. removing only the watermark/provenance channel leaves measurable residual attribution;
3. semantic, style, and timing transformations each change residual linkage;
4. the composite transformation reduces both person and generation top-1 attribution below the declared threshold in the reference population;
5. the claim remains explicitly adversary-relative and non-universal;
6. all automated tests pass deterministically.

These conditions validate the **test apparatus**, not a claim about any deployed AI provider.

## Next research phases

### v0.2 — richer synthetic artifacts

Generate actual text with controlled topic, phrase, punctuation, lexical, and semantic features and replace abstract vectors with measurable text-derived features.

### v0.3 — detector adapters

Define a provider-neutral adapter interface for externally supplied provenance detectors. No provider-specific detector should be assumed trustworthy merely because it returns a score.

### v0.4 — privacy transformations

Evaluate multiple meaning-preserving transformations and measure the privacy/utility frontier.

### v0.5 — independent attack agents

Use separate attribution and privacy agents with isolated evidence scopes. DDC records the evidence available to each side and prevents evidence leakage between adversary classes.

### v1.0 — reproducible benchmark

Freeze datasets, seeds, metrics, threat models, claim thresholds, and report schema. Publish benchmark results separately from the original threat-analysis paper.
