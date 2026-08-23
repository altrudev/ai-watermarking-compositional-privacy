# v0.8 Evidence Custody and Recovery

**Status:** evidence-custody record  
**Scope:** synthetic-only  
**Canonical v0.8 experiment:** `7cbb6d8b3e76fdd7a3bbce6db92d34442d025c5e`

## Canonical identities

Complete reference object:

- bytes: `223416`
- SHA-256: `8e0d60322528d44eccf42801caaf5af24e48848d6b75e875b23a59f0a9feca43`
- independent executions: `2`
- byte-identical: `true`

Complete evidence bundle:

- filename: `AI-Watermarking-v0.8-Open-Set-Evidence-Bundle.zip`
- bytes: `1837642`
- SHA-256: `baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

Raw deterministic scenario archives:

| Scenario | Records | Gzip bytes | SHA-256 |
|---|---:|---:|---|
| S1 | 10,368 | 320,558 | `d5ade57c0db81e02f4c6830428fd953f3e322434034e30ed7c993957835b45e5` |
| S2 | 13,824 | 452,195 | `229940087f273bf75e1c880b77798b0dd6be010eb56610fa436ef4983d9717c8` |
| S3 | 20,736 | 682,288 | `94557ab84c117f01a252dbee649b679e36058e4c45ead37c74f494804d45f141` |

Total raw artifact-level records: **44,928**.

The machine-readable canonical manifest remains `research/RAW_EVIDENCE-v0.8.json`.

## Current custody

At this repository state the complete bundle is retained outside Git history in connected Adobe Creative Cloud asset storage and is cryptographically anchored by the hashes above and the canonical manifest.

The connected GitHub interface available during the v0.8 transition did not expose a binary release-asset or arbitrary local-file upload operation. Therefore the repository must not imply that the ZIP bytes are present in Git when they are not.

**Checksum in Git != artifact bytes in Git.**

## Recovery procedure

For any recovered copy of the evidence bundle:

```bash
sha256sum AI-Watermarking-v0.8-Open-Set-Evidence-Bundle.zip
```

The result must equal:

`baede290c793bc621a8a826449d1fc62bf372e26ac813612d05ac5041eba50fb`

After extraction, each raw gzip archive must match its scenario hash above. A mismatch means the recovered artifact is not the canonical v0.8 evidence package.

## Durability requirement

Long-term evidence custody is not considered fully closed until at least one additional durable repository/archive stores the actual bundle bytes or the complete reconstructable raw archives independently of the current Adobe asset.

Preferred future destinations are an immutable research-data archive or a GitHub release asset when an authenticated binary-upload path is available. The archive destination must preserve the exact existing bytes; re-exporting or recompressing the data creates a different artifact and requires a new checksum record.

## Boundary

The evidence is synthetic experiment evidence only. Retention, publication, mirroring, or checksum verification does not create real-person attribution authority, provider access authority, or evidence about a deployed watermark implementation.
