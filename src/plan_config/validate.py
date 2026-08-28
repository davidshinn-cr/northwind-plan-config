"""Validate the published configuration against the JSON Schemas.

Run as ``python -m plan_config.validate``. This is the gate that runs in CI on
every configuration pull request: it parses every file, checks it against its
schema, and confirms the filename matches the identifier inside the document.
"""

import json
import sys
from typing import List

from jsonschema import Draft202012Validator

from plan_config import paths


def _load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _schema_errors(validator, document, label) -> List[str]:
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda e: list(e.path)):
        location = "/".join(str(part) for part in error.path) or "<root>"
        errors.append("{}: {}: {}".format(label, location, error.message))
    return errors


def validate_plans() -> List[str]:
    """Check every plan document against ``schemas/plan.schema.json``."""
    validator = Draft202012Validator(_load(paths.PLAN_SCHEMA))
    errors = []
    for plan_file in sorted(paths.PLANS_DIR.glob("*.json")):
        plan = _load(plan_file)
        errors.extend(_schema_errors(validator, plan, plan_file.name))
        if plan.get("plan_id") != plan_file.stem:
            errors.append(
                "{}: plan_id {!r} does not match the file name".format(
                    plan_file.name, plan.get("plan_id")
                )
            )
    return errors


def validate_rate_tables() -> List[str]:
    """Check every rate table against ``schemas/rate_table.schema.json``."""
    validator = Draft202012Validator(_load(paths.RATE_TABLE_SCHEMA))
    errors = []
    for rate_file in sorted(paths.RATES_DIR.glob("*.json")):
        table = _load(rate_file)
        errors.extend(_schema_errors(validator, table, rate_file.name))
        if table.get("rate_table_id") != rate_file.stem:
            errors.append(
                "{}: rate_table_id {!r} does not match the file name".format(
                    rate_file.name, table.get("rate_table_id")
                )
            )
    return errors


def validate_all() -> List[str]:
    """Every schema error across the published configuration."""
    return validate_plans() + validate_rate_tables()


def main() -> int:
    errors = validate_all()
    plan_count = len(list(paths.PLANS_DIR.glob("*.json")))
    rate_count = len(list(paths.RATES_DIR.glob("*.json")))

    if errors:
        for error in errors:
            print("ERROR {}".format(error), file=sys.stderr)
        print(
            "\n{} schema error(s) across {} plan(s) and {} rate table(s)".format(
                len(errors), plan_count, rate_count
            ),
            file=sys.stderr,
        )
        return 1

    print(
        "OK: {} plan(s) and {} rate table(s) validate against their schemas".format(
            plan_count, rate_count
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
