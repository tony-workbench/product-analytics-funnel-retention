# SQL Practice: Service Counts and Device Updates

Two small SQLite exercises on made-up data:

- **Service failure counts**: count failed requests per service, keeping services with no failures.
- **Device updates**: pick the newest or earliest status for each device with `ROW_NUMBER`.

## What you need

- Python 3 (its built-in `sqlite3` module is enough)
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

## See the query results

```sh
sqlite3 :memory: < queries/service_failure_counts.sql
sqlite3 :memory: < queries/lesson_practice_2.sql
```

Queries: [queries/](queries/). Exercise notes: [LEARNING_LOG.md](LEARNING_LOG.md).
