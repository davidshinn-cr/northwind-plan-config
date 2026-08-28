# northwind-plan-config

The published product database for the Northwind voluntary benefits platform,
and the services that read it.

Northwind is a synthetic reference codebase. The company, the plans, the rates
and the employer groups are invented. It exists to make one thing concrete: a
change to a JSON configuration file is a change to production behaviour, and
reviewing it means tracing what that data reaches.

## What is in here

| Path | What |
| --- | --- |
| `config/plans/` | One document per published benefit plan |
| `config/rates/` | Premium rates by state and age band, one document per rate table |
| `config/groups/` | Employer groups and the plans each has been sold |
| `config/riders/` | Rider definitions and their state exclusions |
| `schemas/` | JSON Schemas the configuration is validated against |
| `src/plan_config/` | Loader, publisher, availability and eligibility rules, pricing, catalog API, carrier export |
| `db/migrations/` | The plan catalog tables |
| `db/views/` | `v_plan_state_availability` — the sellability rule, in SQL |
| `tests/` | Behaviour tests over the published configuration |

`AGENTS.md` is the data model brief: what each field decides, and the coupling
between the four state-keyed maps that a reviewer has to check by hand.

## The path a configuration change takes

```
config/plans/*.json ──► loader ──► seed ──► plan / plan_state / plan_rate
                                                  │
                                    v_plan_state_availability (SQL)
                                                  │
                            availability ──► catalog_api  GET /plans
                                                  │
                                    ═══ service boundary ═══
                                                  │
                                    northwind-enrollment-api
```

`GET /plans` is the only public read path onto this data.
[`northwind-enrollment-api`](https://github.com/davidshinn-cr/northwind-enrollment-api)
is its consumer: it builds the member's offer set, prices elections, and writes
enrolment records.

## Running the checks

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt

# Validate every document against its schema
PYTHONPATH=src .venv/bin/python -m plan_config.validate

# Run the behaviour tests
.venv/bin/python -m pytest
```

Both run on every pull request. Note what the schema pass can and cannot do: it
checks the shape of each document on its own. It cannot check that a state
listed in `availability.states` also has a guaranteed issue amount, a filed form
number, and rate rows, because those live in three other places and one of them
is a different file.

## Serving the catalog locally

```bash
PYTHONPATH=src .venv/bin/uvicorn plan_config.catalog_api:app --reload
curl 'http://localhost:8000/plans?group_id=NW-GRP-0088&member_state=TX&as_of=2027-01-15'
```
