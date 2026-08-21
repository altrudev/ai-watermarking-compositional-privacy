# Reference Results v0.7 — Cross-Family / Cross-Policy Replication

**Status:** Experimental synthetic-only replication/falsification result  
**Protocol commit:** `786ebb3d097d999e15f72cbfce536e59566206a1`  
**Predecessor:** v0.6 pairwise non-commutativity mechanism  
**Reference classification:** `MECHANISM_NOT_REPLICATED`

## Aggregate result

The predeclared v0.7 matrix changed the transform families, adversary policies, population sizes, generation seeds, publication-artifact seeds, calibration/holdout partition, and cross-scenario transfer conditions while preserving the historical scoring semantics.

The exact declared execution produced:

- predictive holdout cells (`r >= 0.70`): **5 / 60**;
- transfer-supported cells (`r >= 0.50`): **3 / 30**;
- median holdout Pearson `r`: **0.0**;
- median transfer Pearson `r`: **0.0**;
- transform-family/scenario coverage: **not satisfied**;
- adversary-policy transfer coverage: **not satisfied**;
- historical scorer parity: **PASS in every scenario**;
- five-policy matrix scorer parity: **PASS in every scenario**;
- commuting negative controls: **PASS**;
- explicit final-text equality for the control: **PASS**;
- explicit final-metadata equality for the control: **PASS**.

Under the thresholds frozen before reference execution, this yields only:

> **`MECHANISM_NOT_REPLICATED`**

The strong v0.6 local mechanism therefore does not generalize across the broader v0.7 matrix.

## Evidence retention

The evidence package retains:

- `holdout-matrix-v0.7.json` — all 60 holdout cells;
- `transfer-matrix-v0.7.json` — all 30 frozen cross-scenario transfer cells;
- `pairwise-diagnostics-v0.7.json.gz.b64` — the complete six-scenario T2 pairwise diagnostic set plus explicit T5 controls, deterministically gzip-compressed (`mtime=0`) and base64 encoded for compact repository retention.

Decoded diagnostics JSON SHA-256:

`0d0fe799220f999780ce0fa01501561121b6e01ee8d56d4b3aeb57de5e7cfe29`

Deterministic gzip SHA-256:

`b2782e197037be917db976d5dbdae8baa15d50c20606f7dcd5f92f6c5fd57211`

The complete aggregate reference object serialized with sorted compact JSON produced SHA-256:

`1ab3c89b689ab0660203d2b12aded49290039132c576d8a7b61d7f5732be2fff`

That aggregate was reproduced byte-identically in two independent executions during the exact-tree verification gate.

## What replicated

The result is not uniformly zero. Five holdout cells met the v0.7 predictive threshold and three transfer cells met the transfer threshold. In particular, some text-only cells retained strong pairwise-order predictiveness under selected populations/families.

Those positive cells are retained as context-dependent evidence. They do not rescue the aggregate replication claim because the predeclared coverage and count gates were not met.

## What failed to replicate

The principal v0.6 proposition under test was that pairwise transformation non-commutativity could remain broadly predictive of complete-path attribution variation after changing transform family, adversary policy, population and seeds, with some transfer between changed synthetic populations.

That broader proposition was falsified for the declared matrix.

The failure is informative: pairwise-order predictiveness appears sensitive to transform family, scoring policy, population and/or evidence composition. A strong result inside one benchmark must therefore remain local unless it survives independent perturbation and transfer tests.

## Lineage interpretation

v0.7 does **not** invalidate the exact v0.6 result. It changes its maturity and scope.

- v0.6 remains a valid experimental finding for its declared fixed synthetic benchmark.
- v0.7 rejects promotion of that finding into a cross-family or broadly transferable system property.
- the combined lineage supports **context dependence**, not a universal transformation-order law.

This is consistent with the standing rules established in earlier phases:

> **Single benchmark result ≠ robust system property.**

> **Synthetic benchmark mechanism ≠ deployed-provider mechanism.**

> **Replication failure ≠ permission to tune the protocol after observing results.**

## Interpretation boundary

This result does not establish anonymity, real-person attribution capability, deployed watermark behavior, provider-log linkage, or a universal privacy law.

It supports only this bounded conclusion:

> The v0.6 pairwise non-commutativity mechanism did not replicate broadly across the predeclared v0.7 cross-family, cross-policy, multi-population matrix, although isolated context-dependent predictive cells remained.

Negative and mixed cells are part of the result and must not be omitted from later summaries.
