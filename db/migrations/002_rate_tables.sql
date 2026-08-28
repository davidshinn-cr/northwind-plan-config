-- 002_rate_tables.sql
-- Premium rates, published from config/rates/<rate_table_id>.json.
-- plan.rate_table_id points at a set of rows here.

CREATE TABLE IF NOT EXISTS plan_rate (
    rate_table_id  TEXT          NOT NULL,
    state_code     CHAR(2)       NOT NULL,
    age_band       TEXT          NOT NULL,
    rate_amount    NUMERIC(10,4) NOT NULL CHECK (rate_amount >= 0),
    PRIMARY KEY (rate_table_id, state_code, age_band)
);

CREATE INDEX IF NOT EXISTS idx_plan_rate_table_state
    ON plan_rate (rate_table_id, state_code);
