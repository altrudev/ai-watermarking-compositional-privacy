# Detector-Oracle Protocol Final Amendment v0.9.2

**Status:** frozen final amendment before second DDC audit  
**Predecessors:** v0.9 draft + v0.9.1 amendment  
**Precedence:** this file overrides v0.9/v0.9.1 only for the clauses below. All other v0.9.1 constants remain frozen.  
**Implementation authorization:** still NO until second DDC audit PASS.

## B1. Query means one detector call

A primary query budget of `4` or `16` means exactly 4 or 16 detector calls per artifact for D1-D6.

At each query exactly one edit is applied, then the resulting artifact state is submitted once to the detector. Therefore every D1-D6 primary run has:

`number of applied edits == number of detector calls == query budget`.

No hidden candidate evaluation is permitted.

D0 makes zero detector calls but applies the same number of edits as the matched QF budget condition, preserving transformation/utility effort.

## B2. Edit-selection policy replaces v0.9.1 A3 selection semantics

The five frozen edit vectors P1-P5 remain unchanged.

### QF

For budget `b`, apply edits cyclically:

`P1,P2,P3,P4,P5,P1,...`

until `b` edits have been applied. Detector responses, when available, cannot alter this sequence.

### QA

QA uses only the previous disclosed response to choose the next edit. Query 1 always applies P1.

Let `r` be the previous response encoded into `[0,1]`:

- D1: NOT_DETECTED=`0`, DETECTED=`1`;
- D2/D6: LOW=`0`, MEDIUM=`0.5`, HIGH=`1`; RATE_LIMITED uses `0.5`;
- D3-D5: disclosed rounded scalar clamped to `[0,1]`.

For **removal mode** the next edit is:

- `r < 0.25` -> P1
- `0.25 <= r < 0.50` -> P2
- `0.50 <= r < 0.75` -> P4
- `r >= 0.75` -> P5

For **spoof mode** the next edit is:

- `r < 0.25` -> P5
- `0.25 <= r < 0.50` -> P4
- `0.50 <= r < 0.75` -> P2
- `r >= 0.75` -> P1

P3 is intentionally reserved as the QF-cycle-only probe. This creates a negative/control dimension that adaptive selection never directly prefers after query 1.

D4/D5 explanatory metadata remains unavailable to the QA selector and is available only to the inference classifier, as frozen in v0.9.1.

This policy is intentionally simple and may fail. It cannot inspect hidden score, alpha coefficients, K labels, or unqueried candidate outcomes.

## B3. D6 rate limit semantics

D6 calls 1-8 return their predeclared noisy coarse band. Calls 9-16 return `RATE_LIMITED` and reveal no score/band.

Every blocked request still counts as a detector call and consumes one edit. QA maps `RATE_LIMITED` to neutral `r=0.5`; inference encoding remains `0.5`.

## B4. D0 matching replaces v0.9.1 A7 D0 clause

D0 is evaluated separately at budgets 4 and 16. It applies the matching QF edit path, makes zero detector calls, and emits an empty observation vector.

D0/QA is prohibited because an adaptive policy without observations would be semantically meaningless.

D1-vs-D0 binary-leakage comparisons use D1/QF and matched D0/QF at the same budget/state/E condition. QA is evaluated only against QF within the same detector disclosure level.

## B5. Scope-class false attribution replaces v0.9.1 A10

The confirmatory classifier represents synthetic scope classes K1-K4. K0 and K5-K7 are **unrepresented/unknown classes** for the open-set false-attribution control.

For an artifact from K0 or K5-K7, the K1-K4 classifier still produces a posterior because those are the only represented classes. It must abstain unless both are true:

- top posterior `>= 0.60`;
- top1-top2 posterior margin `>= 0.15`.

If both conditions hold, the unknown artifact is recorded as a `FALSE_SCOPE_CLASS_ATTRIBUTION` to the predicted K1-K4 class.

False-attribution rate is:

`accepted unknown-class holdout artifacts / all evaluated unknown-class holdout artifacts`.

This is a synthetic class-confusion metric only. It is not a person, account, session, or deployed-model accusation rate.

K0 remains additionally subject to the no-watermark negative detector control; K5-K7 remain exploratory with respect to positive inference labels but mandatory for this false-attribution safety metric.

## B6. Confirmatory core count and repeated measures

Core positive-inference families are evaluated over:

- 3 scenarios;
- K1-K4;
- states A0,A1,A4;
- E0,E3;
- budgets 4,16;
- D0/QF;
- D1-D6 each under QF and QA-removal and QA-spoof.

The same artifact observed under multiple conditions is a repeated measure. Aggregate scenario-level thresholds operate on per-artifact summaries first; raw cell-event counts must never be described as independent samples.

K0/K5-K7 false-attribution controls are reported separately and cannot inflate the positive core denominator.

## B7. Detector score optimization metric

For M5, the baseline is the final hidden detector score after matched QF edits. QA-removal advantage is:

`QF_final_score - QA_removal_final_score`.

QA-spoof advantage is:

`QA_spoof_final_score - QF_final_score`.

The hidden score is used only for post-run metric calculation, never by QA policy selection. Positive optimization advantage cannot by itself trigger `MATERIAL_INFERENCE_GAIN`; it is a separate security result.
