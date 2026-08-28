"""Decide whether a plan may be offered to a given buyer.

``availability.states`` in a plan file is the gate. Every downstream surface --
the catalog API, the enrollment offer set, the carrier export -- derives from
this list. A state present here is a state in which members can enrol.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from plan_config import loader


def is_state_offered(plan: Dict[str, Any], state: str) -> bool:
    """True when ``state`` appears in the plan's published availability list."""
    return state in plan["availability"]["states"]


def is_channel_offered(plan: Dict[str, Any], channel: str) -> bool:
    """True when the plan is published for this distribution channel."""
    return channel in plan["availability"]["distribution_channels"]


def is_in_force(plan: Dict[str, Any], as_of: date) -> bool:
    """True when ``as_of`` falls inside the plan's effective period."""
    effective = date.fromisoformat(plan["effective_date"])
    if as_of < effective:
        return False
    if plan["termination_date"] is None:
        return True
    return as_of <= date.fromisoformat(plan["termination_date"])


def situs_state_for(plan: Dict[str, Any], group: Dict[str, Any], member_state: str) -> str:
    """The state whose rules govern this sale.

    ``employer_situs`` plans are governed by the employer's state of record;
    ``member_residence`` plans by the member's own state.
    """
    if plan["availability"]["situs_rule"] == "employer_situs":
        return group["situs_state"]
    return member_state


def is_plan_available(
    plan: Dict[str, Any],
    group: Dict[str, Any],
    member_state: str,
    channel: str,
    as_of: date,
) -> bool:
    """Full availability gate for one plan and one prospective buyer."""
    situs = situs_state_for(plan, group, member_state)
    return (
        is_in_force(plan, as_of)
        and is_state_offered(plan, situs)
        and is_channel_offered(plan, channel)
        and group["eligible_lives"] >= plan["availability"]["min_group_size"]
    )


def available_plan_ids(
    group_id: str,
    member_state: str,
    channel: str,
    as_of: date,
    plans: Optional[Dict[str, Any]] = None,
    groups: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Every plan a member of ``group_id`` may be offered, in plan_id order."""
    plans = plans if plans is not None else loader.load_plans()
    groups = groups if groups is not None else loader.load_groups()
    group = groups[group_id]

    return sorted(
        plan_id
        for plan_id in group["offered_plan_ids"]
        if plan_id in plans
        and is_plan_available(plans[plan_id], group, member_state, channel, as_of)
    )


def states_by_plan(plans: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
    """The published availability list for every plan, for reporting."""
    plans = plans if plans is not None else loader.load_plans()
    return {plan_id: loader.offered_states(plan) for plan_id, plan in sorted(plans.items())}
