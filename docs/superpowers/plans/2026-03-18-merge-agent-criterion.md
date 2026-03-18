# Merge Agent Criterion Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the Agent-Friendly criterion, redistribute its checks into Read and Write, and update all schema, ratings, site code, and docs accordingly.

**Architecture:** Pure data migration + config changes. No new files created. The Agent criterion's 3 cross-cutting checks (`documented-api`, `standard-auth`, `no-anti-automation`) are copied into Read and Write for each rating. 2 redundant checks are dropped. Weights shift from 6-way to 5-way split.

**Tech Stack:** YAML (schema, ratings), Markdown (rules, README), Python (validation), TypeScript/Astro (site), CSS

**Spec:** `docs/superpowers/specs/2026-03-18-merge-agent-criterion-design.md`

---

## Migration Impact

Pre-computed grade and score changes for all 5 products. No grade changes occur — only scores shift due to weight redistribution.

| Product | Old Score | Old Grade | New Score | New Grade | Read | Write |
|---------|-----------|-----------|-----------|-----------|------|-------|
| apple-health | 69 | B | 71 | B | B→B | B→B |
| garmin | 62 | B | 65 | B | B→B | C→C |
| google-photos | 77 | A | 80 | A | A→A | S→S |
| telegram | 93 | S | 93 | S | S→S | S→S |
| wechat | 22 | D | 24 | D | C→C | F→F |

Key verification: Telegram Read S and Google Photos Write S survive because all 3 new API checks pass for those products.

---

## File Map

**Modify:**
- `schema/criteria.yaml` — remove `agent_friendly`, update weights
- `judges/rules.md` — remove Agent section, update Read/Write checks+grading, update weights table
- `ratings/apple-health.yaml` — migrate checks, update score
- `ratings/garmin.yaml` — migrate checks, update score
- `ratings/google-photos.yaml` — migrate checks, update score
- `ratings/telegram.yaml` — migrate checks, update score
- `ratings/wechat.yaml` — migrate checks, update score
- `scripts/validate.py` — remove Agent-Friendly from HEADER_TO_CRITERION
- `site/src/pages/index.astro` — remove `agent_friendly` from criteriaGroups
- `site/src/pages/about.astro` — "six" → "five"
- `site/src/styles/global.css` — grid columns `repeat(7, ...)` → `repeat(6, ...)`
- `README.md` — 6→5 criteria, remove Agent row

---

## Task 1: Update Schema

**Files:**
- Modify: `schema/criteria.yaml`

- [ ] **Step 1: Remove agent_friendly criterion and update weights**

Remove the `agent_friendly` entry from the `criteria` list. Update `overall.weights`:

```yaml
overall:
  weights:
    read: 0.30
    ownership: 0.20
    delete: 0.20
    understand: 0.15
    write: 0.15
```

Remove:
```yaml
  - id: agent_friendly
    name: Agent
    question: Is it agent-friendly?
    note: >
      Can an AI agent perform all of the above (read, write, understand, delete)
      ...
```

And remove from weights:
```yaml
    agent_friendly: 0.10
```

- [ ] **Step 2: Commit**

```bash
git add schema/criteria.yaml
git commit -m "schema: remove agent_friendly criterion, update weights to 5-way split"
```

---

## Task 2: Update Grading Rules

**Files:**
- Modify: `judges/rules.md`

- [ ] **Step 1: Update weights table**

Change the Weights table to:

```markdown
| Criterion | Weight |
|-----------|--------|
| Read | 30% |
| Ownership | 20% |
| Delete | 20% |
| Understand | 15% |
| Write | 15% |
```

- [ ] **Step 2: Update Read checks and grading**

Replace the Read `### Checks` section with:

```markdown
### Checks

- **bulk-export**: Can the user export all their data in bulk (not record-by-record)?
- **covers-all-types**: Does the export include all data types the product stores?
- **open-format**: Is the exported data in an open/standard format (JSON, CSV, XML, etc.)?
- **api-read**: Can data be read programmatically via a documented API?
- **realtime-read**: Is near-real-time or streaming read access available (webhooks, subscriptions, live sync)?
- **documented-api**: Is there a publicly documented API for reading data that individuals (not just businesses) can use?
- **standard-auth**: Does the API use standard authentication (OAuth, API keys, tokens)?
- **no-anti-automation**: Are there no CAPTCHAs, rate walls, or anti-bot barriers for API usage?
```

