#!/usr/bin/env python3
"""Validate registry and rating YAML files against the schema."""

import sys
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


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
    return errors


def validate_rating(path: Path, criteria_ids: list[str]) -> list[str]:
    """Validate a rating YAML file. Returns list of errors."""
    errors = []
    data = load_yaml(path)
    for field in ("date", "reviewer", "criteria"):
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")
    if "criteria" not in data:
        return errors
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

    # Validate registry entries
    registry_ids = set()
    for path in sorted((root / "registry").glob("*.yaml")):
        registry_ids.add(path.stem)
        errors.extend(validate_registry(path))

    # Validate rating entries
    for path in sorted((root / "ratings").glob("*.yaml")):
        errors.extend(validate_rating(path, criteria_ids))
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
