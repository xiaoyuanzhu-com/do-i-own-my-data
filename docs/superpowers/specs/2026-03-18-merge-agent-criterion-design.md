# Merge Agent Criterion Into 5 Core Criteria

## Summary

Remove the "Agent-Friendly" criterion as a standalone evaluation dimension. Redistribute its checks into Read and Write, and redistribute its 10% weight between them. The project moves from 6 criteria to 5.

**Motivation:** The Agent criterion evaluates whether data operations can be performed programmatically. This is better modeled as a quality dimension of Read and Write rather than a separate concern. Most Agent checks overlap with existing checks (`api-read`, `api-write`, `open-format`), and the cross-cutting ones (`standard-auth`, `no-anti-automation`, `documented-api`) naturally describe API accessibility for reading and writing data.

## New Criteria Structure

### Weights

| Criterion | Old Weight | New Weight |
|-----------|-----------|-----------|
| Read | 25% | 30% |
| Ownership | 20% | 20% |
| Delete | 20% | 20% |
| Understand | 15% | 15% |
| Write | 10% | 15% |
| ~~Agent~~ | ~~10%~~ | removed |

### Check Redistribution

Agent's 5 checks are handled as follows:

| Agent Check | Destination | Rationale |
|-------------|------------|-----------|
| `documented-api` | Read + Write | Cross-cutting API accessibility; duplicated into both |
| `standard-auth` | Read + Write | Cross-cutting API accessibility; duplicated into both |
| `no-anti-automation` | Read + Write | Cross-cutting API accessibility; duplicated into both |
| `machine-readable-output` | Dropped | Redundant with Understand's `open-format` + `human-readable` |
| `programmatic-crud` | Dropped | Redundant with Read's `api-read` + Write's `api-write` |

### Read — Updated Checks (8 total)

| Check | Source |
|-------|--------|
| `bulk-export` | existing |
| `covers-all-types` | existing |
| `open-format` | existing |
| `api-read` | existing |
| `realtime-read` | existing |
| `documented-api` | from Agent |
| `standard-auth` | from Agent |
| `no-anti-automation` | from Agent |

### Write — Updated Checks (7 total)

| Check | Source |
|-------|--------|
| `import-from-file` | existing |
| `import-from-service` | existing |
| `api-write` | existing |
| `bulk-upload` | existing |
| `documented-api` | from Agent |
| `standard-auth` | from Agent |
| `no-anti-automation` | from Agent |

### Understand, Delete, Ownership — Unchanged

No check changes. Weights unchanged.

### Note on Duplicated Checks

`documented-api`, `standard-auth`, and `no-anti-automation` appear in both Read and Write but are **evaluated independently per criterion**. The same check ID may have different results. For example, Google Photos has a documented write API but deprecated its read API — `documented-api` would be false in Read but true in Write. For products with no API at all, all three checks are simply false.

## Updated Grading Rules

Design principle: the new API checks **raise the ceiling but don't lower the floor**. Products without APIs aren't penalized harder than before. B/C/D/F grades are unchanged from the old rules. Only S and A are affected:

- **S** requires all checks including the new API ones
- **A** keeps its old rule unchanged — the API checks are not required at A

This ensures products like Google Photos (excellent bulk export in open formats, no read API) retain their current A grade.

### Read

| Grade | Rule |
|-------|------|
| S | All 8 checks pass |
| A | bulk-export AND covers-all-types AND (open-format OR api-read) |
| B | bulk-export AND (open-format OR api-read) |
| C | bulk-export OR api-read |
| D | Some data access but major friction |
| F | No way to get data out |

Note: Grade A is identical to the old rule. The 3 new API checks (`documented-api`, `standard-auth`, `no-anti-automation`) only differentiate S from A.

### Write

| Grade | Rule |
|-------|------|
| S | All 7 checks pass |
| A | api-write AND (import-from-file OR bulk-upload) |
| B | api-write OR (import-from-file AND import-from-service) |
| C | import-from-file OR import-from-service OR api-write |
| D | Some write path but major friction |
| F | No way to bring data in |

Note: Grade A is identical to the old rule. The 3 new API checks only differentiate S from A.

### Understand, Delete, Ownership — Grading Unchanged

## Migration

### Ordering

To avoid intermediate validation failures, apply changes in this order: (1) rating files, (2) schema and rules, (3) validation script, (4) site code and README. Alternatively, land everything in a single atomic commit.

### Rating Files

For each existing rating file:

1. Copy `documented-api`, `standard-auth`, `no-anti-automation` checks (with evidence and sources) from the `agent_friendly` `by_model` section into both `read` and `write` `by_model` sections
2. Drop `machine-readable-output` and `programmatic-crud` checks (redundant)
3. Remove the `agent_friendly` criterion block entirely
4. Re-evaluate Read and Write grades against the new grading rules (A and below should be unchanged; verify any existing S grades still pass with 3 additional checks)
5. Recompute overall scores with the new weights

### Schema and Docs

- `schema/criteria.yaml` — remove `agent_friendly` entry, update weights to Read 30% / Write 15%
- `judges/rules.md` — remove Agent section, update Read and Write with new checks and grading rules, update weights table
- `README.md` — change all instances of "6 criteria" to "5 criteria", remove Agent row from table, update criterion descriptions, update contribution instructions

### Site Code

- `site/src/data/products.ts` — verify whether `agent_friendly` is referenced directly or loaded dynamically from schema; update only if needed
- `site/src/pages/index.astro` — remove `agent_friendly` from `criteriaGroups` Control group (leaving `['delete', 'ownership']`), verify grid layout adapts dynamically
- `site/src/pages/about.astro` — change "six criteria" to "five criteria" in meta description and heading, remove Agent from criteria list
- Any other hardcoded criterion lists or iteration over 6 criteria

### Validation

- `scripts/validate.py` — update expected criteria list, remove `"Agent-Friendly": "agent_friendly"` from `HEADER_TO_CRITERION` dict, update overall score computation to use new weights

## Score-to-Grade Mapping — Unchanged

| Overall Grade | Score Range |
|---------------|-------------|
| S | 90–100 |
| A | 75–89 |
| B | 55–74 |
| C | 35–54 |
| D | 15–34 |
| F | 0–14 |
