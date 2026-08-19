# Textual Compositional Privacy Benchmark — Test Plan v0.2

## Research purpose

v0.2 moves the synthetic unlinkability experiment from pre-built abstract semantic/style vectors to actual generated synthetic text. The benchmark asks whether identity linkage still emerges when semantic, lexical, and stylometric signals must be derived from the artifact itself, and whether composite privacy transformations remain effective under adaptive re-identification.

## DDC-governed research boundary

### Authority

The experiment is authorized only to generate and re-identify identities, accounts, sessions, generations, and text created by the harness itself.

### Prohibited expansion

The benchmark has no loader for real people, provider logs, private conversations, scraped social profiles, platform account records, or third-party identity corpora. Any future real-data phase requires a separate research decision, data authority, privacy review, threat model, and test protocol.

### Evidence rules

**Privacy transformation ≠ privacy evidence.** Every transformation must be followed by re-identification testing.

**Fixed-attack failure ≠ adaptive-attack failure.** The attacker may reweight the evidence channels that remain useful after transformation.

**Failed re-identification ≠ proven anonymity.** Results are bounded to the declared synthetic generator, evidence channels, attack model, transformations, metrics, seed, and thresholds.

## Synthetic lineage

```text
synthetic person
  -> synthetic account
  -> synthetic session
  -> synthetic text generation
  -> synthetic published artifact
```

Every identity-bearing ID is generated locally in the `syn-` namespace.

## Text-derived evidence channels

1. semantic/topic distribution derived from text;
2. stylometric structure derived from sentence length, punctuation, lexical richness, and recurring phrase habits;
3. lexical signature distribution derived from text;
4. abstract provider/model provenance family;
5. provider hint;
6. generation/publication timing.

No proprietary watermark is implemented or emulated.

## Adversaries

| Class | Available evidence |
|---|---|
| Public observer | person-level semantic, lexical, and style profiles |
| Detector operator | public evidence + abstract provenance/provider result |
| AI provider | generation-level text-derived profiles + provenance/provider evidence |
| Provider + publisher | provider evidence + publication timing |
| Adaptive provider + publisher | reweights surviving signals after transformation using an isolated calibration partition |

## Test families

### T1 — Determinism and synthetic-only boundary

- Same seed reproduces the same synthetic population and texts.
- All IDs retain the `syn-` namespace.
- No real-data loader exists.

### T2 — Actual textual artifacts

- Every generation contains generated text rather than only latent vectors.
- Attack features are extracted from that text.

### T3 — Single-signal attacks

Measure person attribution independently for semantic, style, lexical, provenance, provider, and timing channels.

### T4 — Compositional attack

Measure combined provider+publisher attribution and compute:

```text
combined person attribution
- strongest single-signal person attribution
```

### T5 — Provenance-only removal

Remove the abstract provenance family and provider hint without changing textual/timing evidence. Measure residual attribution.

### T6 — Composite privacy transformation

Apply provenance removal, publication delay, lexical normalization, style normalization, and deterministic semantic generalization.

### T7 — Adaptive re-identification

Use one partition of transformed artifacts to measure surviving signal utility and derive attack weights. Evaluate on a separate partition.

### T8 — Privacy/utility frontier

Run multiple transformation strengths and report person/generation attribution alongside semantic retention and exact-content retention.

### T9 — Claim gate

The benchmark may emit only:

- `SUPPORTED_FOR_DECLARED_TEST`
- `NOT_SUPPORTED`

It must not emit universal anonymity or real-provider claims.

## Reference acceptance conditions

The v0.2 reference benchmark is considered informative when:

1. no single synthetic text signal trivially defines identity;
2. combined evidence exceeds the strongest single signal;
3. provenance/provider removal alone leaves measurable residual attribution;
4. the adaptive attacker is independently calibrated from its evaluation partition;
5. composite transformation materially reduces person and generation attribution;
6. privacy/utility effects are reported together;
7. all automated tests pass deterministically;
8. the claim remains synthetic, adversary-relative, and non-universal.

These conditions validate the benchmark apparatus and declared synthetic result only.
