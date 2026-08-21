# Validation Record v0.7 — Cross-Family / Cross-Policy Replication

**Scope:** synthetic-only v0.7 candidate  
**Protocol commit:** `786ebb3d097d999e15f72cbfce536e59566206a1`  
**Candidate branch:** `agent/implement-v0.7-replication`

## Rules-before-results

PASS.

The protocol and all claim thresholds were merged before the implementation/reference result branch. No post-result threshold changes are authorized.

## Exact-source execution gate

PASS for the declared executable test boundary before evidence-only packaging changes.

Verified executable/test blobs:

- `lab/cross_family_replication_lab.py`: `028f98e068ba4f6b004920930a2aa49f3e69d488`
- `tests/test_cross_family_replication_lab.py`: `c123d5e592ef4a7947b372a123fddb9170dc373b`
- `lab/cross_family_replication_diagnostics.py`: `235c782ba7a27e4613735b2aabddaf4fe5566ad2`
- `tests/test_cross_family_replication_diagnostics.py`: `cc04e5019b6287acad930d17b4b25d54337d7a74`
- unchanged `lab/noncommutativity_lab.py`: `f0269836e2b4d611b1aff6eee2f85a5c7b9013a3`
- unchanged `lab/transformation_chain_lab.py`: `30b9bde830eaa8f00771957d50ed78d21979fa49`
- unchanged `lab/__init__.py`: `777d869e40e35d20a35d2296d5298305cd943c4d`

## Execution results

- Python compilation: **PASS**.
- focused v0.7 regression + diagnostics suites: **15 / 15 PASS**.
- historical scorer parity: **PASS in every scenario**.
- five-policy matrix scorer parity: **PASS in every scenario**.
- commuting negative controls: **PASS for every scenario/policy**.
- explicit final text equality: **PASS**.
- explicit final metadata equality: **PASS**.

Two complete six-scenario aggregate executions serialized byte-identically with sorted compact JSON:

`SHA-256 1ab3c89b689ab0660203d2b12aded49290039132c576d8a7b61d7f5732be2fff`

The generated compact holdout artifact has Git blob:

`5c25ec32180e5142fe479851993d6697fee7ae66`

which exactly matches the `research/holdout-matrix-v0.7.json` already retained in the candidate.

The retained transfer matrix was generated from the same reproduced aggregate result:

- transfer cells: **30**;
- SHA-256: `55ea60f23c40685a2d3060638f4f0f83cea892c413d68babbf1fd6979d58f70d`;
- Git blob: `148c68c09a0ddeeceea8da24d78bf018d2467f94`.

The complete pairwise diagnostics plus explicit control evidence are retained as deterministic gzip/base64 text:

- decoded JSON SHA-256: `0d0fe799220f999780ce0fa01501561121b6e01ee8d56d4b3aeb57de5e7cfe29`;
- deterministic gzip (`mtime=0`) SHA-256: `b2782e197037be917db976d5dbdae8baa15d50c20606f7dcd5f92f6c5fd57211`.

Decode locally with standard Python:

```bash
python - <<'PY'
from pathlib import Path
import base64, gzip
src = Path('research/pairwise-diagnostics-v0.7.json.gz.b64').read_text().strip()
Path('pairwise-diagnostics-v0.7.json').write_bytes(gzip.decompress(base64.b64decode(src)))
PY
```

## Evidence-package repair boundary

The post-execution additions are evidence-only artifacts. They do not modify:

- transformations;
- adversary policies;
- scenarios, populations or seeds;
- calibration/holdout partitioning;
- transfer pairs;
- scorer semantics;
- claim thresholds;
- aggregate claim classification;
- authority or privacy boundaries.

Therefore the already verified executable candidate remains the tested source boundary, while the added files close the predeclared T2/T8 retention defect.

## Reference classification

`MECHANISM_NOT_REPLICATED`

- holdout predictive: **5 / 60**;
- transfer supported: **3 / 30**;
- median holdout Pearson `r`: **0.0**;
- median transfer Pearson `r`: **0.0**.

The adverse result is preserved unchanged.

## DDC boundary

No real people, real accounts, provider logs, private conversations, scraped identity datasets, production watermark detectors, production credentials or external execution authority were introduced.

**Designed ≠ Implemented ≠ Tested ≠ Recovery-proven ≠ Production-authorized.**

This validation record supports **Tested** only for the declared synthetic v0.7 experiment boundary. It does not assert recovery proof, production authorization or real-world validity.
