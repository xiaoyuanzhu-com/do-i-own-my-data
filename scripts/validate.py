#!/usr/bin/env python3
"""Validate registry and rating YAML files against the schema."""

import re
import sys
from pathlib import Path

import yaml

# Mapping from rules.md h2 header first-word to criteria ID
HEADER_TO_CRITERION = {
    "Read": "read",
    "Write": "write",
    "Understand": "understand",
    "Delete": "delete",
    "Ownership": "ownership",
}

VALID_GRADES = {"S", "A", "B", "C", "D", "F"}

GRADE_TO_SCORE = {"S": 100, "A": 80, "B": 60, "C": 40, "D": 20, "F": 0}

# Score range boundaries for overall grade (lower bound inclusive)
SCORE_TO_GRADE = [
    (90, "S"),
    (75, "A"),
    (55, "B"),
    (35, "C"),
    (15, "D"),
    (0, "F"),
]


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_rules(rules_path: Path) -> dict[str, list[str]]:
    """Parse judges/rules.md and return {criterion_id: [check_ids]}."""
    text = rules_path.read_text()
    rules: dict[str, list[str]] = {}
    current_criterion = None
    in_checks = False

    for line in text.splitlines():
        # Match h2 headers like "## Read — Can I read my data?"
        h2 = re.match(r"^## (\S+)", line)
        if h2:
            header_word = h2.group(1)
            current_criterion = HEADER_TO_CRITERION.get(header_word)
            in_checks = False
            if current_criterion:
                rules[current_criterion] = []
            continue

        # Match h3 "### Checks"
        if re.match(r"^### Checks", line):
            in_checks = True
            continue

        # Any other h3 exits the checks section
        if re.match(r"^###\s", line):
            in_checks = False
            continue

        # Match check lines like "- **check-id**: description"
        if in_checks and current_criterion:
            check = re.match(r"^- \*\*(\S+?)\*\*:", line)
            if check:
                rules[current_criterion].append(check.group(1))

    return rules


def score_to_grade(score: float) -> str:
    """Convert a numeric score to a letter grade."""
    for min_score, grade in SCORE_TO_GRADE:
        if score >= min_score:
            return grade
    return "F"


def validate_schema(schema_path: Path) -> list[str]:
    """Load schema and return criteria IDs."""
    schema = load_yaml(schema_path)
    return [c["id"] for c in schema["criteria"]]


def validate_registry(path: Path) -> list[str]:
    """Validate a registry YAML file. Returns list of errors."""
    errors = []
    data = load_yaml(path)
    for field in ("name", "website", "description", "vendor", "tags"):
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")
    if "tags" in data and not isinstance(data["tags"], list):
        errors.append(f"{path}: 'tags' must be a list")
    if "logo" in data and data["logo"] is not None:
        if not isinstance(data["logo"], dict):
            errors.append(f"{path}: 'logo' must be an object")
        elif "container" in data["logo"] and not isinstance(data["logo"]["container"], str):
            errors.append(f"{path}: logo.container must be a string color value")
    return errors


