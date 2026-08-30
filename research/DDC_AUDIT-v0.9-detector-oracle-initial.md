# DDC Adversarial Protocol Audit — v0.9 Detector Oracle (Initial)

**Protocol audited:** `research/TEST_PLAN-v0.9-detector-oracle.md` at `da81f93f7e275d2e87358c8e359a5dd529c7d98d`  
**Base:** `9301a74301e8ab3e11306225773c0f551d03055d`  
**Scope:** synthetic-only  
**Decision:** **FAIL — REPAIR BEFORE IMPLEMENTATION**

## Audit question

Can an implementation conform to the written protocol while materially changing the probability of obtaining the preferred detector-leakage result?

**Answer: yes.** The draft correctly freezes the research boundary, disclosure levels, query budgets, broad metrics, controls, and claim boundaries, but several result-critical functions remain underdetermined.

## Findings

### F1 — hidden detector function underdetermined — BLOCKING

The protocol requires a deterministic hidden score in `[0,1]` but does not freeze its formula, threshold, signal/noise decomposition, scope offsets, transformation effects, or calibration distribution.

An implementation could choose a detector landscape that is trivially learnable, nearly flat, or arbitrarily noisy while still claiming protocol compliance.

**Repair:** freeze an explicit synthetic score function and all constants before implementation.

### F2 — inference/posterior method underdetermined — BLOCKING

M1 entropy reduction, M2 candidate reduction, and M3 hidden-scope classification require an inference model, but the protocol does not specify how detector observations update candidate probabilities.

Different posterior rules could create or suppress apparent leakage.

**Repair:** freeze a simple transparent candidate-likelihood rule and prior. Retain detector score optimization as a separate metric so inference is not conflated with attack success.

### F3 — D1/D2/D6 disclosure mappings incomplete — BLOCKING

The binary threshold, confidence-band cut points, D6 noise distribution/amplitude, and D6 rate-limit semantics are not frozen.

**Repair:** predeclare exact mappings.

### F4 — edit operators insufficiently specified — BLOCKING

The five edit proxies are named but not mathematically defined. An implementation could make one candidate edit directly encode the desired score direction.

**Repair:** define edits as deterministic perturbations of a synthetic observable feature vector, with bounded L1 magnitude and an independently calculated utility penalty.

### F5 — utility metric underdetermined — BLOCKING

The protocol sets a utility floor of `0.80` without defining utility.

**Repair:** freeze a deterministic utility function based only on declared transformation cost, independent of detector score and hidden truth.

### F6 — spoof-proxy A4 risks truth leakage — BLOCKING

The draft says A4 alters the detector statistic without copying labels, but does not define how. This is exactly the location where hidden truth could leak into observables.

**Repair:** A4 must be an externally chosen, deterministic feature perturbation independent of target hidden scope. It may test false-positive susceptibility but cannot be optimized from the true target label.

### F7 — matrix is unnecessarily confounded/oversized — MATERIAL

The full cross product of `S × K × D × Q × budget × A × E` creates tens of thousands of condition cells before artifact repetitions. Several combinations are analytically redundant, particularly D0 across detector budgets and query modes.

This creates compute burden and increases the chance of repeated-measures overcounting.

**Repair:** define a smaller confirmatory core matrix and a separately labeled exploratory sensitivity matrix. Do not count repeated budget/disclosure observations as independent artifacts.

### F8 — D0 parity semantics ambiguous — MATERIAL

D0 has no detector queries but the draft says artifact-generation effort is held constant. It does not specify which edited artifact is used for comparison.

**Repair:** D0/QF uses the deterministic frozen path. D0/QA is prohibited because adaptivity without observations is meaningless.

### F9 — calibration partition not concrete — BLOCKING

The protocol says calibration and holdout scopes are disjoint but does not freeze which deterministic artifact indices belong to each partition.

**Repair:** use artifact indices `0-3` calibration, `4-7` development/control, `8-11` holdout; holdout inaccessible to thresholds or policy selection.

### F10 — materiality rule uses disjunctive metric gate — MATERIAL

`candidate reduction OR classification gain OR entropy gain` may produce a positive label from a metric whose interpretation is weak in a specific cell.

**Repair:** require at least one information metric (entropy or classification) plus utility, and report candidate reduction descriptively. Attack optimization gets separate labels.

### F11 — architecture/key-scope inference wording too broad — MATERIAL

The protocol risks allowing a synthetic K-class classification result to be described as architecture inference.

**Repair:** rename this metric `synthetic scope-class inference`; prohibit claims about actual key architecture or key recovery.

### F12 — response-stability leakage needs exact repeated-query control — MATERIAL

The protocol mentions repeated identical queries but does not freeze a repeated-query subtest.

**Repair:** add a fixed identical-query control at budgets 4 and 16 for D1-D6; any D1-D5 variation is a control failure; D6 may vary only from deterministic noise.

## DDC invariant review

- **Need != Authority:** PASS. Research interest does not expand to provider access or real identities.
- **Data != Authority:** PASS. External papers are hypothesis-generating evidence only.
- **Detection != Attribution:** PASS in wording; must remain enforced in implementation.
- **Candidate reduction != evidence creation:** PASS in wording; metric design needs F2 repair.
- **Synthetic evidence != deployed-provider evidence:** PASS.
- **Rules before results:** **FAIL until F1-F6/F9 are repaired.**

## Decision

**`FAIL_PROTOCOL_UNDERSPECIFIED`**

Implementation and canonical execution remain unauthorized.

A repaired protocol may proceed to a second DDC audit. The second audit must verify that all result-critical functions and partition semantics are frozen before any implementation-derived result is observed.
