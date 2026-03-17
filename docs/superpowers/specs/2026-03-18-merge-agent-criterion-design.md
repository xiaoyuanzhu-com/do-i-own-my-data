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

## Updated Grading Rules

Design principle: the new API checks **raise the ceiling but don't lower the floor**. Products without APIs aren't penalized harder than before. But reaching S now requires proper API accessibility.

### Read

| Grade | Rule |
|-------|------|
| S | All 8 checks pass |
| A | bulk-export AND covers-all-types AND api-read AND documented-api |
| B | bulk-export AND (open-format OR api-read) |
| C | bulk-export OR api-read |
| D | Some data access but major friction |
| F | No way to get data out |

### Write

| Grade | Rule |
|-------|------|
| S | All 7 checks pass |
| A | api-write AND documented-api AND (import-from-file OR bulk-upload) |
| B | api-write OR (import-from-file AND import-from-service) |
| C | import-from-file OR import-from-service OR api-write |
| D | Some write path but major friction |
| F | No way to bring data in |

### Understand, Delete, Ownership — Grading Unchanged

## Migration

### Rating Files

For each existing rating file:

1. Copy `documented-api`, `standard-auth`, `no-anti-automation` checks (with evidence and sources) from the `agent_friendly` `by_model` section into both `read` and `write` `by_model` sections
2. Drop `machine-readable-output` and `programmatic-crud` checks (redundant)
3. Remove the `agent_friendly` criterion block entirely
4. Re-evaluate Read and Write grades against the new grading rules
5. Recompute overall scores with the new weights

### Schema and Docs

- `schema/criteria.yaml` — remove `agent_friendly` entry, update weights to Read 30% / Write 15%
- `judges/rules.md` — remove Agent section, update Read and Write with new checks and grading rules, update weights table
- `README.md` — change "6 criteria" to "5 criteria", remove Agent row from table, update criterion descriptions

### Site Code

- `site/src/data/products.ts` — remove `agent_friendly` from types and data loading logic
- UI components displaying criterion badges/columns — reduce from 6 to 5
- Any hardcoded criterion lists or iteration over 6 criteria

### Validation

- `scripts/validate.py` — update expected criteria list, update overall score computation to use new weights, remove agent_friendly from required fields

## Score-to-Grade Mapping — Unchanged

| Overall Grade | Score Range |
|---------------|-------------|
| S | 90–100 |
| A | 75–89 |
| B | 55–74 |
| C | 35–54 |
| D | 15–34 |
| F | 0–14 |
