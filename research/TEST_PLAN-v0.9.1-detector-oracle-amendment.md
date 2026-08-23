# Detector-Oracle Protocol Amendment v0.9.1

**Status:** frozen amendment repairing the initial DDC audit  
**Governing draft:** `research/TEST_PLAN-v0.9-detector-oracle.md` at `da81f93f7e275d2e87358c8e359a5dd529c7d98d`  
**Initial audit:** `research/DDC_AUDIT-v0.9-detector-oracle-initial.md` at `3a4dbe99b29b644c665748a8999e9d8813acf7d2`  
**Precedence:** where this amendment conflicts with the v0.9 draft, this amendment controls.  
**Implementation authorization:** still NO until second DDC audit PASS.

## A1. Exact hidden detector

The synthetic artifact state is a five-dimensional observable vector `z=(z0..z4)` plus a hidden synthetic scope class `K`.

For every artifact, initial `z_i` is generated deterministically from SHA-256 of `scenario|scope_instance|artifact_index|dimension`, mapped uniformly to `[-0.20, +0.20]`.

Artifact noise `eps` is generated independently from SHA-256 of `scenario|scope_instance|artifact_index|noise`, mapped uniformly to `[-0.15,+0.15]`.

The hidden detector logit is:

`L = base[K] + dot(alpha[K], z) + state_offset[A] + eps`

and hidden detector score is:

`s = 1 / (1 + exp(-L))`.

Frozen coefficients:

| K | base | alpha |
|---|---:|---|
| K0 | -2.40 | `(0,0,0,0,0)` |
| K1 | 0.60 | `(0.45,-0.20,0.10,0.05,-0.05)` |
| K2 | 0.70 | `(-0.15,0.50,-0.10,0.10,0.05)` |
| K3 | 0.75 | `(0.10,-0.10,0.55,-0.20,0.05)` |
| K4 | 0.80 | `(0.05,0.10,-0.15,0.55,-0.10)` |
| K5 | 0.85 | `(-0.10,0.05,0.10,-0.15,0.60)` |
| K6 | 0.90 | `(0.35,0.35,-0.20,0.10,0.10)` |
| K7 | 0.95 | `(0.30,-0.25,0.30,-0.25,0.30)` |

Frozen state offsets:

- A0 `0.00`
- A1 `-0.25`
- A2 `-0.45`
- A3 `-0.65`
- A4 `+0.40`

A4 is an externally chosen positive observable perturbation independent of the true target class. It is a false-signal susceptibility proxy, not DITTO emulation.

## A2. Exact detector disclosures

All disclosures derive from the same hidden `s`.

- D0: no response.
- D1: `DETECTED` iff `s >= 0.65`, else `NOT_DETECTED`.
- D2: `LOW` if `s < 0.45`; `MEDIUM` if `0.45 <= s < 0.75`; `HIGH` otherwise.
- D3: scalar `round(s,3)`.
- D4: D3 plus five contribution bins based on `alpha[K][i] * z[i]`: `NEG` if `< -0.05`, `NEUTRAL` if `[-0.05,+0.05]`, `POS` if `> +0.05`. The bins never emit alpha values or K labels.
- D5: D3 plus a threshold-distance band using `s-0.65`: `FAR_BELOW < -0.20`, `NEAR_BELOW [-0.20,0)`, `NEAR_ABOVE [0,+0.20)`, `FAR_ABOVE >= +0.20`; plus `active_dimension_count = count(|alpha_i*z_i| > 0.05)`.
- D6: add deterministic noise `n in [-0.08,+0.08]` derived from SHA-256 of `scenario|artifact|query_index|D6`, clamp to `[0,1]`, then expose only the D2 band. Calls 1-8 are informative. Calls 9-16 return `RATE_LIMITED`. A blocked call still counts against the requested query budget.

Repeated identical D1-D5 calls must be byte-identical. D6 may differ only because its query-index noise is predeclared.

## A3. Exact edit candidates

