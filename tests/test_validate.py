from plan_config import validate


def test_published_configuration_matches_the_schemas():
    assert validate.validate_all() == []
