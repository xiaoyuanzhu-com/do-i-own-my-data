# Do I Own My Data?

A community-driven directory that rates products on how friendly they are toward user data ownership.

## What is this?

Many apps and services collect your data but make it hard to access, export, or move it elsewhere. This project evaluates products against six concrete criteria so consumers can make informed choices about where their data lives.

Each product has a **registry entry** (what it is) and a **rating** (how it scores on data ownership). Ratings use a simple scale: **yes**, **partial**, or **no**.

## The 6 criteria

| Criterion | Question |
|-----------|----------|
| **API Access** | Can you programmatically read your data? |
| **Bulk Export** | Can you download all your data at once? |
| **Open Formats** | Is exported data in standard, open formats? |
| **Real-time Access** | Can you access your data as it's created? |
| **Data Deletion** | Can you truly delete your data? |
| **Portability** | Can you actually use your data elsewhere? |

See `schema/criteria.yaml` for the full definitions including what yes/partial/no means for each.

## How to browse

For now, browse the YAML files directly:

- **`registry/`** -- one file per product with name, website, vendor, and tags
- **`ratings/`** -- one file per product with a rating and notes for each criterion, plus source links

Example: `registry/apple-health.yaml` and `ratings/apple-health.yaml`.

## How to contribute

1. **Add a registry entry** -- create `registry/<product-name>.yaml` with fields: `name`, `website`, `description`, `vendor`, `tags`
2. **Add a rating** (optional) -- create `ratings/<product-name>.yaml` with a `criteria` section rating each of the 6 criteria, plus `links` to sources
3. **Submit a PR**

Filename convention: **lowercase-hyphenated** (e.g., `google-photos.yaml`, `apple-health.yaml`).

Look at existing files for the expected format.

## How to validate

Run the validation script to check all registry and rating files against the schema:

```bash
python3 scripts/validate.py
```

## License

This project is licensed under the [MIT License](LICENSE).
