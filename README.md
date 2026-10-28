# SQLite Practice

Three small SQLite exercises on made-up data:

- **Service failure counts**: use a CTE and LEFT JOIN to keep every service. Result: login=1, search=2, profile=0.
- **Device updates**: use `ROW_NUMBER` with timestamp/ID tie-breaking to select one newest or earliest update per device.
- **Reading changes**: use `LAG` to compare recorded station readings, preserving missing totals and day gaps. Result: 10 rows, 6 columns.

## What you need

- Python 3 with built-in `sqlite3`; SQLite 3.25+ for window functions
- Optional: the `sqlite3` command-line tool, to print query results

## Run the tests

1. Get the code:

   ```sh
   git clone https://github.com/tony-workbench/sqlite-practice.git
   cd sqlite-practice
   ```

2. Run the tests:

   ```sh
   python3 -m unittest discover -s tests -v
   ```

25 tests cover the examples, output grain, ties, NULLs and empty inputs.

## See the query results

```sh
sqlite3 :memory: < queries/service_failure_counts.sql
sqlite3 :memory: < queries/lesson_practice_2.sql
sqlite3 -header -column -nullvalue NULL :memory: < queries/scan_reading_report.sql
```

Reproduce the saved reading-change CSV (normalize CRLF to LF):

```sh
sqlite3 -csv -header -nullvalue NULL :memory: < queries/scan_reading_report.sql | tr -d '\r'
```

The LAG solution began as a Codex-generated example; Tony confirmed his later
practice and revision. Added edge-case tests are Codex packaging QA.
These are small learning fixtures. Counter resets, production data and
performance are outside their scope.

Queries: [queries/](queries/). Tests: [tests/](tests/).
Result: [CSV](outputs/tables/scan_reading_report.csv).
Exercise notes: [LEARNING_LOG.md](LEARNING_LOG.md).
