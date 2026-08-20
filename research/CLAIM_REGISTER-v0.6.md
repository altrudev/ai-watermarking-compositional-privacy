# Claim Register v0.6

## Supported inside the declared synthetic reference experiment

### C6.1 — Canonical scorer parity
The optimized cached evaluator reproduces the canonical v0.3 attribution scorer for the declared parity path.

### C6.2 — Pairwise mechanism predictiveness
The predeclared pairwise-order predictor reaches Pearson `r = 0.9282921071911276` across all 24 complete transformation paths, exceeding the predeclared `r >= 0.70` threshold.

### C6.3 — Concentrated non-commutativity
The largest observed order effect is the `summarize | model_edit` pair, with a signed person top-1 difference of `-23.6111` percentage points when pair order is reversed.

### C6.4 — Smaller secondary interaction
The `paraphrase | translate` pair produces a signed person top-1 difference of approximately `-1.3889` percentage points.

### C6.5 — Commuting negative control
Lowercasing and whitespace normalization commute under the declared experiment: final text and metadata are identical and person/generation attribution differences are zero.

## Derived

### D6.1 — Path dependence can have localized mechanisms
In this benchmark, complete-path variation is not uniformly distributed across every transform relationship. A small number of pairwise interactions account for much of the predictive signal.

### D6.2 — Final metadata equality does not imply transformation equivalence
The dominant non-commuting pair preserves final metadata equality while changing text-derived lexical and semantic evidence and downstream attribution.

### D6.3 — Transformation lineage remains relevant
Where non-commuting transforms exist, the final artifact alone may be insufficient to explain how its privacy/linkability state arose. This is a research implication, not a production or constitutional rule.

## Not established

- a universal law of privacy-transform non-commutativity;
- a universal recommendation to summarize before model editing;
- deployed-provider or proprietary-model behavior;
- human identity resolution against real people;
- anonymity or untraceability;
- causal sufficiency of pairwise effects in every population or transform family;
- legal or production privacy thresholds.

## Explicit non-claims

No real people, accounts, provider logs, private conversations, scraped profiles, production watermark detectors, or proprietary model APIs are used. Predictor success inside the synthetic benchmark does not authorize identity resolution or elevate the result to a validated H/R Native invariant.
