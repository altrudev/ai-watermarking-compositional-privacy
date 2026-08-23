# DDC Branch Cleanup Record — 2026-08-22

**Repository:** `altrudev/ai-watermarking-compositional-privacy`  
**Authority:** Root Human Authority instruction: `Fix it`  
**Canonical target head used for cleanup:** `9d446fa8f943b7ec29ed8ade133653a5340e45a0`  
**Policy:** `research/BRANCH_CANONICALITY.md`

## Purpose

Close repository-audit finding R3 by removing stale working branches as competing active states while preserving unique/rejected history where it was not already adequately preserved by a merged pull request or canonical commit.

## Preservation copies created

Before moving the corresponding working refs, the following explicit noncanonical archives were created:

- `archive/agent-canonicalize-v0.8-open-set`
- `archive/agent-ddc-full-audit-v0.8-protocol`
- `archive/agent-implement-v0.8-open-set`
- `archive/agent-path-dependence-v0.4`
- `archive/rejected-agent-textual-benchmark-v0.2`

These `archive/` refs are historical evidence only. They may contain incomplete, superseded, rejected, or pre-repair states and must not be treated as current research authority.

The historical v0.8 protocol working branch was not separately archived because its governing protocol commits/files are already retained in canonical history; its working ref was therefore only neutralized after that fact was verified from the repository lineage.

## Working refs moved to canonical head

The following former working refs were moved to `9d446fa8f943b7ec29ed8ade133653a5340e45a0` after their history was preserved by merged PR/canonical history or an explicit `archive/` copy:

- `agent/canonicalize-v0.8-open-set`
- `agent/canonicalize-v0.8-open-set-r2`
- `agent/cross-family-replication-v0.7`
- `agent/ddc-full-audit-v0.8-protocol`
- `agent/implement-v0.7-replication`
- `agent/implement-v0.8-open-set`
- `agent/noncommutativity-v0.6`
- `agent/open-set-false-attribution-v0.8-protocol`
- `agent/path-dependence-v0.4`
- `agent/textual-benchmark-v0.2`
- `audit/ddc-chain-v0.1-v0.5`
- `ddc/governance-hardening-20260822`
- `ddc/licensing-scope-20260822`
- `ddc/repository-audit-20260822`
- `ddc/research-method-attribution-boundary-20260822`
- `ddc/v0.8-lineage-sync-20260822`
- `publication/beyond-model-provenance-v1.0`
- `research/path-dependence-v0.4`
- `research/robustness-v0.5`
- `research/text-unlinkability-lab-v0.2`
- `research/transformation-chain-v0.3`
- `research/unlinkability-lab-v0.1`

The closed-but-unmerged `agent/textual-benchmark-v0.2` state was preserved first as `archive/rejected-agent-textual-benchmark-v0.2` before its former working ref was moved.

## DDC interpretation

This cleanup does not rewrite canonical experiment commits or erase adverse/rejected history. It changes branch references so old working names no longer advertise stale heads as if they were active research states.

> **Archived state != canonical state.**

> **PR history != permission to resume old work.**

> **Working ref cleanup != deletion of canonical evidence.**

## Finding disposition

**R3 — stale/merged working branches: CLOSED for active-state ambiguity.**

The repository still contains explicitly named `archive/` branches by design. Their noncanonical meaning is governed by `research/BRANCH_CANONICALITY.md`.

Host-level branch protection (R1) remains a separate gate and is tracked in issue #18.
