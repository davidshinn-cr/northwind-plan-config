-- 001_plan_tables.sql
-- The published plan catalog. Rows here are written only by plan_config.seed
-- from the JSON under config/plans/; nothing else writes to these tables.

CREATE TABLE IF NOT EXISTS plan (
    plan_id           TEXT PRIMARY KEY,
    plan_name         TEXT        NOT NULL,
    product_line      TEXT        NOT NULL,
    carrier_id        TEXT        NOT NULL,
    plan_year         INTEGER     NOT NULL,
    effective_date    DATE        NOT NULL,
    termination_date  DATE,
    situs_rule        TEXT        NOT NULL
                      CHECK (situs_rule IN ('employer_situs', 'member_residence')),
    min_group_size    INTEGER     NOT NULL CHECK (min_group_size >= 1),
    rate_table_id     TEXT        NOT NULL
);

-- One row per state the plan is published in. Driven directly by
-- availability.states in the plan JSON: a state added there becomes a row here
-- on the next publish, and a state removed disappears.
--
-- guaranteed_issue_amount and form_number are nullable because the publisher
-- writes whatever the plan document carries for that state, including nothing.
CREATE TABLE IF NOT EXISTS plan_state (
    plan_id                  TEXT    NOT NULL REFERENCES plan (plan_id) ON DELETE CASCADE,
    state_code               CHAR(2) NOT NULL,
    guaranteed_issue_amount  INTEGER,
    form_number              TEXT,
    PRIMARY KEY (plan_id, state_code)
);

CREATE INDEX IF NOT EXISTS idx_plan_state_state ON plan_state (state_code);

CREATE TABLE IF NOT EXISTS employer_group (
    group_id        TEXT PRIMARY KEY,
    group_name      TEXT    NOT NULL,
    situs_state     CHAR(2) NOT NULL,
    eligible_lives  INTEGER NOT NULL CHECK (eligible_lives >= 0)
);

CREATE TABLE IF NOT EXISTS group_plan_offering (
    group_id  TEXT NOT NULL REFERENCES employer_group (group_id) ON DELETE CASCADE,
    plan_id   TEXT NOT NULL REFERENCES plan (plan_id) ON DELETE CASCADE,
    PRIMARY KEY (group_id, plan_id)
);
