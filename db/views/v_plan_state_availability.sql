-- v_plan_state_availability
--
-- The catalog's sellability rule, expressed once in SQL so that the enrolment
-- experience, the reporting warehouse and the carrier export all agree on what
-- "available" means for a plan in a state.
--
-- A plan-state row is sellable only when it is in force, has a filed form
-- number, has a filed guaranteed issue amount, and has priced rate rows. The
-- last three come from different parts of the plan document and from a
-- different file, so they can disagree with availability.states.

CREATE OR REPLACE VIEW v_plan_state_availability AS
SELECT
    p.plan_id,
    p.plan_name,
    p.product_line,
    p.plan_year,
    ps.state_code,
    p.effective_date,
    p.termination_date,
    p.situs_rule,
    ps.guaranteed_issue_amount,
    ps.form_number,
    p.rate_table_id,
    COALESCE(r.rate_row_count, 0)                       AS rate_row_count,
    (ps.form_number IS NOT NULL)                        AS is_form_filed,
    (ps.guaranteed_issue_amount IS NOT NULL)            AS is_gi_filed,
    (COALESCE(r.rate_row_count, 0) > 0)                 AS is_priced,
    (
        CURRENT_DATE >= p.effective_date
        AND (p.termination_date IS NULL OR CURRENT_DATE <= p.termination_date)
        AND ps.form_number IS NOT NULL
        AND ps.guaranteed_issue_amount IS NOT NULL
        AND COALESCE(r.rate_row_count, 0) > 0
    )                                                   AS is_sellable
FROM plan AS p
JOIN plan_state AS ps
    ON ps.plan_id = p.plan_id
LEFT JOIN (
    SELECT rate_table_id, state_code, COUNT(*) AS rate_row_count
    FROM plan_rate
    GROUP BY rate_table_id, state_code
) AS r
    ON r.rate_table_id = p.rate_table_id
   AND r.state_code = ps.state_code;

COMMENT ON VIEW v_plan_state_availability IS
    'One row per plan and published state, with the filing and pricing '
    'preconditions that make that plan-state sellable.';
