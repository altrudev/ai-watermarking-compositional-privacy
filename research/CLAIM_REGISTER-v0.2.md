# Claim Register v0.2

## Experiment class
Synthetic-text unlinkability and re-identification benchmark.

## Supported by v0.2

### C-02-01 — Actual text can carry several independent linkage channels
**Status:** Experimentally supported inside the synthetic benchmark.

Lexical, semantic, stylometric, provenance, provider, and timing signals are derived or attached independently and can be measured separately.

### C-02-02 — Weak signals can compose into much stronger attribution
**Status:** Experimentally supported inside the synthetic benchmark.

Reference person top-1 attribution:
- strongest individual signal: 20.83%
- combined provider-plus-publisher evidence: 81.94%
- correlation gain: 61.11 percentage points

### C-02-03 — Provenance-marker removal is not equivalent to unlinkability
**Status:** Experimentally supported inside the synthetic benchmark.

Reference person top-1:
- baseline: 81.94%
- provenance/provider hints removed: 28.47%

### C-02-04 — A successful channel transformation can produce little system-level privacy improvement
**Status:** Experimentally supported inside the synthetic benchmark.

Style normalization measurably changes the style vector but did not materially change combined person attribution in the reference run because other channels continued to dominate.

### C-02-05 — Multi-channel transformation can materially reduce measured attribution
**Status:** Experimentally supported inside the synthetic benchmark.

Reference composite person top-1: 3.12%.

This is not a claim of anonymity.

## Derived

### D-02-01 — Privacy claims should be evaluated against composed evidence
A transformation that removes one channel should not be represented as anonymization without adversarial evaluation against the remaining available channels.

### D-02-02 — Utility/privacy trade-offs require measurement
The composite transform reduces linkage partly by generalizing content and style, so utility loss must be measured alongside attribution reduction.

## Hypotheses for later experiments

### H-02-01
Longer transformation chains may move identifying information between channels rather than monotonically remove it.

### H-02-02
Translation, summarization, human editing, and multi-model rewriting may reduce some stylometric/lexical signals while preserving semantic or temporal linkage.

### H-02-03
A stronger attribution model may recover identities that the transparent v0.2 baseline cannot.

## Explicit non-claims

v0.2 does not claim:
- that Anthropic or another provider performs these attribution operations;
- that the simulated watermark behaves like Claude/SynthID or any proprietary mark;
- that 81.94%, 28.47%, or 3.12% generalize beyond the declared synthetic experiment;
- that the composite output is anonymous;
- that the transparent baseline is state-of-the-art authorship attribution;
- that failed re-identification proves unlinkability against a different adversary, model, dataset, or auxiliary evidence source.
