# Repository Guidelines

## Project Structure & Module Organization
- `registry/` stores one YAML file per product with metadata.
- `ratings/` stores one YAML file per product with the five criteria, notes, and source links.
- `schema/criteria.yaml` defines the canonical criteria IDs and rating meanings.
- `scripts/validate.py` validates YAML structure and slug alignment; Python dependencies live in `scripts/requirements.txt`.
- `site/` contains the Astro site. Main app code lives in `site/src/`, static assets in `site/public/`, and product loading logic in `site/src/data/products.ts`.
- `docs/plans/` holds design notes and planning documents.

## Build, Test, and Development Commands
- `python3 -m pip install -r scripts/requirements.txt` installs the YAML validation dependency.
- `python3 scripts/validate.py` checks all `registry/` and `ratings/` files against `schema/criteria.yaml`.
- `cd site && npm install` installs the site dependencies. Use Node `>=22.12.0`.
- `cd site && npm run dev` starts the Astro dev server.
- `cd site && npm run build` creates a production build and catches site integration issues.
- `cd site && npm run preview` serves the built site locally.

## Coding Style & Naming Conventions
- Use lowercase, hyphenated filenames for product YAML: `google-photos.yaml`.
- Keep `registry/` and `ratings/` slugs identical when both exist.
- Follow existing style: 2-space indentation in Astro/TypeScript, 4 spaces in Python, and concise, schema-first YAML.
- Prefer clear names such as `loadProducts` or `criteriaSchema`; avoid one-letter identifiers.
- No formatter or linter is currently configured, so match the surrounding file style exactly.

## Testing Guidelines
- There is no dedicated unit test suite yet; validation is the baseline check.
- Run `python3 scripts/validate.py` after editing YAML, schema, or validation logic.
- Run `cd site && npm run build` after changing `site/src/` or shared data-loading behavior.
- For rating entries, include evidence links and verify each criterion includes both `rating` and `notes`.

## Commit & Pull Request Guidelines
- Follow the existing Conventional Commit pattern: `feat: ...`, `fix: ...`, `docs: ...`, with optional scope like `feat(site): ...`.
- Keep commits focused; separate data updates from site or tooling changes when practical.
- PRs should summarize changes, list affected slugs or pages, and note validation/build results.
- Include screenshots for visible site changes and link related issues or source material when relevant.

## Data Quality Notes
- Base ratings on verifiable product behavior, not assumptions.
- When adding or updating a rating, include source links that support the score and notes.
