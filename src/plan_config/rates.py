"""Resolve premium rates for a plan, state and age band.

Rates live in ``config/rates/<rate_table_id>.json`` and are keyed by state
under ``rates_by_state``. A plan points at exactly one rate table through its
``rate_table_id``.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from plan_config import loader

LOGGER = logging.getLogger(__name__)

CENTS = Decimal("0.01")


def rate_table_for(plan: Dict[str, Any], rate_tables: Optional[Dict[str, Any]] = None):
    """The rate table a plan points at, or ``None`` if it is not published."""
    rate_tables = rate_tables if rate_tables is not None else loader.load_rate_tables()
    return rate_tables.get(plan["rate_table_id"])


def resolve_rate(
    plan: Dict[str, Any],
    state: str,
    age_band: str,
    rate_tables: Optional[Dict[str, Any]] = None,
) -> Decimal:
    """The published rate for one plan, state and age band.

    Falls back to zero when the rate table carries no row for the state or the
    age band, so that a partially published rate table cannot take the pricing
    service down mid-enrolment.
    """
    table = rate_table_for(plan, rate_tables)
    if table is None:
        LOGGER.warning(
            "rate table %s referenced by %s is not published",
            plan["rate_table_id"],
            plan["plan_id"],
        )
        return Decimal("0.00")

    state_rates = table["rates_by_state"].get(state)
    if state_rates is None:
        LOGGER.warning(
            "rate table %s has no rows for state %s", table["rate_table_id"], state
        )
        return Decimal("0.00")

    raw = state_rates.get(age_band)
    if raw is None:
        LOGGER.warning(
            "rate table %s has no %s row for state %s",
            table["rate_table_id"],
            age_band,
            state,
        )
        return Decimal("0.00")

    return Decimal(str(raw)).quantize(CENTS)


def monthly_premium(
    plan: Dict[str, Any],
    state: str,
    age_band: str,
    elected_benefit_amount: int,
    rate_tables: Optional[Dict[str, Any]] = None,
) -> Decimal:
    """Monthly premium for one member's election.

    ``flat_monthly_per_member`` tables price the plan directly;
    ``per_1000_of_benefit_monthly`` tables price per thousand dollars elected.
    """
    table = rate_table_for(plan, rate_tables)
    rate = resolve_rate(plan, state, age_band, rate_tables)

    if table is not None and table["rate_basis"] == "per_1000_of_benefit_monthly":
        units = Decimal(elected_benefit_amount) / Decimal("1000")
        return (rate * units).quantize(CENTS)

    return rate.quantize(CENTS)


def priced_states(plan: Dict[str, Any], rate_tables: Optional[Dict[str, Any]] = None):
    """Every state the plan's rate table actually carries rows for."""
    table = rate_table_for(plan, rate_tables)
    if table is None:
        return []
    return sorted(table["rates_by_state"].keys())
