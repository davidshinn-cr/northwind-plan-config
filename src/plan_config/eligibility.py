"""Apply a plan's member-level eligibility rules.

Everything here is driven by the ``eligibility`` block of a plan file. The
guaranteed-issue amount is state-keyed: it is the benefit a member can elect
without underwriting, and it is filed with the state, so it differs by state.
"""

from typing import Any, Dict, List, Optional


class EligibilityResult(object):
    """The outcome of evaluating one member against one plan."""

    def __init__(self, eligible: bool, reasons: Optional[List[str]] = None):
        self.eligible = eligible
        self.reasons = reasons or []

    def __repr__(self):
        return "EligibilityResult(eligible={!r}, reasons={!r})".format(
            self.eligible, self.reasons
        )


def guaranteed_issue_amount(plan: Dict[str, Any], state: str) -> Optional[int]:
    """The no-underwriting benefit ceiling filed for ``state``.

    Returns ``None`` when the plan carries no filed amount for that state.
    """
    return plan["eligibility"]["guaranteed_issue_amount"].get(state)


def evaluate(
    plan: Dict[str, Any],
    state: str,
    hours_per_week: int,
    days_since_hire: int,
    elected_benefit_amount: int,
) -> EligibilityResult:
    """Evaluate one member against one plan's eligibility rules."""
    rules = plan["eligibility"]
    reasons = []

    if hours_per_week < rules["min_hours_per_week"]:
        reasons.append(
            "works {} hours per week; plan requires {}".format(
                hours_per_week, rules["min_hours_per_week"]
            )
        )

    if days_since_hire < rules["waiting_period_days"]:
        reasons.append(
            "{} days since hire; plan waiting period is {} days".format(
                days_since_hire, rules["waiting_period_days"]
            )
        )

    ceiling = guaranteed_issue_amount(plan, state)
    if ceiling is None:
        reasons.append(
            "no guaranteed issue amount is filed for {} on {}".format(state, plan["plan_id"])
        )
    elif elected_benefit_amount > ceiling:
        reasons.append(
            "elected {} exceeds the {} guaranteed issue amount of {}; "
            "medical underwriting is required".format(elected_benefit_amount, state, ceiling)
        )

    return EligibilityResult(eligible=not reasons, reasons=reasons)