At every step, the policy receives exactly five candidate next vectors from current `z`:

- P1 `( +0.18, -0.05,  0.00,  0.00,  0.00 )`
- P2 `(  0.00, +0.18, -0.05,  0.00,  0.00 )`
- P3 `(  0.00,  0.00, +0.18, -0.05,  0.00 )`
- P4 `( -0.05,  0.00,  0.00, +0.18,  0.00 )`
- P5 `(  0.00, -0.05,  0.00,  0.00, +0.18 )`

No candidate is created from the hidden truth label. Each candidate has identical L1 step cost `0.23`.

QF selects `P1,P2,P3,P4,P5` cyclically independent of detector output.

QA-removal selects the candidate with the lowest encoded disclosed response; QA-spoof selects the highest. Ties break by `P1 < P2 < ... < P5`. The policy may not access hidden `s` unless D3-D5 disclose its rounded scalar. For D1/D2/D6 it operates only on the ordinal encoding below.

Response encodings used only for policy comparison:

- D1: NOT_DETECTED=`0`, DETECTED=`1`;
- D2/D6: LOW=`0`, MEDIUM=`0.5`, HIGH=`1`; RATE_LIMITED repeats the last informative encoded value, or `0.5` if none exists;
- D3-D5: disclosed rounded scalar.

D4/D5 metadata may be used only by the inference classifier, not by the QA edit selector. This isolates score richness from explanatory-metadata richness.

## A4. Exact utility

Base utility by artifact state:

- A0 `1.00`
- A1 `0.97`
- A2 `0.95`
- A3 `0.92`
- A4 `0.96`

After `q` applied edits:

`utility = max(0, base_utility[A] - 0.008*q)`.

Utility is independent of detector score, hidden K label, and inference result. The primary utility floor remains `0.80`.

## A5. Exact partition

Each synthetic scope instance has exactly 12 artifacts:

- indices `0-3`: calibration;
- indices `4-7`: development/control only;
- indices `8-11`: holdout.

Holdout artifacts may not select thresholds, inference temperature, edit policies, materiality thresholds, or detector mappings.

## A6. Exact inference rule

The synthetic scope-class inference task predicts among `K1,K2,K3,K4` in the confirmatory core. K0 is a negative-control class and K5-K7 are exploratory sensitivity classes.

For each scenario/disclosure/query-mode/budget/state combination, construct a calibration template for each K1-K4 using only artifact indices 0-3 and the same query procedure applied in that condition.

Encode observations as numeric vectors:

- D0: empty vector and therefore uniform posterior;
- D1: each response `0/1`;
- D2/D6: LOW=`0`, MEDIUM=`0.5`, HIGH=`1`, RATE_LIMITED=`0.5`;
- D3: scalar response sequence;
- D4: D3 sequence followed by contribution bins NEG=`-1`, NEUTRAL=`0`, POS=`1` for each dimension/query;
- D5: D3 sequence followed by threshold-distance bands `-1.5,-0.5,+0.5,+1.5` and normalized active count `count/5`.

A class template is the elementwise mean calibration vector for that class.

For a holdout observation vector `x`, define squared distance `d_k = mean((x-template_k)^2)`. If vector is empty, all `d_k=0`.

Posterior weight:

`w_k = exp(-d_k / 0.05)`

`p_k = w_k / sum(w)`.

Prior is uniform over K1-K4. Predicted class is highest posterior; ties break K1<K2<K3<K4.

Entropy is base-2 Shannon entropy of `p`. Information gain is `2.0 - entropy(p)` bits because the four-class prior entropy is exactly 2 bits.

Candidate-set size is the count of classes with posterior `p_k >= 0.10`; if none, use 4 rather than manufacturing an empty candidate set.

This inference model is deliberately transparent. It does not recover secret keys and does not imply a deployed attacker possesses comparable templates.

## A7. Confirmatory core vs exploratory matrix

To avoid repeated-measures inflation and unnecessary compute, the confirmatory core is limited to:

