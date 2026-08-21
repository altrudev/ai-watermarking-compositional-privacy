# DDC Audit — v0.7 Cross-Family Replication Candidate

**Status:** merge-gate audit complete; candidate evidence package complete  
**Protocol:** `786ebb3d097d999e15f72cbfce536e59566206a1`  
**Canonical predecessor:** `c29b40db9000d3e0a49c2c25fadab215d3084480`

## Authority and scope

The v0.7 continuation remains inside the synthetic research envelope authorized by H/R Native's `RESEARCH_CONTINUATION-20260820` program.

No real people, real accounts, provider logs, private conversations, scraped identity datasets, production watermark detectors, proprietary model APIs, production credentials, destructive operations, or new authority capabilities are introduced.

## DDC distinctions preserved

- Published research object ≠ active research program ≠ experiment ≠ experimental result ≠ validated invariant.
- Privacy transformation ≠ privacy evidence.
- Failed re-identification ≠ proven anonymity.
- Synthetic benchmark mechanism ≠ deployed-provider mechanism.
- Replication failure ≠ permission to tune the protocol after observing results.
- Experimental evidence ≠ H/R Native constitutional authority.
- Local mechanism evidence ≠ robust cross-family system property.

## Rules-before-results

**PASS.**

The v0.7 protocol and thresholds were merged at `786ebb3d097d999e15f72cbfce536e59566206a1` before implementation/reference execution.

Frozen interpretation gates remain:

- holdout predictive: `r >= 0.70`;
- transfer supported: `r >= 0.50`;
- replicated aggregate: `H >= 42`, `T >= 15`, required medians and coverage;
- not replicated: `H < 30` or `T < 9` after controls/parity pass.

No threshold changed after the result was observed.

## Candidate architecture

The candidate is additive relative to the canonical predecessor and leaves historical v0.1-v0.6 source/result files unchanged.

It uses two new four-transform families, five frozen adversary policies, six frozen population/seed scenarios, deterministic calibration/holdout partitioning, calibration-only pairwise estimation, holdout-only primary evaluation, three frozen cross-scenario transfers, historical scorer parity, multi-policy scorer parity and commuting controls.

## Finding DDC-v0.7-01 — incomplete T2 diagnostics

**Original severity:** merge-blocking evidence defect, not a scoring defect.  
**Disposition:** repaired and verified.

The original candidate did not retain every T2 diagnostic field. The additive `lab/cross_family_replication_diagnostics.py` repair now records lexical/semantic/style divergence, all six declared scorer channels including provider-only evidence, policy order effects, ties for largest changed channels, and explicit final text/metadata equality for the commuting control.

The repair changes no transform, policy, scenario, seed, partition, scorer, threshold or claim classification.

## Finding DDC-v0.7-02 — incomplete T8 immutable evidence retention

**Original severity:** merge-blocking evidence-package defect, not a scoring defect.  
**Disposition:** repaired.

The predeclared reporting contract requires retention of the complete 60-cell holdout matrix, complete 30-cell transfer matrix and complete T2 pairwise diagnostic set.

The candidate now retains:

- `research/holdout-matrix-v0.7.json` — 60 holdout cells;
- `research/transfer-matrix-v0.7.json` — 30 transfer cells;
- `research/pairwise-diagnostics-v0.7.json.gz.b64` — complete six-scenario T2 diagnostics plus explicit T5 controls, deterministically gzip-compressed and base64 encoded;
- `research/RESULTS-v0.7.md`;
- `research/CLAIM_REGISTER-v0.7.md`;
- `research/VALIDATION-v0.7.md`.

Decoded diagnostics JSON SHA-256:

`0d0fe799220f999780ce0fa01501561121b6e01ee8d56d4b3aeb57de5e7cfe29`

## Exact execution and determinism gate

**PASS for the declared executable/test boundary.**

Verified blobs:

