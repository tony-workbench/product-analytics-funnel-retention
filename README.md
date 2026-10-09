# SQL Practice: Service Counts and Device Updates

## Problem

Count failed requests for each service while retaining services with no failures.
This learning exercise shows why joining a service to several matching logs can
produce repeated rows, and how aggregation produces one summary row per service.

Lesson Practice 2 selects the newest or earliest status update for each device.
It makes timestamp and ID tie-breaking explicit, so one device produces one
deterministically selected status rather than an ambiguous aggregate result.

## Data

- Source: synthetic data embedded in [the SQL script](queries/service_failure_counts.sql).
- Scope: 3 services and 5 request logs; failure means `status >= 400` in this exercise.
- Tables: `services(id, name)` and `logs(id, service_id, status)`.
- Limitations: tiny sample, assumed unique service IDs, no real users or traffic.
  Unknown status values do not satisfy the failure filter. Orphan logs and
  duplicate service IDs are not validated or repaired.

Lesson Practice 2 uses separate [synthetic device data](queries/lesson_practice_2.sql):

- Scope: 4 updates for 2 devices, plus small synthetic test fixtures.
- Table: `updates(id, device, ts, state)`; `ts` is an integer ordering value,
  not a real timestamp or timezone-aware event date.
- Assumptions: unique IDs and non-null, comparable values. The schema does not
  enforce those assumptions; invalid types, NULLs, and duplicate IDs are not
  covered by the validated input contract.

## What I Built

A CTE and LEFT JOIN query with GROUP BY and COUNT, plus an explanation and
counterexample for a repeated-row bug. The completed exercise was packaged into
a standalone SQL file and an automated test runner with Codex assistance.
The original query logic is retained. Extra packaging checks are distinguished
from the original three checks in the test file.

Lesson Practice 2 adds newest/earliest ROW_NUMBER queries, a hand trace, and an
explanation of why MAX(ts) does not encode an ID tie-break. The query logic and
four original assertions come from the completed Python/SQLite exercise.
Codex extracted the standalone SQL, organized tests, and added six packaging
QA tests; this packaging is not a claim of additional independent work by Tony.

## Methods

Filter failure logs in a CTE, keep `services` on the left, and group by service
ID and name. Count the matched `failures.service_id`, not `COUNT(*)`, so an
unmatched service gets zero. This implementation aggregates **after** joining;
it does not implement preaggregation.

The device exercise uses a CTE with ROW_NUMBER, partitioned by device.
For the newest row, sort by `ts DESC, id DESC`; for the earliest row, sort by
`ts ASC, id ASC`. The outer SELECT keeps `rn = 1` and orders displayed devices.
Temporary views expose those same queries to the test runner.

## Validation

Run [the tests](tests/test_service_failure_counts.py) with the command below.
The original exercise covers a normal count, a two-match join counterexample,
and a zero-failure service. Packaging QA also checks unique output grain,
source-total reconciliation, a service without logs, and a NULL status.
These checks cover the stated examples, not every possible input.

Lesson Practice 2 has 10 tests: the original newest/earliest sample assertions,
normal timestamp-priority test, and newest-time tie counterexample, plus six
explicitly labeled packaging QA tests. Additional checks cover empty input,
a single update, earliest-time ties, all 120 insertion orders of the five-row
counterexample, output population/grain, and ambiguous maximum-time candidates.
The full repository test command below passes 17 tests, including the existing
7 service-count tests. This is local validation, not a hosted CI result.

## Results

### Service failure counts

| Service | Failure count |
| --- | ---: |
| login | 1 |
| search | 2 |
| profile | 0 |

The direct join returns two `search` rows. The corrected query returns three
service rows and three total failures. This is a local learning result, not a
production metric or business impact claim.

### Lesson Practice 2: device updates

Both sample queries return `a | online` and `b | offline`. The selected record
for a differs: newest chooses ID 3 at ts=12; earliest chooses ID 1 at ts=10.
At the maximum time for a, IDs 2 and 3 have different states; ROW_NUMBER's ID
tie-break selects the required row. The original tie counterexample returns
`a | offline` and `b | online` regardless of its 120 possible insertion orders.
Each query returns 2 rows, matching the 2 distinct source devices.

## Repository Structure

- `queries/service_failure_counts.sql`: sample tables, query, and validation queries.
- `tests/test_service_failure_counts.py`: reproducible checks using SQLite.
- `queries/lesson_practice_2.sql`: device data, newest/earliest queries, trace,
  original test expectations, and validation queries.
- `tests/test_lesson_practice_2.py`: 4 original checks and 6 packaging QA tests.
- `LEARNING_LOG.md`: verified learning evidence and next milestone.

## How to Reproduce

Requires Python 3 with its standard-library `sqlite3` module. No packages,
network access, credentials, or external data are required.
Lesson Practice 2 requires SQLite 3.25.0 or newer for window functions
([SQLite release notes](https://www.sqlite.org/releaselog/3_25_0.html)).
From this project directory:

```sh
python3 -B -m unittest discover -s tests -v
```

The runner executes the SQL file in a fresh in-memory SQLite database for each
test. Optionally, with the SQLite CLI installed, print the result and validation
tables directly:

```sh
sqlite3 :memory: < queries/service_failure_counts.sql
sqlite3 :memory: < queries/lesson_practice_2.sql
```

## Limitations and Next Steps

The parent folder reserves a future product-analytics project name, but this
version contains two small SQL exercises, not a complete analytics product.
ROW_NUMBER is implemented and tested; funnel, cohort, retention, LAG,
preaggregation, production performance, and website publication are not
completed here. The device schema has no PRIMARY KEY or NOT NULL constraints;
invalid inputs and ties on both ts and id are outside this exercise's contract.
A future exercise can compare service-count preaggregation or use LAG to
compare adjacent observations. Neither next step is inferred to be complete.
