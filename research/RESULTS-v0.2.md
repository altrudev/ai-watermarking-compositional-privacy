# Reference Results v0.2 — Textual Compositional Privacy Benchmark

**Status:** Experimental synthetic benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities, synthetic text, and abstract provenance signals only  
**Schema:** `altru.dev/textual-compositional-privacy-benchmark/0.2`

## Headline result

The v0.2 reference run generated **288 synthetic text generations** across **36 synthetic people**, 72 synthetic accounts, and 144 synthetic sessions.

Unlike v0.1, semantic, lexical, and stylometric evidence is derived from the generated text itself rather than supplied as pre-built abstract author vectors.

| Condition | Person top-1 | Generation top-1 | Generation top-5 |
|---|---:|---:|---:|
| Combined provider + publisher baseline | 74.65% | 46.88% | 100.00% |
| Provenance/provider signal removed only | 71.88% | 35.76% | 92.01% |
| Composite transform + adaptive attack | 6.77% | 4.69% | 23.96% |

The strongest single signal was **style at 56.60% person top-1**. Combined provider-plus-publisher evidence reached **74.65%**, producing a measured **18.06 percentage-point compositional correlation gain**.

Removing only the simulated provenance/provider channel left **71.88%** person attribution. In this synthetic model, provenance removal therefore did not remove the majority of residual identity linkage.

## Single-signal person attribution

| Signal | Person top-1 |
|---|---:|
| lexical | 23.61% |
| provider | 4.17% |
| semantic | 32.29% |
| style | 56.60% |
| time | 10.76% |
| watermark | 8.33% |

## Adaptive attack

The composite privacy result is not evaluated only against the original fixed weighting. The benchmark uses the first third of transformed artifacts as an isolated calibration set, measures which signals remain useful, then reweights the attack and evaluates the remaining artifacts.

Under that adaptive attack, full-strength composite transformation produced **6.77% person top-1** and **4.69% generation top-1**.

This is bounded evidence for the declared synthetic experiment. It is not an anonymity claim.

## Privacy / utility frontier

| Strength | Person top-1 | Generation top-1 | Semantic retention | Exact-content retention |
|---:|---:|---:|---:|---:|
| 0.00 | 85.42% | 70.83% | 100.00% | 100.00% |
| 0.25 | 52.60% | 44.27% | 100.00% | 89.91% |
| 0.50 | 39.06% | 25.52% | 100.00% | 74.84% |
| 0.75 | 32.81% | 19.27% | 100.00% | 70.02% |
| 1.00 | 6.77% | 4.69% | 100.00% | 61.18% |

The benchmark’s semantic-retention metric is **100.00%** at full transformation while exact content-feature retention is **61.18%**. These are controlled benchmark metrics, not human-quality or deployed-model utility scores.

## Transformations in v0.2

1. remove the abstract provider/model provenance marker and provider hint;
2. add publication-time delay;
3. normalize synthetic lexical signature words;
4. normalize punctuation, recurring phrase habits, and sentence structure;
5. generalize selected topic terms through deterministic neutral substitutions.

Each transformed artifact is attacked again rather than treated as private because the transformation executed.

## Claim gate

Reference result: `SUPPORTED_FOR_DECLARED_TEST`

The harness may emit only `SUPPORTED_FOR_DECLARED_TEST` or `NOT_SUPPORTED`. It does not emit `ANONYMOUS`, `UNTRACEABLE`, or a claim about a deployed provider.

## Interpretation boundary

- Synthetic identities only.
- Synthetic text only.
- Abstract simulated provenance signal only.
- No real provider detector.
- No real accounts, conversations, provider logs, social profiles, or people.
- Privacy transformation ≠ privacy evidence.
- Fixed-attack failure ≠ adaptive-attack failure.
- Failed re-identification ≠ proven anonymity.

## Reproduction

```bash
python -m unittest discover -s tests -v
python -m lab.textual_benchmark
```

The machine-readable record is [`reference-report-v0.2.json`](reference-report-v0.2.json).