Replace the Read `### Grading` section with:

```markdown
### Grading

- **S**: All 8 checks pass
- **A**: bulk-export AND covers-all-types AND (open-format OR api-read)
- **B**: bulk-export AND (open-format OR api-read)
- **C**: bulk-export OR api-read
- **D**: Some data access exists but with major friction (e.g., record-by-record download, screenshot-only, copy-paste)
- **F**: No way to get data out
```

- [ ] **Step 3: Update Write checks and grading**

Replace the Write `### Checks` section with:

```markdown
### Checks

- **import-from-file**: Can the user import data from a file (CSV, JSON, etc.)?
- **import-from-service**: Can the user migrate data from another service?
- **api-write**: Can data be written programmatically via a documented API?
- **bulk-upload**: Is bulk upload supported (not just one-by-one)?
- **documented-api**: Is there a publicly documented API for writing data that individuals (not just businesses) can use?
- **standard-auth**: Does the API use standard authentication (OAuth, API keys, tokens)?
- **no-anti-automation**: Are there no CAPTCHAs, rate walls, or anti-bot barriers for API usage?
```

Replace the Write `### Grading` section with:

```markdown
### Grading

- **S**: All 7 checks pass
- **A**: api-write AND (import-from-file OR bulk-upload)
- **B**: api-write OR (import-from-file AND import-from-service)
- **C**: import-from-file OR import-from-service OR api-write
- **D**: Some write path exists but with major friction (e.g., manual data entry only, no import)
- **F**: No way to bring data in from outside the product
```

- [ ] **Step 4: Remove entire Agent-Friendly section**

Delete the entire `## Agent-Friendly — Is it agent-friendly?` section including its Checks and Grading subsections (lines 156-173 of `judges/rules.md`).

- [ ] **Step 5: Commit**

```bash
git add judges/rules.md
git commit -m "rules: merge Agent checks into Read/Write, remove Agent section"
```

---

## Task 3: Migrate Rating Files

For each of the 5 rating files, perform the same operation: copy 3 checks from `agent_friendly` into `read` and `write`, remove `agent_friendly` block, update overall score. The checks to copy are `documented-api`, `standard-auth`, `no-anti-automation` (with their evidence and sources). Drop `machine-readable-output` and `programmatic-crud`.

**Files:**
- Modify: `ratings/telegram.yaml`
- Modify: `ratings/google-photos.yaml`
- Modify: `ratings/apple-health.yaml`
- Modify: `ratings/garmin.yaml`
- Modify: `ratings/wechat.yaml`

- [ ] **Step 1: Migrate telegram.yaml**

Copy the 3 checks from `agent_friendly.by_model.claude-sonnet-4-20250514.checks` (documented-api, standard-auth, no-anti-automation) and append them to both `read.by_model.claude-sonnet-4-20250514.checks` and `write.by_model.claude-sonnet-4-20250514.checks`.

Remove entire `agent_friendly:` block (lines 134-160).

Update overall score: `score: 93` (unchanged).

- [ ] **Step 2: Migrate google-photos.yaml**

Same pattern. Copy 3 Agent checks into read and write `by_model` checks.

Remove entire `agent_friendly:` block (lines 134-160).

Update overall: `score: 80` (was 77).

- [ ] **Step 3: Migrate apple-health.yaml**

Same pattern.

Remove entire `agent_friendly:` block (lines 134-160).

Update overall: `score: 71` (was 69).

- [ ] **Step 4: Migrate garmin.yaml**

Same pattern.

Remove entire `agent_friendly:` block (lines 133-159).

Update overall: `score: 65` (was 62).

- [ ] **Step 5: Migrate wechat.yaml**

Same pattern.

Remove entire `agent_friendly:` block (lines 128-153).

Update overall: `score: 24` (was 22).

- [ ] **Step 6: Commit**

```bash
git add ratings/
git commit -m "ratings: migrate Agent checks into Read/Write for all 5 products"
```

