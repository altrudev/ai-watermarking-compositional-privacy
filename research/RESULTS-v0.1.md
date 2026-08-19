# Reference Results v0.1

**Status:** Experimental synthetic benchmark  
**Date:** 2026-08-18  
**Scope:** Synthetic identities and abstract linkage signals only

## Headline result

The reference run generated 480 synthetic generation events and measured how multiple weak linkage channels compose under a provider-plus-publisher adversary.

| Condition | Person top-1 | Generation top-1 | Generation top-5 |
|---|---:|---:|---:|
| Combined baseline | 82.08% | 72.92% | 98.33% |
| Provenance marker removed only | 56.88% | 43.33% | 86.67% |
| Composite privacy transform | 5.42% | 1.46% | 7.29% |

The result demonstrates two properties **inside this synthetic model**:

1. removing the simulated watermark/provenance channel alone leaves substantial residual linkability;
2. reducing several linkage dimensions together is materially more effective than treating any one channel as the identity problem.

## Single-signal person-attribution results

| Signal | Person top-1 |
|---|---:|
| Semantic similarity | 21.46% |
| Style similarity | 34.17% |
| Simulated watermark family | 10.00% |
| Timing | 5.21% |

Combined provider-plus-publisher person attribution was **82.08%**.

The measured correlation gain was therefore:

```text
82.08% - 34.17% = 47.91 percentage points
```

This is the reference experiment's direct test of:

> **Component Privacy ≠ Compositional Privacy**

## Composite transformation

The reference composite transformation performs four independent operations:

1. remove the simulated provider/model provenance marker and provider hint;
2. delay publication time by six hours;
3. generalize the semantic representation toward the population centroid;
4. normalize the style representation toward the population centroid.

After this transformation:

- person top-1 attribution: **5.42%**
- generation top-1 attribution: **1.46%**
- mean near-best anonymity set: **3.58 candidates**
- mean semantic retention: **78.82%**
- mean style retention: **67.90%**

Under the v0.1 declared thresholds, the harness returns:

`SUPPORTED_FOR_DECLARED_TEST`

It deliberately does **not** return `ANONYMOUS` or `UNTRACEABLE`.

## Interpretation boundary

These results validate the research apparatus and demonstrate compositional linkage behavior in the controlled synthetic model. They do not establish the behavior of Anthropic, Claude, SynthID, OpenAI, Gemini, or any other deployed system.

The simulated watermark is an abstract provider/model provenance channel. It is not an implementation or emulation of a proprietary watermark.

## Reproduction

```bash
python -m unittest discover -s tests -v
python -m lab.unlinkability_lab
```

The reference run uses deterministic seeds. A changed population size, seed, scoring policy, feature construction, adversary evidence scope, or transformation strength constitutes a different experiment and should produce a separately identified result record.
