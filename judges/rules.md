# Evaluation Rules

These rules define how AI judges evaluate products. Each criterion has concrete yes/no
checks. The grading section maps check results to a final S/A/B/C/D/F grade.

All grades are normalized so that higher = better for the user. S is the best possible
grade, F is the worst.

Judges must cite publicly available sources for every check. If evidence is insufficient
or ambiguous, mark the check as false and note the gap. Do not speculate.

## Grade Scale

| Grade | Meaning |
|-------|---------|
| S | Perfect — all checks pass, exemplary data ownership |
| A | Excellent — core capabilities present with minor gaps |
| B | Good — solid baseline, some meaningful limitations |
| C | Mediocre — minimal viable capability, significant gaps |
| D | Poor — technically possible but with major friction |
| F | Fail — no meaningful capability |

## Overall Grade

The overall grade for a product is a weighted average of all criterion grades.

### Grade-to-score mapping

| Grade | Score |
|-------|-------|
| S | 100 |
| A | 80 |
| B | 60 |
| C | 40 |
| D | 20 |
| F | 0 |

### Weights

| Criterion | Weight |
|-----------|--------|
| Read | 30% |
| Ownership | 20% |
| Delete | 20% |
| Understand | 15% |
| Write | 15% |

### Score-to-grade mapping

| Overall Grade | Score Range |
|---------------|-------------|
| S | 90–100 |
| A | 75–89 |
| B | 55–74 |
| C | 35–54 |
| D | 15–34 |
| F | 0–14 |

---

## Read — Can I read my data?

### Checks

- **bulk-export**: Can the user export all their data in bulk (not record-by-record)?
- **covers-all-types**: Does the export include all data types the product stores?
- **open-format**: Is the exported data in an open/standard format (JSON, CSV, XML, etc.)?
- **api-read**: Can data be read programmatically via a documented API?
- **realtime-read**: Is near-real-time or streaming read access available (webhooks, subscriptions, live sync)?
- **documented-api**: Is there a publicly documented API for reading data that individuals (not just businesses) can use?
- **standard-auth**: Does the API use standard authentication (OAuth, API keys, tokens)?
- **no-anti-automation**: Are there no CAPTCHAs, rate walls, or anti-bot barriers for API usage?

### Grading

- **S**: All 8 checks pass
- **A**: bulk-export AND covers-all-types AND (open-format OR api-read)
- **B**: bulk-export AND (open-format OR api-read)
- **C**: bulk-export OR api-read
- **D**: Some data access exists but with major friction (e.g., record-by-record download, screenshot-only, copy-paste)
- **F**: No way to get data out

## Write — Can I write my data?

### Checks

- **import-from-file**: Can the user import data from a file (CSV, JSON, etc.)?
- **import-from-service**: Can the user migrate data from another service?
- **api-write**: Can data be written programmatically via a documented API?
- **bulk-upload**: Is bulk upload supported (not just one-by-one)?
- **documented-api**: Is there a publicly documented API for writing data that individuals (not just businesses) can use?
- **standard-auth**: Does the API use standard authentication (OAuth, API keys, tokens)?
- **no-anti-automation**: Are there no CAPTCHAs, rate walls, or anti-bot barriers for API usage?

### Grading

- **S**: All 7 checks pass
- **A**: api-write AND (import-from-file OR bulk-upload)
- **B**: api-write OR (import-from-file AND import-from-service)
- **C**: import-from-file OR import-from-service OR api-write
- **D**: Some write path exists but with major friction (e.g., manual data entry only, no import)
- **F**: No way to bring data in from outside the product

## Understand — Can I understand my data?

### Checks

- **open-format**: Is the exported data in an open, non-proprietary format?
- **documented-schema**: Is the data schema publicly documented?
- **standard-schema**: Does the data follow an industry-standard schema (not vendor-specific)?
- **human-readable**: Can a technically competent person read and interpret the data without vendor tools?

### Grading

- **S**: All 4 checks pass
- **A**: open-format AND documented-schema AND human-readable
- **B**: open-format AND human-readable
- **C**: open-format OR human-readable
- **D**: Data is technically accessible but requires significant reverse-engineering
- **F**: Proprietary or binary format, effectively unreadable without the original product

## Delete — Can I delete my data?

### Checks

- **granular-delete**: Can the user delete individual records or specific data?
- **full-delete**: Can the user delete all their data or their entire account?
- **clear-retention**: Is there a clear, published data retention policy?
- **backup-removal**: Does deletion include removal from backups (or a stated timeline)?

### Grading

- **S**: All 4 checks pass
- **A**: granular-delete AND full-delete AND clear-retention
- **B**: granular-delete AND full-delete
- **C**: full-delete OR granular-delete
- **D**: Some deletion exists but with major friction (e.g., must contact support, unclear process)
- **F**: No deletion capability, or data persists after account closure

## Ownership — Do I own my data?

Note: All grades are normalized so that higher = better for the user. S means the user
fully owns their data with no exploitation. F means the company fully exploits user data.

### Checks

- **broad-license**: Does the ToS grant the company a broad license to use, sublicense, or distribute user content beyond service operation?
- **ai-training**: Does the company use user data for AI/ML training (without explicit opt-in)?
- **data-selling**: Does the company sell or share user data with third parties for advertising or monetization?
- **ad-targeting**: Is user data used for targeted advertising?

### Grading

- **S**: NOT broad-license AND NOT ai-training AND NOT data-selling AND NOT ad-targeting (user fully owns data, no exploitation)
- **A**: NOT ai-training AND NOT data-selling AND NOT ad-targeting (minor broad-license for service operation only)
- **B**: NOT data-selling AND NOT ad-targeting (some broad license or AI training, but no monetization of user data)
- **C**: broad-license OR ai-training (some exploitation, but not aggressive)
- **D**: broad-license AND (ai-training OR data-selling) (significant exploitation)
- **F**: broad-license AND (ai-training OR data-selling OR ad-targeting) (full exploitation — company treats user data as its own)
