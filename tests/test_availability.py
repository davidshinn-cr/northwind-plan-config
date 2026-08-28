from datetime import date

from plan_config import availability


def test_group_in_a_published_state_is_offered_the_plan(plans, groups, plan_year_start):
    offered = availability.available_plan_ids(
        "NW-GRP-0088", "TX", "worksite", plan_year_start, plans=plans, groups=groups
    )
    assert "CI-3000" in offered


def test_group_outside_the_published_states_is_not_offered_the_plan(
    plans, groups, plan_year_start
):
    # ACC-2200 is not published in Texas for the 2027 plan year.
    offered = availability.available_plan_ids(
        "NW-GRP-0088", "TX", "worksite", plan_year_start, plans=plans, groups=groups
    )
    assert "ACC-2200" not in offered


def test_employer_situs_plan_follows_the_group_not_the_member(plans, groups, plan_year_start):
    ci = plans["CI-3000"]
    peachtree = groups["NW-GRP-0042"]  # situs GA

    # A member living in a state the plan is not published in still gets it,
    # because CI-3000 is governed by the employer's state of record.
    assert availability.is_plan_available(ci, peachtree, "NC", "worksite", plan_year_start)


def test_member_residence_plan_follows_the_member(plans, groups, plan_year_start):
    hi = plans["HI-1500"]
    peachtree = groups["NW-GRP-0042"]  # situs GA

    assert availability.is_plan_available(hi, peachtree, "GA", "worksite", plan_year_start)
    assert not availability.is_plan_available(hi, peachtree, "NC", "worksite", plan_year_start)


def test_plan_is_not_in_force_before_its_effective_date(plans):
    assert not availability.is_in_force(plans["CI-3000"], date(2026, 12, 31))
    assert availability.is_in_force(plans["CI-3000"], date(2027, 1, 1))


def test_broker_only_channel_is_gated(plans, groups, plan_year_start):
    hi = plans["HI-1500"]
    lone_star = groups["NW-GRP-0088"]

    assert availability.is_plan_available(hi, lone_star, "TX", "worksite", plan_year_start)
    assert not availability.is_plan_available(hi, lone_star, "TX", "broker", plan_year_start)


def test_group_below_minimum_size_is_not_offered_the_plan(plans, groups, plan_year_start):
    hi = plans["HI-1500"]
    small_group = dict(groups["NW-GRP-0088"], eligible_lives=4)

    assert not availability.is_plan_available(
        hi, small_group, "TX", "worksite", plan_year_start
    )