def validate_rating(
    path: Path,
    criteria_ids: list[str],
    rules: dict[str, list[str]] | None = None,
    schema_weights: dict[str, float] | None = None,
) -> list[str]:
    """Validate a rating YAML file. Returns list of errors.

    Supports graded format (grade field) and legacy format (reviewer field).
    """
    errors = []
    data = load_yaml(path)

    # Detect format
    is_graded = "overall" in data and "models" in data
    is_legacy_models = "models" in data and "overall" not in data
    is_legacy_reviewer = "reviewer" in data

    if is_graded:
        for field in ("date", "models", "criteria", "overall"):
            if field not in data:
                errors.append(f"{path}: missing required field '{field}'")

        # Validate overall section
        if "overall" in data:
            overall = data["overall"]
            if "grade" not in overall:
                errors.append(f"{path}: overall missing 'grade'")
            elif overall["grade"] not in VALID_GRADES:
                errors.append(f"{path}: overall invalid grade '{overall['grade']}'")
            if "score" not in overall:
                errors.append(f"{path}: overall missing 'score'")
            elif not isinstance(overall["score"], (int, float)):
                errors.append(f"{path}: overall score must be a number")

            # Verify overall grade matches computed score
            if (
                schema_weights
                and "criteria" in data
                and "grade" in overall
                and "score" in overall
            ):
                computed_score = 0.0
                for cid, weight in schema_weights.items():
                    entry = data["criteria"].get(cid, {})
                    grade = entry.get("grade")
                    if grade and grade in GRADE_TO_SCORE:
                        computed_score += GRADE_TO_SCORE[grade] * weight
                computed_grade = score_to_grade(computed_score)
                if computed_grade != overall["grade"]:
                    errors.append(
                        f"{path}: overall grade '{overall['grade']}' doesn't match "
                        f"computed grade '{computed_grade}' (score {computed_score:.0f})"
                    )

    elif is_legacy_models:
        for field in ("date", "models", "criteria"):
            if field not in data:
                errors.append(f"{path}: missing required field '{field}'")
    elif is_legacy_reviewer:
        for field in ("date", "reviewer", "criteria"):
            if field not in data:
                errors.append(f"{path}: missing required field '{field}'")
    else:
        errors.append(f"{path}: unrecognized format (no 'overall', 'models', or 'reviewer')")

    if "criteria" not in data:
        return errors

    if is_graded:
        models = data.get("models", [])
        model_ids = set(models) if isinstance(models, list) else set()

        for cid in criteria_ids:
            if cid not in data["criteria"]:
                errors.append(f"{path}: missing criteria '{cid}'")
                continue
            entry = data["criteria"][cid]

            # Validate consensus grade
            if "grade" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'grade'")
            elif entry["grade"] not in VALID_GRADES:
                errors.append(
                    f"{path}: criteria '{cid}' invalid grade '{entry['grade']}'"
                )

            # Validate by_model
            if "by_model" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'by_model'")
                continue

            by_model = entry["by_model"]
            for mid in model_ids:
                if mid not in by_model:
                    errors.append(
                        f"{path}: criteria '{cid}' missing model '{mid}' in by_model"
                    )
                    continue
                model_entry = by_model[mid]

                if "grade" not in model_entry:
                    errors.append(
                        f"{path}: criteria '{cid}' model '{mid}' missing 'grade'"
                    )
                elif model_entry["grade"] not in VALID_GRADES:
                    errors.append(
                        f"{path}: criteria '{cid}' model '{mid}' invalid grade "
                        f"'{model_entry['grade']}'"
                    )

                # Validate check IDs against rules
                if "checks" in model_entry and rules and cid in rules:
                    valid_checks = set(rules[cid])
                    found_checks = {
                        c["id"] for c in model_entry["checks"] if "id" in c
                    }
                    for check_id in found_checks:
                        if check_id not in valid_checks:
                            errors.append(
                                f"{path}: criteria '{cid}' model '{mid}' "
                                f"unknown check '{check_id}'"
                            )
                    for check_id in valid_checks:
                        if check_id not in found_checks:
                            errors.append(
                                f"{path}: criteria '{cid}' model '{mid}' "
                                f"missing check '{check_id}'"
                            )

            # Warn about unknown models in by_model
            for mid in by_model:
                if mid not in model_ids:
                    errors.append(
                        f"{path}: criteria '{cid}' unknown model '{mid}' in by_model"
                    )

        # Check for unknown criteria
        for cid in data["criteria"]:
            if cid not in criteria_ids:
                errors.append(f"{path}: unknown criteria '{cid}'")

    elif is_legacy_models:
        # Legacy multi-model format with yes/partial/no values
        valid_ratings = {"yes", "partial", "no"}
        models = data.get("models", [])
        model_ids = set(models) if isinstance(models, list) else set()

        for cid in criteria_ids:
            if cid not in data["criteria"]:
                errors.append(f"{path}: missing criteria '{cid}'")
                continue
            entry = data["criteria"][cid]

            if "value" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'value'")
            elif entry["value"] not in valid_ratings:
                errors.append(
                    f"{path}: criteria '{cid}' invalid value '{entry['value']}'"
                )

            if "by_model" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'by_model'")
                continue

            by_model = entry["by_model"]
            for mid in model_ids:
                if mid not in by_model:
                    errors.append(
                        f"{path}: criteria '{cid}' missing model '{mid}' in by_model"
                    )
                    continue
                model_entry = by_model[mid]

                if "value" not in model_entry:
                    errors.append(
                        f"{path}: criteria '{cid}' model '{mid}' missing 'value'"
                    )
                elif model_entry["value"] not in valid_ratings:
                    errors.append(
                        f"{path}: criteria '{cid}' model '{mid}' invalid value "
                        f"'{model_entry['value']}'"
                    )

                if "checks" in model_entry and rules and cid in rules:
                    valid_checks = set(rules[cid])
                    found_checks = {
                        c["id"] for c in model_entry["checks"] if "id" in c
                    }
                    for check_id in found_checks:
                        if check_id not in valid_checks:
                            errors.append(
                                f"{path}: criteria '{cid}' model '{mid}' "
                                f"unknown check '{check_id}'"
                            )
                    for check_id in valid_checks:
                        if check_id not in found_checks:
                            errors.append(
                                f"{path}: criteria '{cid}' model '{mid}' "
                                f"missing check '{check_id}'"
                            )

            for mid in by_model:
                if mid not in model_ids:
                    errors.append(
                        f"{path}: criteria '{cid}' unknown model '{mid}' in by_model"
                    )

        for cid in data["criteria"]:
            if cid not in criteria_ids:
                errors.append(f"{path}: unknown criteria '{cid}'")

    else:
        # Legacy reviewer format
        valid_ratings = {"yes", "partial", "no"}
        for cid in criteria_ids:
            if cid not in data["criteria"]:
                errors.append(f"{path}: missing criteria '{cid}'")
                continue
            entry = data["criteria"][cid]
            if "rating" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'rating'")
            elif entry["rating"] not in valid_ratings:
                errors.append(
                    f"{path}: criteria '{cid}' invalid rating '{entry['rating']}'"
                )
            if "notes" not in entry:
                errors.append(f"{path}: criteria '{cid}' missing 'notes'")
        for cid in data["criteria"]:
            if cid not in criteria_ids:
                errors.append(f"{path}: unknown criteria '{cid}'")

    return errors


