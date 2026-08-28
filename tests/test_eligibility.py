from plan_config import eligibility


def test_member_meeting_every_rule_is_eligible(plans):
    result = eligibility.evaluate(
        plans["CI-3000"],
        state="TX",
        hours_per_week=40,
        days_since_hire=90,
        elected_benefit_amount=30000,
    )
    assert result.eligible
    assert result.reasons == []


def test_part_time_member_is_not_eligible(plans):
    result = eligibility.evaluate(
        plans["CI-3000"],
        state="TX",
        hours_per_week=12,
        days_since_hire=90,
        elected_benefit_amount=10000,
    )
    assert not result.eligible
    assert "works 12 hours per week" in result.reasons[0]


def test_member_inside_the_waiting_period_is_not_eligible(plans):
    result = eligibility.evaluate(
        plans["CI-3000"],
        state="TX",
        hours_per_week=40,
        days_since_hire=10,
        elected_benefit_amount=10000,
    )
    assert not result.eligible
    assert "waiting period" in result.reasons[0]


def test_election_above_the_state_guaranteed_issue_amount_requires_underwriting(plans):
    ci = plans["CI-3000"]

    # Texas carries a higher filed guaranteed issue amount than Georgia, so the
    # same election clears in one state and not the other.
    assert eligibility.evaluate(ci, "TX", 40, 90, 30000).eligible
    assert not eligibility.evaluate(ci, "GA", 40, 90, 30000).eligible


def test_state_with_no_filed_guaranteed_issue_amount_blocks_the_election(plans):
    result = eligibility.evaluate(plans["CI-3000"], "WY", 40, 90, 5000)
    assert not result.eligible
    assert "no guaranteed issue amount is filed for WY" in result.reasons[0]
