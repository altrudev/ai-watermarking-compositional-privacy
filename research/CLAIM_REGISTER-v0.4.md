# Claim Register v0.4

## Experimental claims

### C4.1 — Transformation order materially affected residual attribution
**Status:** Supported in the declared synthetic reference experiment.

Across all 24 permutations of the same four transformations, person top-1 attribution ranged from 25.69% to 44.44%, a spread of 18.75 percentage points. The random-person baseline was 8.33%.

### C4.2 — Final metadata differences do not explain the measured spread
**Status:** Supported in the declared experiment.

All paths had one identical final metadata signature. Provider hints and simulated watermark metadata were absent from every final path.

### C4.3 — The same transformation multiset does not imply the same privacy outcome
**Status:** Supported in the declared experiment.

All paths used paraphrase, summarize, translate, and model edit exactly once, yet produced materially different attribution outcomes.

### C4.4 — Transformation history should be preserved as privacy evidence
**Status:** Derived design implication.

Because order changed residual attribution, recording only the final artifact or unordered transformation set loses information relevant to the privacy claim.

## Explicit non-claims

v0.4 does **not** claim:

- universal anonymity or unlinkability;
- that the best path is generally optimal;
- that summarization should always occur first;
- that model editing is inherently privacy-reducing;
- that deployed LLMs, translation systems, or watermark detectors behave like these proxies;
- that the quantitative spread will persist at every population size or seed;
- that four aggregate final digests imply only four meaningful semantic outcomes;
- that absence of attribution by this benchmark proves absence of attribution by another adversary.

## Standing distinctions

- Privacy transformation ≠ privacy evidence
- Failed re-identification ≠ proven anonymity
- Intermediate unlinkability ≠ end-to-end unlinkability
- Transformation set ≠ transformation history ≠ privacy outcome