- replication source `028f98e068ba4f6b004920930a2aa49f3e69d488`;
- replication tests `c123d5e592ef4a7947b372a123fddb9170dc373b`;
- diagnostics source `235c782ba7a27e4613735b2aabddaf4fe5566ad2`;
- diagnostics tests `cc04e5019b6287acad930d17b4b25d54337d7a74`;
- canonical noncommutativity dependency `f0269836e2b4d611b1aff6eee2f85a5c7b9013a3`;
- canonical transformation-chain dependency `30b9bde830eaa8f00771957d50ed78d21979fa49`;
- canonical lab initializer `777d869e40e35d20a35d2296d5298305cd943c4d`.

Verification evidence:

- Python compilation: **PASS**;
- focused suites: **15/15 PASS**;
- historical scorer parity: **PASS in every scenario**;
- five-policy matrix scorer parity: **PASS in every scenario**;
- commuting controls: **PASS**;
- explicit final text equality: **PASS**;
- explicit final metadata equality: **PASS**;
- two full six-scenario executions: **byte-identical**;
- aggregate sorted compact JSON SHA-256: `1ab3c89b689ab0660203d2b12aded49290039132c576d8a7b61d7f5732be2fff`;
- generated holdout Git blob: `5c25ec32180e5142fe479851993d6697fee7ae66`, exactly matching the retained candidate artifact.

The post-verification additions are evidence-only files. They do not alter the already-tested executable source boundary.

## v0.1-v0.7 lineage audit

**PASS with a negative v0.7 replication result.**

The lineage remains internally consistent:

1. v0.1 established the compositional-privacy threat model and synthetic unlinkability testing boundary.
2. v0.2 moved to actual synthetic text while retaining explicit non-claims about deployed providers and real identities.
3. v0.3 established that privacy improvement need not be monotonic across a transformation chain.
4. v0.4 established path dependence for a fixed transform set and benchmark.
5. v0.5 explicitly required perturbation testing before promotion and preserved a zero-spread negative condition.
6. v0.6 identified pairwise non-commutativity as a strongly predictive **local synthetic mechanism**, while explicitly declining to claim universality or transferability.
7. v0.7 independently tested that broader proposition under new families, policies, seeds, populations, holdout partitions and cross-scenario transfer. It **did not replicate broadly**.

There is therefore no contradiction requiring historical rewriting. v0.7 narrows the maturity of v0.6 rather than invalidating its exact benchmark result.

The evidence-supported lineage implication is:

> Pairwise transformation non-commutativity can be strongly predictive in a particular synthetic benchmark, but that predictiveness is context-dependent and must not be promoted into a robust system property without independent cross-family, cross-policy and transfer evidence.

No constitutional or production invariant follows from this result.

## Preserved adverse result

`MECHANISM_NOT_REPLICATED`

- predictive holdout cells: **5 / 60**;
- transfer-supported cells: **3 / 30**;
- median holdout Pearson `r`: **0.0**;
- median transfer Pearson `r`: **0.0**;
- family/scenario coverage: **not satisfied**;
- policy-transfer coverage: **not satisfied**.

Positive isolated cells remain retained as context-dependent observations and do not override the aggregate gate.

## Merge-gate disposition

- inside authorized envelope: **PASS**;
- protocol predates results: **PASS**;
- exact candidate passes declared tests: **PASS**;
- negative controls pass: **PASS**;
- authority/privacy expansion: **NONE FOUND**;
- incompatible base drift: **NONE FOUND**;
- exact-byte/source verification: **PASS for executable boundary**;
- predeclared evidence-retention contract: **PASS after additive evidence-only repair**;
- negative/mixed result preserved: **PASS**.

**DDC disposition: merge-authorized, subject only to re-reading current base/head immediately before merge and confirming no incompatible drift.**

## Maturity

- Designed / predeclared: **yes**.
- Implemented: **yes**.
- Tested: **yes, declared synthetic boundary**.
- Replicated broadly: **no**.
- Recovery-proven: **no**.
- Real-world validated: **no**.
- Production-authorized: **no**.
