"""Read the published JSON configuration off disk.

Nothing in this module interprets the data; it only parses and indexes it.
Interpretation lives in :mod:`plan_config.availability`,
:mod:`plan_config.eligibility` and :mod:`plan_config.rates`.
"""

import json
from typing import Any, Dict, List, Optional

from plan_config import paths


def _read_json(path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_plans() -> Dict[str, Dict[str, Any]]:
    """Return every plan in ``config/plans/``, keyed by ``plan_id``."""
    plans = {}
    for plan_file in sorted(paths.PLANS_DIR.glob("*.json")):
        plan = _read_json(plan_file)
        plans[plan["plan_id"]] = plan
    return plans


def load_rate_tables() -> Dict[str, Dict[str, Any]]:
    """Return every rate table in ``config/rates/``, keyed by ``rate_table_id``."""
    tables = {}
    for rate_file in sorted(paths.RATES_DIR.glob("*.json")):
        table = _read_json(rate_file)
        tables[table["rate_table_id"]] = table
    return tables


def load_riders() -> Dict[str, Dict[str, Any]]:
    """Return every rider, keyed by ``rider_id``."""
    return {r["rider_id"]: r for r in _read_json(paths.RIDERS_FILE)["riders"]}


def load_groups() -> Dict[str, Dict[str, Any]]:
    """Return every employer group, keyed by ``group_id``."""
    return {g["group_id"]: g for g in _read_json(paths.GROUPS_FILE)["groups"]}


def load_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """Return a single plan, or ``None`` if it is not published."""
    return load_plans().get(plan_id)


def offered_states(plan: Dict[str, Any]) -> List[str]:
    """The states in which a plan is published for sale."""
    return list(plan["availability"]["states"])
