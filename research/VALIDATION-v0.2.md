# Validation Record v0.2

**Experiment:** Actual synthetic-text unlinkability lab  
**Branch:** `research/text-unlinkability-lab-v0.2`  
**Date:** 2026-08-18

## Pre-publication validation

The exact v0.2 source and test files were executed locally before publication.

```text
python -m py_compile lab/text_unlinkability_lab.py tests/test_text_unlinkability_lab.py
PASS

python -m unittest discover -s tests -v
v0.2 text suite: 12/12 PASS

deterministic reference experiment
24 synthetic persons / 288 generation events
PASS
```

## Reference-result verification

```text
combined person top-1                 81.9444%
strongest individual person top-1    20.8333%
correlation gain                      61.1111 percentage points
provenance removed person top-1       28.4722%
composite person top-1                 3.1250%
composite generation top-1             0.6944%
mean topic retention                  84.0386%
mean content-word retention           85.5067%
mean length retention                 91.1936%
```

## Scope verification

The v0.2 implementation contains no network client, URL endpoint, CSV/dataframe loader, or real-identity import path. Identity-bearing records are generated internally and enforced under the `syn-` namespace.

## Regression preservation

The v0.2 branch does not modify:

- `lab/unlinkability_lab.py`
- `tests/test_unlinkability_lab.py`
- `research/RESULTS-v0.1.md`
- `research/reference-report-v0.1.json`
- `paper.md`
- `CITATION.cff`
- `LICENSE`

Therefore v0.1 remains an independently preserved experiment rather than being rewritten to fit v0.2.

## Claim gate

Validation of this experiment does not authorize the claims `ANONYMOUS`, `UNTRACEABLE`, or equivalent universal privacy claims.

Standing rules remain:

> **Privacy transformation ≠ privacy evidence**

> **Failed re-identification ≠ proven anonymity**
