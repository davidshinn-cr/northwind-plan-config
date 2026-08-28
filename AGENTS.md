# Northwind Plan Configuration — data model brief

This repository is the product database for the Northwind voluntary benefits
platform. The JSON under `config/` is not documentation and it is not seed data
for a test environment. It is production behaviour. A number changed in
`config/plans/` decides which employees are shown which plan, at what price, in
which state.

Configuration is authored by the Product Configuration team from written
business requirements, not by the engineers who own the services that read it.

## What the documents are

### `config/plans/<plan_id>.json`

One published benefit plan. The fields that carry behaviour:

| Field | What it decides |
| --- | --- |
| `availability.states` | The states the plan may be sold in. This is the availability gate. |
| `availability.situs_rule` | Whether the governing state is the employer's or the member's. |
| `availability.distribution_channels` | Which sales channels may offer it. |
| `availability.min_group_size` | The smallest employer group that may be offered it. |
| `effective_date` / `termination_date` | The period the plan is in force. |
| `eligibility.guaranteed_issue_amount` | Per state, the benefit a member may elect without underwriting. Filed with the state. |
| `eligibility.*` (remaining) | Member-level gates: hours, waiting period, dependent age, pre-existing period. |
| `rate_table_id` | Which rate table prices this plan. |
| `form_numbers` | Per state, the filed certificate form number. Printed on the member's certificate and required by the carrier. |
| `riders` | Optional benefits attached to the plan. |

### `config/rates/<rate_table_id>.json`

Premium rates for one plan and plan year, keyed by state and then by age band.
`rate_basis` decides whether the number is a flat monthly premium or a rate per
$1,000 of elected benefit.

### `config/groups/employer-groups.json`

Employer groups, their state of record, and the plans each has been sold.

### `config/riders/riders.json`

Rider definitions, including states in which a rider may not be attached.

## The coupling that matters

A state is not represented in one place. Publishing a plan in a state means the
state code appears in **four** independent maps, three of which are in different
files:

1. `availability.states` — in the plan document
2. `eligibility.guaranteed_issue_amount` — in the plan document
3. `form_numbers` — in the plan document
4. `rates_by_state` — in the referenced rate table file

Nothing in the repository enforces that these four agree. `schemas/` validates
the shape of each document in isolation; JSON Schema cannot express a constraint
that spans two files, and the validator does not attempt it. A state present in
one map and absent from another is a valid document set, and it publishes.

## Where the data goes

```
config/plans/*.json   ──►  plan_config.loader
config/rates/*.json         │
                            ├──►  plan_config.seed        ──►  plan, plan_state, plan_rate
                            │                                       │
                            │                              db/views/v_plan_state_availability.sql
                            │                                       │
                            ├──►  plan_config.availability  ──►  plan_config.catalog_api  GET /plans
                            ├──►  plan_config.eligibility
                            ├──►  plan_config.rates
                            └──►  plan_config.carrier_export  ──►  nightly carrier file
```

`GET /plans` is the only public read path onto this data. The enrolment
experience is a separate service and a separate repository; it consumes that
endpoint and holds its own copy of the response contract.

## How a configuration change is reviewed

A configuration pull request is a behaviour change. Reviewing it means
answering, from the diff:

1. **Which keys moved.** Every state code, plan identifier, rate table
   identifier and date the diff adds, removes or changes — named individually,
   with old and new values. "Updated availability" is not a review.
2. **Whether that matches the requirement.** The linked ticket is the
   specification. A key the ticket does not name has no business in the diff.
3. **What reads it.** Trace from the changed key to the code and SQL that
   consume it, and on to what a member, an employer or the carrier would
   observe differently. Work out which paths those are from the repository
   itself.
4. **Whether the four coupled maps still agree** for every state the diff
   touches, and what happens at run time if they do not. Read the consuming
   code to determine that; do not assume it raises.
5. **Whether the change is priced and filed.** A plan published in a state it
   is not priced or filed for is publishable, schema-valid, and broken.
6. **Whether the effective period is right.** A date applied to the wrong
   period silently rewrites what already-enrolled members were sold.

## Conventions

- Configuration is committed as formatted JSON, two-space indent, one array
  element per line, so that a single state code is a single line in the diff.
- State codes are two-letter uppercase USPS abbreviations.
- `plan_id` and `rate_table_id` must match their file names.
- Rate tables are immutable once a plan year opens. A change to published rates
  is a new table and a new `rate_table_id`, never an edit in place.
