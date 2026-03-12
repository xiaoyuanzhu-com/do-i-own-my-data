import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";

export interface Criteria {
  rating: "yes" | "partial" | "no";
  notes: string;
}

export type LogoConfig =
  | { source: "thesvg"; slug: string; variant?: string }
  | { source: "url"; url: string }
  | { source: "local"; file: string };

export interface Product {
  slug: string;
  name: string;
  website: string;
  description: string;
  vendor: string;
  tags: string[];
  logoUrl: string | null;
  criteria: Record<string, Criteria>;
  links: { label: string; url: string }[];
  date?: string;
  reviewer?: string;
}

export interface RatingSummary {
  yes: number;
  partial: number;
  no: number;
  rated: number;
  total: number;
}

// Astro runs with cwd set to the site/ directory.
// The data files (registry/, ratings/, schema/) live one level up.
const DATA_DIR = path.resolve(process.cwd(), "..");

function resolveLogoUrl(logo: unknown): string | null {
  if (!logo || typeof logo !== "object") return null;
  const cfg = logo as Record<string, string>;
  switch (cfg.source) {
    case "thesvg":
      return `https://thesvg.org/icons/${cfg.slug}/${cfg.variant || "default"}.svg`;
    case "url":
      return cfg.url || null;
    case "local":
      return cfg.file ? `/${cfg.file}` : null;
    default:
      return null;
  }
}

export function loadProducts(): Product[] {
  const registryDir = path.join(DATA_DIR, "registry");
  const ratingsDir = path.join(DATA_DIR, "ratings");

  const files = fs.readdirSync(registryDir).filter((f) => f.endsWith(".yaml"));

  return files.map((file) => {
    const slug = file.replace(".yaml", "");
    const registry = yaml.load(
      fs.readFileSync(path.join(registryDir, file), "utf-8")
    ) as Record<string, unknown>;

    const ratingPath = path.join(ratingsDir, file);
    let rating: Record<string, unknown> = {};
    if (fs.existsSync(ratingPath)) {
      rating = yaml.load(
        fs.readFileSync(ratingPath, "utf-8")
      ) as Record<string, unknown>;
    }

    return {
      slug,
      name: registry.name as string,
      website: registry.website as string,
      description: registry.description as string,
      vendor: registry.vendor as string,
      tags: (registry.tags as string[]) || [],
      logoUrl: resolveLogoUrl(registry.logo),
      criteria: (rating.criteria as Record<string, Criteria>) || {},
      links: (rating.links as { label: string; url: string }[]) || [],
      date: rating.date as string | undefined,
      reviewer: rating.reviewer as string | undefined,
    };
  }).sort((a, b) => a.name.localeCompare(b.name));
}

export function loadCriteriaSchema() {
  const schemaPath = path.join(DATA_DIR, "schema", "criteria.yaml");
  const schema = yaml.load(
    fs.readFileSync(schemaPath, "utf-8")
  ) as {
    criteria: {
      id: string;
      name: string;
      question: string;
      note: string;
      values: Record<string, string>;
    }[];
  };
  return schema.criteria;
}

export function summarizeCriteria(
  product: Product,
  criteriaIds: string[]
): RatingSummary {
  const summary: RatingSummary = {
    yes: 0,
    partial: 0,
    no: 0,
    rated: 0,
    total: criteriaIds.length,
  };

  for (const id of criteriaIds) {
    const rating = product.criteria[id]?.rating;
    if (!rating) continue;
    summary[rating] += 1;
    summary.rated += 1;
  }

  return summary;
}
