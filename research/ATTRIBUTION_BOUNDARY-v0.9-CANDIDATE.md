# Attribution Boundary / Key Architecture — v0.9 Candidate Scope

**Status:** candidate research direction only  
**Implementation authorization:** NO  
**Canonical reference execution authorization:** NO  
**Predecessor constraint:** v0.8 must be completed and closed, or explicitly superseded through a separate governed transition, before v0.9 implementation begins  
**Scope:** synthetic-only

## Why this candidate exists

Public technical discussion after the v0.8 protocol audit exposed two questions not isolated cleanly in the current program:

1. how much attribution value a watermark contributes when stronger or weaker auxiliary evidence already exists;
2. how the privacy properties change when key scope changes while detector behavior may remain similar.

This document records those questions without modifying the frozen v0.8 protocol or promoting them into claims.

## Candidate primary question

> **What is the minimum watermark architecture and minimum auxiliary information required for a non-identifying provenance signal to materially improve attribution?**

Secondary question:

> **Which privacy properties can be independently audited when the watermark secret remains protected?**

## Candidate key-scope matrix

Synthetic future conditions may include:

| Code | Synthetic key scope | Intended analytical role |
|---|---|---|
| K0 | no watermark | baseline |
| K1 | global shared key | provider-wide shared signal |
| K2 | provider/model key | model-family narrowing |
| K3 | rotating epoch key | time-bounded narrowing |
| K4 | cohort/organization key | group-level narrowing |
| K5 | session key | interaction-level narrowing |
| K6 | synthetic account/person key | identity-proximal synthetic condition |
| K7 | layered key structure | combined scope condition |

These are synthetic architectures. Their inclusion would not imply that a real provider uses any of them.

## Candidate evidence conditions

Future testing should isolate the marginal contribution of provenance under at least these evidence states:

- E0 — text only;
- E1 — provenance only;
- E2 — weak public auxiliary evidence only;
- E3 — weak public auxiliary evidence + provenance;
- E4 — strong synthetic service-side evidence only;
- E5 — strong synthetic service-side evidence + provenance.

The primary quantity should be the change caused by adding provenance to an otherwise identical evidence condition, not merely the final combined attribution rate.

## Candidate transparency conditions

A separate auditability study may compare:

- A0 — secret key + opaque architecture;
- A1 — secret key + documented key scope/rotation policy;
- A2 — secret key + verifiable commitments to key/configuration epochs.

The research question is whether an auditor can detect a material architecture transition without learning the underlying secret.

## Required controls before any future execution

A future v0.9 protocol would need to predeclare:

- exact synthetic population and key assignment;
- candidate membership and filtering semantics;
- public-detector output separately from internal architecture state;
- marginal-contribution metrics;
- open-set abstention behavior;
- false-attribution metrics;
- calibration/holdout isolation;
- negative controls for candidate reduction;
- controls preventing key-scope labels from directly leaking truth;
- deterministic replay and exact protocol lineage;
- explicit claim/nonclaim register.

## Standing distinctions

- **Watermark signal != attribution evidence.**
- **Candidate reduction != evidence creation.**
- **Key secrecy != architectural secrecy.**
- **Detector behavior != internal watermark architecture.**
- **Anonymous-by-design != independently demonstrated anonymity.**
- **Detection != Provenance != Attribution != Identity Resolution != Authority.**
- **Correlation != authorization.**
- **Synthetic evidence != deployed-provider evidence.**

## Explicit nonclaims

This candidate does not claim that:

- any deployed provider uses user-specific, session-specific, cohort-specific, rotating, or layered keys;
- any deployed watermark currently identifies a real person;
- a public detector reveals the provider's internal key architecture;
- publishing secret keys is required for transparency;
- a synthetic identity-proximal condition establishes real-user re-identification capability;
- v0.9 has been predeclared, implemented, tested, or execution-authorized.

## DDC transition rule

This file is a research queue item, not a protocol.

The permitted next transition remains the already-authorized v0.8 implementation path. Starting v0.9 implementation before v0.8 closure or explicit governed supersession would break experiment lineage and rules-before-results discipline.
