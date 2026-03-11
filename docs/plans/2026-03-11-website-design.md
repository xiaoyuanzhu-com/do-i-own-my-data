# Website Design — Do I Own My Data

Date: 2026-03-11

## Goal

Turn the YAML data (registry + ratings) into a public, browsable website so consumers can look up products and see how they score on data ownership.

## Architecture

**Astro static site** — reads YAML data at build time, generates static HTML, deploys to GitHub Pages or Cloudflare Pages.

- Zero JS by default. Only interactive component is client-side search.
- No backend, no database, no MeiliSearch.
- Contributions continue via GitHub PRs on YAML files.

## Pages

| Route | Content |
|-------|---------|
| `/` | All products in a clean table with rating indicators (yes/partial/no) + search bar at top |
| `/products/[name]` | Full rating card — all 6 criteria with notes and source links |
| `/about` | The 6 criteria explained with footnotes, project info |

## Search

Client-side search using Fuse.js (~7KB). At build time, Astro generates a `search-index.json` with product names, vendors, tags, and ratings. The search bar is an Astro island — the only interactive component on the page. Handles thousands of products comfortably (the JSON index would be a few MB at most).

## Data flow

```
registry/*.yaml + ratings/*.yaml
        ↓
  Astro build (content collections)
        ↓
  Static HTML + search-index.json
        ↓
  Deploy to GitHub Pages / Cloudflare Pages
```

## Style

Clean, simple, solid. Minimal CSS — no UI framework. Good typography, readable on mobile. Trustworthy reference-site feel. Colored indicators for yes (green) / partial (yellow) / no (red).

## What this does NOT include (intentionally)

- No server or database
- No MeiliSearch or Algolia
- No user accounts or login
- No UI framework (Tailwind, Bootstrap, etc.)
- No commenting or voting system
