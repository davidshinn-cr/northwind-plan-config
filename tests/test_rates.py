from decimal import Decimal

import pytest

from plan_config import rates


def test_flat_monthly_rate_is_read_from_the_state_row(plans, rate_tables):
    acc = plans["ACC-2200"]
    assert rates.resolve_rate(acc, "GA", "30-39", rate_tables) == Decimal("8.94")


def test_per_1000_premium_scales_with_the_elected_benefit(plans, rate_tables):
    ci = plans["CI-3000"]
    # Georgia carries a load of 1.00, so the 40-49 rate is 1.54 per $1,000.
    premium = rates.monthly_premium(ci, "GA", "40-49", 20000, rate_tables)
    assert premium == Decimal("30.80")


def test_the_same_election_prices_differently_by_state(plans, rate_tables):
    ci = plans["CI-3000"]
    assert rates.monthly_premium(ci, "TX", "40-49", 20000, rate_tables) > rates.monthly_premium(
        ci, "AL", "40-49", 20000, rate_tables
    )


def test_ci_3000_prices_every_state_it_is_published_in(plans, rate_tables):
    """Regression guard added after the 2025 CI-3000 launch.

    CI-3000 went live in a state whose rate rows had not been loaded and every
    quote for that state came back at zero. Orphaned rate rows are harmless, so
    this only asserts the direction that hurt: published implies priced.
    """
    ci = plans["CI-3000"]
    published = set(ci["availability"]["states"])
    priced = set(rates.priced_states(ci, rate_tables))
    assert published <= priced


@pytest.mark.parametrize("age_band", ["17-17", "100-120"])
def test_an_unknown_age_band_falls_back_to_zero(plans, rate_tables, age_band):
    # Documented behaviour: pricing degrades to zero rather than raising, so a
    # partially published rate table cannot take enrolment down.
    assert rates.resolve_rate(plans["ACC-2200"], "GA", age_band, rate_tables) == Decimal("0.00")
