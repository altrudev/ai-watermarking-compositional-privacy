# Claim Register v0.7 — Cross-Family / Cross-Policy Replication

**Research scope:** synthetic-only  
**Protocol commit:** `786ebb3d097d999e15f72cbfce536e59566206a1`

## Supported experimental claims

### C7-1 — Broad v0.6 mechanism replication is not supported for the declared matrix

**Status:** Supported negative result.  
**Evidence:** 5/60 predictive holdout cells; 3/30 transfer-supported cells; median holdout `r = 0.0`; median transfer `r = 0.0`; required coverage conditions not satisfied.  
**Allowed wording:** The v0.6 pairwise non-commutativity mechanism did not broadly replicate across the predeclared v0.7 transform-family, adversary-policy, population and transfer matrix.

### C7-2 — Context-dependent positive cells remain

**Status:** Supported experimental observation.  
**Evidence:** Five holdout cells met `r >= 0.70`; three transfer cells met `r >= 0.50`.  
**Boundary:** These cells may be described only as local/context-dependent observations. They may not be used to override the aggregate `MECHANISM_NOT_REPLICATED` classification.

### C7-3 — Negative controls and scorer parity held

**Status:** Supported validation claim.  
**Evidence:** historical scorer parity PASS in every scenario; five-policy matrix scorer parity PASS in every scenario; commuting text control PASS; explicit final metadata equality PASS.

### C7-4 — v0.6 remains a bounded predecessor finding, not a robust system property

**Status:** Supported lineage interpretation.  
**Evidence basis:** v0.6 was strongly predictive inside its fixed declared synthetic benchmark; v0.7 failed the independently predeclared broader replication and transfer gates.  
**Allowed wording:** v0.6 remains experimentally valid for its own declared benchmark, while v0.7 blocks promotion of that finding into a cross-family or broadly transferable property.

## Not supported / prohibited claims

The v0.7 evidence does **not** support claims that:

- pairwise transformation order is universally predictive of privacy outcome;
- the v0.6 mechanism transfers reliably across transform families or populations;
- a failed attribution attempt proves anonymity;
- synthetic attribution performance predicts a deployed provider's attribution capability;
- any real person, account, organization, conversation or provider log can be resolved from a watermark;
- watermark detection proves authorship, ownership, authority or complete provenance;
- one successful local transform ordering is a production privacy policy;
- v0.7 authorizes real-world identity-resolution testing.

## Standing distinctions preserved

- Detection ≠ Provenance ≠ Attribution ≠ Authority ≠ Ownership.
- Model attribution ≠ user attribution.
- Component privacy ≠ compositional privacy.
- Privacy transformation ≠ privacy evidence.
- Failed re-identification ≠ proven anonymity.
- Transformation set ≠ transformation history ≠ privacy outcome.
- Single benchmark result ≠ robust system property.
- Experimental result ≠ production authorization.

## Maturity

- Protocol: **Designed / predeclared**.
- Candidate implementation: **Implemented**.
- Exact declared test boundary: **Tested**.
- Replication claim: **Negative / not replicated for declared matrix**.
- Recovery-proven: **No**.
- Production-authorized: **No**.
- Real-world validated: **No**.
