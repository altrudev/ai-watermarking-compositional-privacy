# Validation Record v0.4

## Scope

Validation for the additive v0.4 path-dependence experiment.

## Executed checks

- `py_compile` for the v0.4 module and tests: **PASS**
- v0.4 path-dependence unit/adversarial suite: **11/11 PASS**
- v0.3 transformation-chain regression plus v0.4 suite: **23/23 PASS**
- deterministic 12-person / 144-generation / 24-path reference run: **PASS**

## Structural checks

- all 24 permutations evaluated: PASS
- same four-transform multiset on every path: PASS
- each transformation exactly once per path: PASS
- final metadata identical across paths: PASS
- simulated provider/watermark absent on all final paths: PASS
- invalid/incomplete path rejected: PASS
- v0.1/v0.2/v0.3 experiment files modified by v0.4: NO

## Reference result

- random person baseline: 8.33%
- minimum person top-1: 25.69%
- maximum person top-1: 44.44%
- spread: 18.75 percentage points
- materiality threshold: 8.33 percentage points
- bounded result: `path_dependent`

## Validation boundary

The local executable regression covered the v0.3 dependency surface used by v0.4 plus the complete v0.4 suite. Earlier v0.1/v0.2 experiment files are outside the v0.4 dependency path and are preserved unchanged in the branch diff.

No GitHub Actions were introduced or used.
