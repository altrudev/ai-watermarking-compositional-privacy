# Claim Register v0.5

## Supported inside the declared synthetic matrix

### C5.1 — Canonical predecessor parity
The full canonical v0.5 scenario exactly reproduces the published v0.4 25.69%–44.44% range, 18.75-point spread, and best/worst paths.

### C5.2 — Robustness across declared perturbations
12 of 13 scenarios meet the population-relative materiality threshold for transformation-order path dependence.

### C5.3 — Negative control
The commuting operations `lowercase` and `normalize whitespace` produce identical final text and metadata in either order.

### C5.4 — Directional summarize/model-edit observation
The summarize-before-model-edit pairwise effect is non-positive in every declared scenario. This is bounded to this benchmark.

### C5.5 — Path dependence is not inevitable
The half-strength transform scenario produces a 0.00-point person-attribution spread and does not meet materiality.

## Derived

### D5.1 — Perturbation testing is required before promotion
A privacy property observed under one population, seed, transform strength, or scoring policy should not be promoted to a system property without robustness tests and negative controls.

### D5.2 — Non-commutativity is a candidate mechanism
The contrast between interacting transforms and the commuting control makes transformation non-commutativity a candidate mechanism for path dependence. v0.5 does not prove it is the only mechanism.

## Not established

- universal path dependence;
- deployed-provider behavior;
- user identification by any named provider;
- anonymity of the lowest-linkability path;
- a universal recommendation to summarize before model editing;
- a legal definition of anonymity from the benchmark threshold.

## Explicit non-claims

No real people are ingested or deanonymized. No Claude, SynthID, OpenAI, Gemini, or other proprietary watermark/detector is reverse engineered.
