import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";

export type Grade = "S" | "A" | "B" | "C" | "D" | "F";

export interface Check {
  id: string;
  result: boolean;
  evidence: string;
  source?: string;
}

export interface ModelResult {
  grade: Grade;
  checks: Check[];
}

// Unified display interface
export interface CriteriaDisplay {
  grade: Grade;
  notes?: string;
  by_model?: Record<string, ModelResult>;
}

export type LogoConfig =
  | { source: "thesvg"; slug: string; variant?: string; container?: string }
  | { source: "url"; url: string; container?: string }
  | { source: "local"; file: string; container?: string };

export interface Product {
  slug: string;
  name: string;
  website: string;
  description: string;
  vendor: string;
  tags: string[];
  logoUrl: string | null;
  logoContainer: string | null;
  criteria: Record<string, CriteriaDisplay>;
  overall: { grade: Grade; score: number } | null;
  links: { label: string; url: string }[];
  date?: string;
  reviewer?: string;
  models?: string[];
}

export interface GradeSummary {
  grades: Record<Grade, number>;
  rated: number;
  total: number;
  overall: { grade: Grade; score: number } | null;
}

const GRADE_TO_SCORE: Record<Grade, number> = {
  S: 100,
  A: 80,
  B: 60,
  C: 40,
  D: 20,
  F: 0,
};

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

function resolveLogoContainer(logo: unknown): string | null {
  if (!logo || typeof logo !== "object") return null;
  const cfg = logo as Record<string, unknown>;
  return typeof cfg.container === "string" && cfg.container.trim()
    ? cfg.container.trim()
    : null;
}

// Map legacy yes/partial/no to grades for backward compatibility
function legacyValueToGrade(value: string, criterionId: string): Grade {
  if (criterionId === "ownership") {
    // Ownership was inverted: "no" (you own it) = S, "yes" (they own it) = F
    if (value === "no") return "S";
    if (value === "partial") return "C";
    return "F";
  }
  if (value === "yes") return "A";
  if (value === "partial") return "C";
  return "F";
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

    const rawCriteria = (rating.criteria as Record<string, any>) || {};
    const isGraded = "overall" in rating;
    const isNewFormat = "models" in rating;
    const criteria: Record<string, CriteriaDisplay> = {};

    for (const [key, val] of Object.entries(rawCriteria)) {
      if (isGraded) {
        // New graded format
        criteria[key] = {
          grade: val.grade,
          notes: val.notes,
          by_model: val.by_model,
        };
      } else if (isNewFormat) {
        // Legacy multi-model format (yes/partial/no)
        criteria[key] = {
          grade: legacyValueToGrade(val.value, key),
          notes: val.notes,
          by_model: val.by_model
            ? Object.fromEntries(
                Object.entries(val.by_model).map(([model, result]: [string, any]) => [
                  model,
                  {
                    grade: legacyValueToGrade(result.value, key),
                    checks: result.checks,
                  },
                ])
              )
            : undefined,
        };
      } else {
        // Legacy reviewer format
        criteria[key] = {
          grade: legacyValueToGrade(val.rating, key),
          notes: val.notes,
        };
      }
    }

    const overall = isGraded && rating.overall
      ? (rating.overall as { grade: Grade; score: number })
      : null;

    return {
      slug,
      name: registry.name as string,
      website: registry.website as string,
      description: registry.description as string,
      vendor: registry.vendor as string,
      tags: (registry.tags as string[]) || [],
      logoUrl: resolveLogoUrl(registry.logo),
      logoContainer: resolveLogoContainer(registry.logo),
      criteria,
      overall,
      links: (rating.links as { label: string; url: string }[]) || [],
      date: rating.date as string | undefined,
      reviewer: rating.reviewer as string | undefined,
      models: (rating.models as string[]) || undefined,
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
    }[];
  };
  return schema.criteria;
}

export function summarizeGrades(
  product: Product,
  criteriaIds: string[]
): GradeSummary {
  const grades: Record<Grade, number> = { S: 0, A: 0, B: 0, C: 0, D: 0, F: 0 };
  let rated = 0;

  for (const id of criteriaIds) {
    const grade = product.criteria[id]?.grade;
    if (!grade) continue;
    grades[grade] += 1;
    rated += 1;
  }

  return {
    grades,
    rated,
    total: criteriaIds.length,
    overall: product.overall,
  };
}
