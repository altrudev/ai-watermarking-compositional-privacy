# Branch Canonicality and Research-State Policy

**Status:** normative repository-governance guidance  
**Effective date:** 2026-08-22  
**Canonical branch:** `main`

## Canonicality rule

Only the current `main` branch is an active canonical repository state.

A branch name, commit existence, pull-request head, archived experiment branch, or local checkout does not independently create research authority or canonical status.

> **Branch existence != canonical authority.**

> **Commit existence != current research state.**

> **Merged history != authorization to resume an old branch.**

## Working branches

Active work must occur on a bounded branch created from a recorded canonical `main` commit. Before merge, the branch must be checked for base drift and reviewed against the governing DDC transition.

After a pull request is merged, its working branch should not remain a competing active head. The preferred cleanup order is:

1. retain the merged commit and PR as historical evidence;
2. delete the merged ephemeral working branch when the hosting interface permits safe deletion; or
3. if unique branch history must remain directly addressable, copy it to an `archive/` branch and mark it noncanonical;
4. move or remove the former working branch so it cannot be mistaken for current work.

## Archive branches

Branches under `archive/` are immutable historical/noncanonical references. They may contain superseded, rejected, incomplete, invalid, or pre-repair states.

An archive branch:

- is evidence, not authority;
- must not be used as the base for a new experiment without an explicit governed transition from current `main`;
- must not be described as a current result;
- does not supersede a canonical merge commit or current lineage record.

## Rejected and superseded states

Rejected or abandoned work may be retained under `archive/` when it is useful to understand why a transition failed. Retention does not rehabilitate the state.

**Rejected candidate != validated implementation.**  
**Superseded branch != current protocol.**  
**Intermediate evidence != canonical result.**

## Merge discipline

Without relying on GitHub Actions, repository practice requires:

- pull-request review for changes intended for `main`;
- exact base/head inspection immediately before merge;
- no force-push to `main`;
- no direct rewriting of historical experiment/result files to make later evidence look cleaner;
- result and lineage updates to identify the exact canonical experiment commit;
- adverse evidence to remain retained.

Host-level branch protection should enforce these controls when available. Until host enforcement is enabled, this policy is normative but not a substitute for repository settings.

## Authority boundary

Repository administration does not grant identity-resolution authority, external provider access, real-person research scope, production credentials, or permission to start a new experiment.

**Repository write permission != research authority.**
