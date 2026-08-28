"""Repository-relative locations of the published configuration."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = REPO_ROOT / "config"
PLANS_DIR = CONFIG_DIR / "plans"
RATES_DIR = CONFIG_DIR / "rates"
RIDERS_FILE = CONFIG_DIR / "riders" / "riders.json"
GROUPS_FILE = CONFIG_DIR / "groups" / "employer-groups.json"

SCHEMA_DIR = REPO_ROOT / "schemas"
PLAN_SCHEMA = SCHEMA_DIR / "plan.schema.json"
RATE_TABLE_SCHEMA = SCHEMA_DIR / "rate_table.schema.json"
