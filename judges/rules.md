# Evaluation Rules

These rules define how AI judges evaluate products. Each criterion has concrete yes/no
checks. The scoring section maps check results to a final yes/partial/no rating.

Judges must cite publicly available sources for every check. If evidence is insufficient
or ambiguous, mark the check as false and note the gap. Do not speculate.

## Read — Can I read my data?

### Checks

- **bulk-export**: Can the user export all their data in bulk (not record-by-record)?
- **covers-all-types**: Does the export include all data types the product stores?
- **open-format**: Is the exported data in an open/standard format (JSON, CSV, XML, etc.)?
- **api-read**: Can data be read programmatically via a documented API?
- **realtime-read**: Is near-real-time or streaming read access available (webhooks, subscriptions, live sync)?

### Scoring

- **yes**: bulk-export AND covers-all-types AND (open-format OR api-read)
- **partial**: bulk-export OR api-read
- **no**: NOT bulk-export AND NOT api-read

## Write — Can I write my data?

### Checks

- **import-from-file**: Can the user import data from a file (CSV, JSON, etc.)?
- **import-from-service**: Can the user migrate data from another service?
- **api-write**: Can data be written programmatically via a documented API?
- **bulk-upload**: Is bulk upload supported (not just one-by-one)?

### Scoring

- **yes**: api-write AND (import-from-file OR bulk-upload)
- **partial**: import-from-file OR import-from-service OR api-write
- **no**: NOT import-from-file AND NOT import-from-service AND NOT api-write

## Understand — Can I understand my data?

### Checks

- **open-format**: Is the exported data in an open, non-proprietary format?
- **documented-schema**: Is the data schema publicly documented?
- **standard-schema**: Does the data follow an industry-standard schema (not vendor-specific)?
- **human-readable**: Can a technically competent person read and interpret the data without vendor tools?

### Scoring

- **yes**: open-format AND documented-schema AND human-readable
- **partial**: open-format AND human-readable
- **no**: NOT open-format OR NOT human-readable

## Delete — Can I delete my data?

### Checks

- **granular-delete**: Can the user delete individual records or specific data?
- **full-delete**: Can the user delete all their data or their entire account?
- **clear-retention**: Is there a clear, published data retention policy?
- **backup-removal**: Does deletion include removal from backups (or a stated timeline)?

### Scoring

- **yes**: granular-delete AND full-delete AND clear-retention
- **partial**: full-delete OR granular-delete
- **no**: NOT full-delete AND NOT granular-delete

## Ownership — Do they own my data?

Note: this criterion is "bad" when yes — yes means THEY own your data.

### Checks

- **broad-license**: Does the ToS grant the company a broad license to use, sublicense, or distribute user content beyond service operation?
- **ai-training**: Does the company use user data for AI/ML training (without explicit opt-in)?
- **data-selling**: Does the company sell or share user data with third parties for advertising or monetization?
- **ad-targeting**: Is user data used for targeted advertising?

### Scoring

- **yes** (they own it): broad-license AND (ai-training OR data-selling OR ad-targeting)
- **partial**: broad-license OR ai-training
- **no** (you own it): NOT broad-license AND NOT ai-training AND NOT data-selling AND NOT ad-targeting

## Agent-Friendly — Is it agent-friendly?

### Checks

- **documented-api**: Is there a publicly documented API that individuals (not just businesses) can use?
- **standard-auth**: Does the API use standard authentication (OAuth, API keys, tokens)?
- **no-anti-automation**: Are there no CAPTCHAs, rate walls, or anti-bot barriers for API usage?
- **machine-readable-output**: Does the API return machine-readable formats (JSON, XML)?
- **programmatic-crud**: Can all core operations (read, write, delete) be done via API without manual UI steps?

### Scoring

- **yes**: documented-api AND standard-auth AND machine-readable-output AND programmatic-crud
- **partial**: documented-api OR (api exists but with significant friction)
- **no**: NOT documented-api AND no programmatic access
