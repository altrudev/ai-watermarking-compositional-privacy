# Reproducibility and Runtime Contract

**Status:** normative reproducibility guidance  
**Effective date:** 2026-08-22

## Python runtime

The supported runtime floor for the active research repository is now **Python 3.11 or newer**.

This is a prospective repository support policy. It does not rewrite or reinterpret the interpreter versions used for historical experiment runs when those versions were not recorded.

The governance-hardening audit environment reported **Python 3.13.5**. That interpreter observation is environment evidence only; it is not by itself a whole-repository regression result.

## Canonical test command

The repository-wide regression command is:

```bash
python -m unittest discover -s tests -v
```

The corresponding compile gate is:

```bash
python -m py_compile lab/*.py tests/*.py
```

A future result that depends on new executable code must record:

- exact canonical or candidate commit;
- Python version;
- compile result;
- complete test command and pass/fail count;
- deterministic replay evidence where the protocol requires it;
- exact source/blob identity for result-critical files.

## Exact-head rule

A test result applies only to the bytes actually executed.

> **Test command != proof of tested bytes.**

> **Passing tests on a reconstruction != proof of a clean network clone.**

> **Documentation-only drift != executable drift, but it must still be identified.**

If a clean checkout cannot be obtained because the execution environment cannot reach GitHub, the verification record must say so. An exact executable tree reconstructed from verified Git blobs may provide strong executable-tree evidence, but it must not be labeled a clean-checkout proof.

## Current v0.8 status

The v0.8 result has exact candidate-blob validation, focused test evidence, deterministic complete replay, and exact evidence hashes recorded in its validation/audit lineage.

The later repository-level audit found that the current `main` differs from the canonical v0.8 experiment only in documentation/governance records. A fresh network-cloned whole-repository regression run at the current head remains a separate proof gate until executed in an environment with repository network access.

## No GitHub Actions

This repository does not use GitHub Actions as a required validation mechanism. Reproducibility evidence must therefore be retained through explicit local/external execution records and exact Git lineage rather than inferred from a CI badge.
