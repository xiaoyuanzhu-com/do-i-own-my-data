# Flexible Logo System Design

**Date:** 2026-03-11
**Status:** Approved

## Problem

The product registry YAML files have no logo/icon support. The product list and detail pages render plain text only. Adding recognizable brand logos improves scannability and visual appeal.

## Decision

Use [theSVG](https://github.com/GLINCKER/thesvg) (thesvg.org) as the default icon source, with a flexible configuration system that supports multiple sources per product.

## YAML Schema

Add an optional `logo` field to registry files. Three source types are supported:

### theSVG (default source)

```yaml
logo:
  source: thesvg
  slug: apple             # icon slug on thesvg.org
  variant: default        # optional: default | mono | light | dark | wordmark
```

Resolved URL: `https://thesvg.org/icons/{slug}/{variant}.svg`

When `variant` is omitted, defaults to `default`.

### External URL

```yaml
logo:
  source: url
  url: https://example.com/garmin-logo.svg
```

### Local file

```yaml
logo:
  source: local
  file: logos/garmin.svg   # relative to site/public/
```

Resolved URL: `/{file}`

### Fallback (no logo field)

When `logo` is omitted entirely, render a colored circle with the product name's first letter. Background color is deterministic, derived from a hash of the product name.

## Source-Specific Fields

| Source   | Required Fields              | Optional Fields |
|----------|------------------------------|-----------------|
| `thesvg` | `slug`                       | `variant`       |
| `url`    | `url`                        | —               |
| `local`  | `file`                       | —               |

## Image Resolution

In `products.ts`, add a `resolveLogoUrl()` function that converts the logo config into a final image URL string (or `null` for fallback):

- **thesvg** → `https://thesvg.org/icons/{slug}/{variant}.svg`
- **url** → use the `url` value as-is
- **local** → `/{file}`
- **omitted** → `null` (triggers fallback rendering)

## UI Rendering

### New Component: `ProductLogo.astro`

Accepts:
- `product` — the product object (needs `name` and resolved logo URL)
- `size` — number in pixels, defaults to 24

Behavior:
- If logo URL exists: render an `<img>` tag with the resolved URL, sized to `{size}px`
- If no logo URL: render a `<span>` styled as a circle with the product's first letter, background color derived from a hash of the product name

### Product list page (`index.astro`)

- 24px logo inline to the left of the product name link

### Product detail page (`[slug].astro`)

- 48px logo in the page header, to the left of the product title

## Example Registry Files After Change

```yaml
# registry/apple-health.yaml
name: Apple Health
website: https://www.apple.com/health/
description: Health and fitness data aggregator on iOS
vendor: Apple
tags: [health, fitness, wearable, ios]
logo:
  source: thesvg
  slug: apple
```

```yaml
# registry/telegram.yaml
name: Telegram
website: https://telegram.org/
description: Cloud-based messaging with open API and bot platform
vendor: Telegram FZ-LLC
tags: [messaging, social, cloud]
logo:
  source: thesvg
  slug: telegram
```

```yaml
# registry/wechat.yaml
name: WeChat
website: https://www.wechat.com/
description: China's super-app for messaging, payments, and services
vendor: Tencent
tags: [messaging, social, payments, china]
logo:
  source: thesvg
  slug: wechat
```