def main() -> int:
    root = Path(__file__).parent.parent
    schema_path = root / "schema" / "criteria.yaml"

    if not schema_path.exists():
        print(f"ERROR: Schema not found at {schema_path}")
        return 1

    criteria_ids = validate_schema(schema_path)
    errors = []
    warnings = []

    # Load weights from schema for overall grade verification
    schema = load_yaml(schema_path)
    schema_weights = None
    if "overall" in schema and "weights" in schema["overall"]:
        schema_weights = schema["overall"]["weights"]

    # Load rules if available
    rules_path = root / "judges" / "rules.md"
    rules = None
    if rules_path.exists():
        rules = parse_rules(rules_path)
    else:
        warnings.append("judges/rules.md not found; skipping check ID validation")

    # Validate registry entries
    registry_ids = set()
    for path in sorted((root / "registry").glob("*.yaml")):
        registry_ids.add(path.stem)
        errors.extend(validate_registry(path))

    # Validate rating entries
    for path in sorted((root / "ratings").glob("*.yaml")):
        errors.extend(validate_rating(path, criteria_ids, rules, schema_weights))
        if path.stem not in registry_ids:
            warnings.append(
                f"{path}: rating exists but no matching registry entry"
            )

    for w in warnings:
        print(f"WARN: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(s) found.")
        return 1

    total = len(registry_ids)
    rated = len(list((root / "ratings").glob("*.yaml")))
    print(f"\nAll valid. {total} products in registry, {rated} rated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
