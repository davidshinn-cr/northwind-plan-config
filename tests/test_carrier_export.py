import pytest

from plan_config import carrier_export


def test_export_row_carries_the_state_filed_form_number(plans):
    row = carrier_export.export_row(plans["CI-3000"], "TX", "M-100294", "NW-GRP-0088")
    assert row["form_number"] == "C3000-TX-R1"
    assert row["carrier_id"] == "NW-LIFE"


def test_a_state_with_no_filed_form_number_is_rejected(plans):
    with pytest.raises(carrier_export.UnfiledFormError):
        carrier_export.export_row(plans["CI-3000"], "WY", "M-100294", "NW-GRP-0088")


def test_every_published_state_has_a_filed_form_number(plans):
    """Invariant: availability.states must be a subset of form_numbers.

    An unfiled state does not fail quietly -- the carrier rejects the entire
    nightly file, so this is checked for every plan on every build.
    """
    assert carrier_export.unfiled_states(plans) == {}
