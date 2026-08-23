# Detector-Oracle Protocol Execution Mapping v0.9.3

**Status:** frozen result-critical mapping before second DDC audit  
**Precedence:** supplements v0.9 + v0.9.1 + v0.9.2; does not alter their hypotheses or thresholds.  
**Implementation authorization:** still NO until second DDC audit PASS.

## C1. Exact deterministic hash-to-unit mapping

Whenever the protocol says a SHA-256 value is mapped deterministically to a numeric interval:

1. compute SHA-256 over the exact UTF-8 string specified by the protocol;
2. take digest bytes `0..7` as an unsigned big-endian 64-bit integer `u`;
3. define `r = u / (2^64 - 1)` in `[0,1]`;
4. map to `[lo,hi]` by `lo + r*(hi-lo)`.

No Python process hash, platform RNG, or locale-dependent conversion may be used.

This mapping governs initial `z`, artifact `eps`, D6 noise, and E3 perturbation values.

## C2. Exact represented/unknown population assignment

Synthetic scope instances are assigned as follows.

### S1

Represented: 8 instances total — 2 each of K1,K2,K3,K4.  
Unknown controls: 8 instances total — 2 each of K0,K5,K6,K7.

### S2

Represented: 16 instances total — 4 each of K1,K2,K3,K4.  
Unknown controls: 8 instances total — 2 each of K0,K5,K6,K7.

### S3

Represented: 24 instances total — 6 each of K1,K2,K3,K4.  
Unknown controls: 12 instances total — 3 each of K0,K5,K6,K7.

Instance IDs are exactly:

`syn-{scenario}-{K}-scope-{ordinal:02d}`

with ordinal starting at `00` within each K class.

Each instance has artifacts `00..11`. Artifact identity is:

`syn-{scenario}-{K}-scope-{ordinal:02d}-artifact-{index:02d}`.

These IDs are experiment truth/custody labels only. Detector score computation may use the instance/artifact string as a seed source but may not emit it in D1-D6 responses.

## C3. Calibration template aggregation

For K1-K4, the class template in each condition is the elementwise mean of encoded observation vectors from **all represented instances of that K class, artifact indices 0-3 only**.

Development indices 4-7 are used only for controls/stability tests. Holdout indices 8-11 are used only for evaluation.

No template may be recomputed after holdout results are observed.

## C4. E3 exact prior

For represented K1-K4 holdout/calibration artifacts, construct log-weights for candidate classes C in K1-K4:

`logw[C] = perturb(C) + (0.12 if C == true_K else 0)`

where `perturb(C)` is hash-mapped to `[-0.05,+0.05]` from:

`E3|artifact_id|candidate_class`.

Normalize with softmax to obtain the E3 prior.

For unknown K0/K5-K7 artifacts, **no candidate receives the +0.12 term**. Their E3 log-weights consist only of the deterministic perturbations. This prevents the auxiliary channel from inventing a represented-class truth for an unknown source.

The E3 prior is an intentionally synthetic correlated evidence channel. Its construction must be disclosed in results and must never be described as naturally occurring metadata.

## C5. Auxiliary combination

For E0, final posterior equals detector posterior.

For E3, final unnormalized weight for candidate K is:

`q[K] = detector_posterior[K] * E3_prior[K]`.

Normalize `q` to sum to 1. If numerical underflow produces a zero sum, the cell is invalid rather than replaced with a preferred posterior.

Information gain and accuracy for E3 conditions are computed on this combined posterior. Marginal detector gain compares it with the same E3 prior under D0.

## C6. Observation flattening

Observation vectors are flattened in query order.

- D1/D2/D3/D6: one numeric value per query.
- D4: for each query append `[score, bin0, bin1, bin2, bin3, bin4]`.
- D5: for each query append `[score, distance_band, active_count/5]`.

A `RATE_LIMITED` D6 response encodes as `0.5`.

All calibration and holdout vectors in a compared condition must have identical length.

## C7. Scope-class accuracy and entropy aggregation

Accuracy is computed first per artifact, then averaged within scenario/condition. Entropy/information gain is computed per artifact, then the scenario median is used for materiality gates.

Repeated observations of the same artifact under different D/Q/budget/state/E cells are never pooled as independent samples to manufacture sample size.

## C8. Unknown false-attribution evaluation conditions

Mandatory false-attribution controls use unknown K0/K5-K7 holdout artifacts under:

- states A0 and A4;
- E0 and E3;
- D0-D6;
- budgets 4 and 16;
- QF for D0 and QF/QA-removal/QA-spoof for D1-D6.

The K1-K4 calibration templates remain the same represented-class templates used by the matching condition. Unknown controls cannot enter template construction.

## C9. Result label precedence

If any mandatory control fails, the overall classification is `CONTROL_FAILED` regardless of positive metric thresholds.

Otherwise labels are independent findings rather than mutually exclusive narratives:

- `MATERIAL_INFERENCE_GAIN` may be emitted per comparison family;
- `BINARY_ORACLE_LEAKAGE_OBSERVED` may be emitted if its exact gate passes;
- `ADAPTIVE_ADVANTAGE_OBSERVED` may be emitted if its exact gate passes;
- `MITIGATION_REDUCES_LEAKAGE` may be emitted if its exact gate passes;
- `FALSE_SCOPE_CLASS_ATTRIBUTION_OBSERVED` is emitted if any mandatory unknown-control family has a non-zero accepted false-attribution rate.

A final summary classification is:

1. `CONTROL_FAILED` if a mandatory control fails;
2. `DETECTOR_MEDIATED_INFERENCE_OBSERVED` if any confirmatory inference label emits;
3. `FALSE_ATTRIBUTION_ONLY_OBSERVED` if no confirmatory inference label emits but false scope-class attribution occurs;
4. `NO_PREDECLARED_EFFECT_ESTABLISHED` otherwise.

The summary label does not erase adverse/null sub-results.
