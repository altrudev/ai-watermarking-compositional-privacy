# Test Plan v0.4 — Transformation Path Dependence

## Purpose

Determine whether residual attribution depends on the **ordered transformation history** even when the same privacy-relevant transformations are applied exactly once.

## DDC transition framing

**Authority**  
Research-only authority over synthetic identities and generated artifacts.

**Intent**  
Test whether transformation order materially changes residual person/generation attribution.

**Preconditions**
- synthetic identities only;
- no real user/account/provider data;
- deterministic fixed seed;
- fixed attribution model;
- same starting artifacts for every path.

**Transition**
Apply every permutation of the same four-transform multiset:
- paraphrase;
- summarize;
- translate proxy;
- model-edit proxy.

**Affected dimensions**
- lexical surface;
- semantic representation;
- stylometry;
- provenance metadata;
- publication timing;
- transformation lineage;
- residual attribution.

**Verification**
- enumerate all 24 permutations;
- verify every path contains every transform exactly once;
- verify final metadata is identical across paths;
- verify simulated provider/watermark values are removed on every path;
- measure person/generation attribution per path;
- measure utility per path;
- compare best/worst paths;
- compare first/last-position effects;
- compare pairwise ordering effects.

**Invariant preservation**
- synthetic-only boundary;
- no network identity resolution;
- no proprietary watermark emulation;
- unchanged v0.1/v0.2/v0.3 experiment files;
- bounded claims only.

**Evidence**
- deterministic machine-readable report;
- human-readable results;
- test suite;
- branch/PR lineage.

**Recovery**
The experiment is additive. Revert the v0.4 merge without altering prior experiments.

## Primary hypothesis

H1:

> The same transformation multiset can yield materially different residual attribution when transformation order changes.

Materiality threshold for the reference test:

`person-top1 spread >= random-person baseline`

With 12 synthetic persons, the threshold is 8.33 percentage points.

## Null

H0:

> Transformation order does not create a material attribution difference under the declared threshold.

## Controls

The experiment must fail closed if:
- a path omits or repeats a transformation;
- final metadata differs between paths;
- real identity data is introduced;
- provenance removal is inconsistent;
- the path count is not exactly 24.

## Required measurements

- person top-1;
- generation top-1;
- generation top-5;
- mean generation rank;
- mean near-best anonymity set;
- semantic retention;
- content-word retention;
- length ratio;
- final aggregate artifact digest;
- first-transform mean effect;
- last-transform mean effect;
- pairwise order effects.

## Claim rule

A `path_dependent` result is bounded to:
- this synthetic population;
- this seed;
- these deterministic transformations;
- this attribution model;
- this materiality threshold.

It is not a universal claim about AI text anonymization.
