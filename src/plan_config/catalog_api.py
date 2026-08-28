"""The plan catalog service.

``GET /plans`` is what the enrolment experience calls to find out which plans a
member may be shown. It is the only public read path onto the published
configuration.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query

from plan_config import availability, eligibility, loader, rates

app = FastAPI(title="Northwind Plan Catalog", version="2027.1.0")


def plan_summary(
    plan: Dict[str, Any],
    state: str,
    rate_tables: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """The shape returned to the enrolment experience for one plan.

    Consumers depend on this contract. ``guaranteed_issue_amount`` and
    ``form_number`` are state-resolved here, not by the caller.
    """
    return {
        "plan_id": plan["plan_id"],
        "plan_name": plan["plan_name"],
        "product_line": plan["product_line"],
        "carrier_id": plan["carrier_id"],
        "plan_year": plan["plan_year"],
        "effective_date": plan["effective_date"],
        "state": state,
        "rate_table_id": plan["rate_table_id"],
        "guaranteed_issue_amount": eligibility.guaranteed_issue_amount(plan, state),
        "form_number": plan["form_numbers"].get(state),
        "riders": plan["riders"],
        "billing_modes": plan["billing_modes"],
        "priced_states": rates.priced_states(plan, rate_tables),
    }


@app.get("/plans")
def list_plans(
    group_id: str = Query(..., description="Employer group requesting the catalog"),
    member_state: str = Query(..., min_length=2, max_length=2),
    channel: str = Query("worksite"),
    as_of: Optional[str] = Query(None, description="ISO date; defaults to today"),
) -> Dict[str, Any]:
    """Every plan this group's members may be offered in ``member_state``."""
    plans = loader.load_plans()
    groups = loader.load_groups()
    rate_tables = loader.load_rate_tables()

    if group_id not in groups:
        raise HTTPException(status_code=404, detail="unknown group {}".format(group_id))

    effective_date = date.fromisoformat(as_of) if as_of else date.today()
    group = groups[group_id]

    plan_ids = availability.available_plan_ids(
        group_id, member_state, channel, effective_date, plans=plans, groups=groups
    )

    summaries: List[Dict[str, Any]] = []
    for plan_id in plan_ids:
        plan = plans[plan_id]
        situs = availability.situs_state_for(plan, group, member_state)
        summaries.append(plan_summary(plan, situs, rate_tables))

    return {
        "group_id": group_id,
        "situs_state": group["situs_state"],
        "member_state": member_state,
        "channel": channel,
        "as_of": effective_date.isoformat(),
        "plans": summaries,
    }


@app.get("/plans/{plan_id}/states")
def plan_states(plan_id: str) -> Dict[str, Any]:
    """The published availability list for one plan."""
    plan = loader.load_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="unknown plan {}".format(plan_id))
    return {
        "plan_id": plan_id,
        "states": plan["availability"]["states"],
        "priced_states": rates.priced_states(plan),
    }


@app.get("/rate-tables/{rate_table_id}")
def rate_table(rate_table_id: str) -> Dict[str, Any]:
    """The published rate table behind a plan's ``rate_table_id``.

    The enrolment experience calls this to price an election. A table that is
    retired or repointed stops resolving here, and the caller sees a 404.
    """
    tables = loader.load_rate_tables()
    if rate_table_id not in tables:
        raise HTTPException(
            status_code=404, detail="unknown rate table {}".format(rate_table_id)
        )
    return tables[rate_table_id]