---

## Task 4: Update Validation Script

**Files:**
- Modify: `scripts/validate.py`

- [ ] **Step 1: Remove Agent-Friendly from HEADER_TO_CRITERION**

In `scripts/validate.py` line 17, remove:
```python
    "Agent-Friendly": "agent_friendly",
```

- [ ] **Step 2: Run validation**

```bash
python3 scripts/validate.py
```

Expected: `All valid. 5 products in registry, 5 rated.`

- [ ] **Step 3: Commit**

```bash
git add scripts/validate.py
git commit -m "validate: remove Agent-Friendly from criterion header mapping"
```

---

## Task 5: Update Site — Index Page

**Files:**
- Modify: `site/src/pages/index.astro`

- [ ] **Step 1: Remove agent_friendly from criteriaGroups**

On line 16, change:
```typescript
  { title: 'Control', ids: ['delete', 'ownership', 'agent_friendly'] },
```
to:
```typescript
  { title: 'Control', ids: ['delete', 'ownership'] },
```

- [ ] **Step 2: Commit**

```bash
git add site/src/pages/index.astro
git commit -m "site: remove agent_friendly from criteriaGroups on index page"
```

---

## Task 6: Update Site — About Page

**Files:**
- Modify: `site/src/pages/about.astro`

- [ ] **Step 1: Update meta description**

On line 10, change `six criteria` to `five criteria`:
```html
description="About the Do I Own My Data? project and the five criteria used to rate products for data ownership and portability."
```

- [ ] **Step 2: Update heading**

On line 35, change:
```html
<h2 class="section-title">The six criteria</h2>
```
to:
```html
<h2 class="section-title">The five criteria</h2>
```

- [ ] **Step 3: Commit**

```bash
git add site/src/pages/about.astro
git commit -m "site: update about page — six criteria to five"
```

---

## Task 7: Update Site — CSS Grid

**Files:**
- Modify: `site/src/styles/global.css`

- [ ] **Step 1: Update comparison-head grid columns**

On line 620, change:
```css
  grid-template-columns: minmax(0, 1.95fr) repeat(7, minmax(72px, 0.7fr)) 2rem;
```
to:
```css
  grid-template-columns: minmax(0, 1.95fr) repeat(6, minmax(72px, 0.7fr)) 2rem;
```

(7 was: Overall + 6 criteria. 6 is: Overall + 5 criteria.)

- [ ] **Step 2: Update comparison-row grid columns**

On line 658, change:
```css
  grid-template-columns: minmax(0, 1.95fr) repeat(7, minmax(72px, 0.7fr)) 2rem;
```
to:
```css
  grid-template-columns: minmax(0, 1.95fr) repeat(6, minmax(72px, 0.7fr)) 2rem;
```

- [ ] **Step 3: Commit**

```bash
git add site/src/styles/global.css
git commit -m "site: update grid columns from 7 to 6 (removed Agent criterion)"
```

---

## Task 8: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update criterion count and table**

On line 7, change `six concrete criteria` to `five concrete criteria`.

On line 11, change `## The 6 criteria` to `## The 5 criteria`.

Remove the Agent row from the criteria table (line 19):
```markdown
| **Agent** | Is it agent-friendly? |
```

Remove the Agent description block (lines 32-33):
```markdown
> **Agent** — can an AI agent do all the above programmatically, without manual steps?
```

On line 41, change `rating each of the 6 criteria` to `rating each of the 5 criteria`.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README — 6 criteria to 5, remove Agent"
```

---

## Task 9: Verify Everything

- [ ] **Step 1: Run validation script**

```bash
python3 scripts/validate.py
```

Expected: `All valid. 5 products in registry, 5 rated.`

- [ ] **Step 2: Build the site**

```bash
cd site && npm run build
```

Expected: Clean build with no errors.

- [ ] **Step 3: Visual check**

```bash
cd site && npm run dev
```

Open `http://localhost:4321` and verify:
- Index page shows 5 criterion columns (not 6)
- About page says "five criteria" and shows 5 cards
- Product detail pages show 5 criteria sections
- All badges and grades display correctly
