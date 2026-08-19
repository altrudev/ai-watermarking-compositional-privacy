# Validation Record v0.3

**Experiment:** Transformation-chain attribution persistence  
**Scope:** Synthetic-only  
**Reference population:** 12 synthetic persons / 144 synthetic generation events

## Exact-source checks before publication

- Python compile check for `lab/transformation_chain_lab.py`: **PASS**
- Python compile check for `tests/test_transformation_chain_lab.py`: **PASS**
- v0.3 adversarial regression suite: **12/12 PASS**
- deterministic reference experiment: **PASS**

## Test-contract notes

The suite intentionally does not require the final chain to achieve unlinkability. Requiring success would bias the research toward a desired conclusion.

The reference run instead produced a negative result: attribution dropped near random after summarization and then increased again after later transformations. The final bounded claim is therefore `NOT_SUPPORTED`.

## Preservation

v0.3 is additive. It does not modify the v0.1 or v0.2 experiment implementations, tests, result records, paper, citation metadata, or license.

## Evidence rules

**Privacy transformation ≠ privacy evidence.**  
**Failed re-identification ≠ proven anonymity.**  
**Intermediate unlinkability ≠ end-to-end unlinkability.**

## Environment limitation

The v0.3 exact-source suite was executed in the available local Python runtime. Because v0.1 and v0.2 files are unchanged in this transition, their previously published exact-source validation records remain the applicable evidence for those versions rather than being rewritten as new v0.3 evidence.