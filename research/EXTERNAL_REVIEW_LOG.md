# External Review Log

**Status:** research-direction provenance  
**Purpose:** record material external criticism that changes the next research question  
**Evidence class:** hypothesis-generating input, not experimental evidence

## 2026-08-22 — LinkedIn discussion on AI text watermarking

### Elton Willis

**Challenge:** If an observer already has strong prompt/output pairs, endpoint telemetry, or other deterministic service-side evidence, the watermark may add little to attribution. The meaningful question is therefore not whether the watermark can participate in attribution, but how much additional evidentiary value it contributes when stronger evidence is present or absent.

**Assumption targeted:** Earlier discussion could be read as giving the watermark too much causal weight in the complete attribution chain.

**Research consequence:** Future work should measure the **marginal contribution** of the provenance signal under multiple evidence conditions rather than reporting only combined attribution performance.

Required comparisons should include, at minimum:

- auxiliary evidence without watermark/provenance;
- watermark/provenance without stronger auxiliary evidence;
- weak auxiliary evidence plus watermark/provenance;
- strong auxiliary evidence plus watermark/provenance;
- strong auxiliary evidence without watermark/provenance.

A watermark that changes attribution only negligibly under strong evidence must not be described as the principal identity signal in that condition.

### Guillaume Meyer

**Challenge:** Privacy properties depend partly on key architecture. Global, model-level, rotating, cohort-level, session-level, user-level, or layered keying designs have different privacy implications. A public detector may also reveal less than the internal key architecture is capable of representing.

**Assumption targeted:** Describing a watermark as anonymous across users is incomplete unless the relevant key scope and architecture are known or independently auditable.

**Research consequence:** Future synthetic work should vary key scope explicitly and separate two questions:

1. what the public detector exposes;
2. what the underlying architecture could distinguish.

The discussion also raised transparency of key changes. The resulting research distinction is:

> **Key secrecy != architectural secrecy.**

The repository does **not** assume that publishing secret keys is always appropriate. A separate auditability question is whether key scope, rotation, and architecture changes can be independently verified while the secret key remains protected.

## Resulting research refinement

The discussion narrows the next question to:

> **What is the minimum watermark architecture and minimum auxiliary information required for a non-identifying provenance signal to materially improve attribution, and which parts of that architecture can be independently audited without exposing the secret key?**

## Explicit nonclaims

This log does not claim that:

- either participant endorses this repository or its conclusions;
- their comments are experimental evidence;
- any deployed provider uses session-specific, user-specific, or layered watermark keys;
- any deployed watermark identifies a real person;
- any public detector exposes hidden user information;
- secret-key publication is required for every transparent watermark design.

The comments are recorded because they materially improved the threat model and experimental questions.
