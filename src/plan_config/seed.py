"""Publish the JSON configuration into the plan database.

This is the hand-off point between the file that the Product Configuration team
edits and the tables the rest of the platform reads. The seeder is a full
replace: whatever is in ``config/`` after a merge is what the database holds.
"""

import logging
from typing import Any, Dict, Optional

from plan_config import loader

LOGGER = logging.getLogger(__name__)

UPSERT_PLAN = """
INSERT INTO plan (
    plan_id, plan_name, product_line, carrier_id, plan_year,
    effective_date, termination_date, situs_rule, min_group_size, rate_table_id
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (plan_id) DO UPDATE SET
    plan_name = EXCLUDED.plan_name,
    product_line = EXCLUDED.product_line,
    carrier_id = EXCLUDED.carrier_id,
    plan_year = EXCLUDED.plan_year,
    effective_date = EXCLUDED.effective_date,
    termination_date = EXCLUDED.termination_date,
    situs_rule = EXCLUDED.situs_rule,
    min_group_size = EXCLUDED.min_group_size,
    rate_table_id = EXCLUDED.rate_table_id
"""

DELETE_PLAN_STATE = "DELETE FROM plan_state WHERE plan_id = %s"

INSERT_PLAN_STATE = """
INSERT INTO plan_state (plan_id, state_code, guaranteed_issue_amount, form_number)
VALUES (%s, %s, %s, %s)
"""

DELETE_RATE_ROWS = "DELETE FROM plan_rate WHERE rate_table_id = %s"

INSERT_RATE_ROW = """
INSERT INTO plan_rate (rate_table_id, state_code, age_band, rate_amount)
VALUES (%s, %s, %s, %s)
"""


def seed_plan(cursor, plan: Dict[str, Any]) -> None:
    """Publish one plan and its per-state rows.

    ``plan_state`` is driven by ``availability.states``. The guaranteed issue
    amount and form number for each state are looked up as the row is written,
    so a state published without either lands in the database as NULL.
    """
    cursor.execute(
        UPSERT_PLAN,
        (
            plan["plan_id"],
            plan["plan_name"],
            plan["product_line"],
            plan["carrier_id"],
            plan["plan_year"],
            plan["effective_date"],
            plan["termination_date"],
            plan["availability"]["situs_rule"],
            plan["availability"]["min_group_size"],
            plan["rate_table_id"],
        ),
    )

    cursor.execute(DELETE_PLAN_STATE, (plan["plan_id"],))
    for state_code in plan["availability"]["states"]:
        cursor.execute(
            INSERT_PLAN_STATE,
            (
                plan["plan_id"],
                state_code,
                plan["eligibility"]["guaranteed_issue_amount"].get(state_code),
                plan["form_numbers"].get(state_code),
            ),
        )


def seed_rate_table(cursor, table: Dict[str, Any]) -> None:
    """Publish one rate table as ``plan_rate`` rows."""
    cursor.execute(DELETE_RATE_ROWS, (table["rate_table_id"],))
    for state_code, bands in table["rates_by_state"].items():
        for age_band, rate_amount in bands.items():
            cursor.execute(
                INSERT_RATE_ROW,
                (table["rate_table_id"], state_code, age_band, rate_amount),
            )


def seed_all(
    cursor,
    plans: Optional[Dict[str, Any]] = None,
    rate_tables: Optional[Dict[str, Any]] = None,
) -> None:
    """Publish the whole configuration set in one transaction."""
    plans = plans if plans is not None else loader.load_plans()
    rate_tables = rate_tables if rate_tables is not None else loader.load_rate_tables()

    for table in rate_tables.values():
        seed_rate_table(cursor, table)
    for plan in plans.values():
        seed_plan(cursor, plan)

    LOGGER.info("published %d plans and %d rate tables", len(plans), len(rate_tables))