- scenarios S1,S2,S3;
- K1-K4 only;
- D0-D6;
- QF for D0; QF and QA for D1-D6;
- budgets 4 and 16;
- artifact states A0, A1, A4;
- auxiliary states E0 and E3;
- holdout artifact indices 8-11.

Budget is irrelevant for D0; D0 is evaluated once per scenario/K/state/E and reused as the matched baseline rather than duplicated.

K0 is evaluated as a mandatory negative-control suite. K5-K7, budgets 1/8, and A2/A3 are exploratory sensitivity analyses and cannot satisfy confirmatory aggregate labels.

Repeated observations of the same holdout artifact across D/Q/budget conditions are repeated measures, not independent artifacts.

## A8. Auxiliary evidence and marginal composition

E0 uses the detector-derived posterior only; with D0 it is uniform.

E3 supplies a weak, deterministic auxiliary prior over K1-K4 generated from calibration-independent SHA-256 noise with the true class receiving only a small fixed log-weight advantage of `+0.12` and each other class a deterministic perturbation in `[-0.05,+0.05]`. E3 by itself is therefore intentionally weak.

For E3 + detector, combine by multiplying the normalized E3 prior and detector posterior elementwise, then renormalize.

The marginal detector gain is the change relative to the same artifact/E3 prior under D0. The E3 generator is frozen and cannot inspect detector outputs.

## A9. Confirmatory materiality

`MATERIAL_INFERENCE_GAIN` requires, relative to its matched D0 or D1 control:

1. either median information gain improvement `>= 0.20 bits` **or** scope-class accuracy improvement `>= 10 percentage points`;
2. median utility `>= 0.80`;
3. the criterion is satisfied in at least 2 of 3 scenarios for the same D/Q/budget/state/E comparison family.

Candidate-set reduction is descriptive and cannot trigger the label by itself.

`BINARY_ORACLE_LEAKAGE_OBSERVED` requires D1 vs D0 to satisfy the material inference gate at budget 16 in at least 2 scenarios.

`ADAPTIVE_ADVANTAGE_OBSERVED` requires QA vs QF at equal D/budget/state/E to improve median information gain by `>=0.10 bits` or scope-class accuracy by `>=10 percentage points` in at least 2 scenarios, with utility floor satisfied.

`MITIGATION_REDUCES_LEAKAGE` requires D6 vs the better of D3/D4 to reduce median information gain by `>=25%` relative while retaining at least `80%` of D3 clean detection utility and without increasing false-attribution rate by more than 5 percentage points.

No confirmatory label may emit if any mandatory control fails or if more than 20% of comparable core families are invalid.

## A10. Open-set/false-attribution rule

The detector-oracle study does not reuse v0.8 person attribution. It uses synthetic **scope-instance** open-set attribution to avoid pretending detector leakage is human identification.

For each scenario, represented scope instances and unknown holdout scope instances are disjoint. A represented instance is accepted only if:

- top posterior `>= 0.60`; and
- top1-top2 posterior margin `>= 0.15`.

These fixed synthetic thresholds are part of v0.9 and are not tuned from holdout. A single represented candidate is never treated as sufficient evidence.

False-attribution rate is the fraction of unknown-scope holdout artifacts accepted as a represented scope instance. This metric cannot be translated into a human false-accusation rate.

## A11. Repeated-query stability subtest

For each D1-D6 and budgets 4 and 16, one development artifact per K1-K4 is queried repeatedly without applying edits.

- D1-D5 responses must remain byte-identical across calls.
- D6 may change only according to its deterministic noise and must become `RATE_LIMITED` after the eighth informative call.

This subtest is a control and not counted as an independent inference result.

## A12. Implementation restriction

Implementation must encode the constants in this amendment verbatim. It may optimize caching/serialization only if tests demonstrate exact semantic parity.

No code may be written to canonicalize a preferred result label. Classification functions must accept synthetic fixture inputs that can force positive, null, and control-failed outcomes in unit tests.
