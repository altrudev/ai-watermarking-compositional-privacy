# Validation Record v0.5

**Date:** 2026-08-18

```text
python -m py_compile lab/robustness_lab.py tests/test_robustness_lab.py
PASS

python -m unittest discover -s tests -v
15/15 PASS

python -m lab.robustness_lab
PASS — 13-scenario reference report produced
```

## v0.4 parity

```text
expected min 25.694444% = observed 25.694444%
expected max 44.444444% = observed 44.444444%
expected spread 18.75 pp = observed 18.75 pp
best/worst paths exact match
PASS
```

## Robustness gate

```text
material scenarios: 12/13 (92.31%)
commuting negative control: PASS
claim: ROBUST_IN_DECLARED_MATRIX
```

## Exact-source SHA-256

- `lab/robustness_lab.py`: `002ef54768d32b1ec34f1c6fbf38bd08aacf42941081ff7693d5a7115deeefa7`
- `tests/test_robustness_lab.py`: `3d519086cf69d6a120571c5ae8fd92ecd7f59400e925fbf5bf272ab46e2323b6`
- `research/reference-report-v0.5.json`: `a7f3304b5673ffac1e93931cb0c177cdbe71e5f73a88470a84b6d601ab64bc99`

## Repository transition gate

Before merge, the branch diff must contain only new v0.5 lab/test/research files plus optional README integration. v0.1-v0.4, `paper.md`, `CITATION.cff`, and `LICENSE` must remain unchanged.
