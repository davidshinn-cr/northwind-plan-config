import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from plan_config import loader  # noqa: E402


@pytest.fixture(scope="session")
def plans():
    return loader.load_plans()


@pytest.fixture(scope="session")
def rate_tables():
    return loader.load_rate_tables()


@pytest.fixture(scope="session")
def groups():
    return loader.load_groups()


@pytest.fixture(scope="session")
def plan_year_start():
    return date(2027, 1, 15)
