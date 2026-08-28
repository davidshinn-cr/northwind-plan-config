"""Build the nightly enrolment file the carrier's policy system ingests.

Every exported row must carry the state-filed form number for the sale. The
carrier rejects the whole file if a row has no form number, so an unfiled state
is a hard stop rather than a silent one.
"""

from typing import Any, Dict, List, Optional

from plan_config import loader


class UnfiledFormError(Exception):
    """Raised when a plan has no filed form number for a state it is sold in."""


def form_number_for(plan: Dict[str, Any], state: str) -> str:
    """The state-filed form number printed on the member's certificate."""
    form_number = plan["form_numbers"].get(state)
    if form_number is None:
        raise UnfiledFormError(
            "{} has no filed form number for {}; the carrier will reject the "
            "export file".format(plan["plan_id"], state)
        )
    return form_number


def export_row(plan: Dict[str, Any], state: str, member_id: str, group_id: str) -> Dict[str, Any]:
    """One row of the carrier enrolment file."""
    return {
        "carrier_id": plan["carrier_id"],
        "plan_id": plan["plan_id"],
        "form_number": form_number_for(plan, state),
        "situs_state": state,
        "group_id": group_id,
        "member_id": member_id,
        "effective_date": plan["effective_date"],
    }


def unfiled_states(plans: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
    """States a plan is published in but carries no filed form number for."""
    plans = plans if plans is not None else loader.load_plans()
    gaps = {}
    for plan_id, plan in sorted(plans.items()):
        missing = [
            state
            for state in plan["availability"]["states"]
            if state not in plan["form_numbers"]
        ]
        if missing:
            gaps[plan_id] = missing
    return gaps
