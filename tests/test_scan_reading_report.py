"""Checks for recorded-row LAG semantics and output grain."""

import sqlite3
import unittest
from pathlib import Path

SQL_PATH = Path(__file__).resolve().parents[1] / "queries" / "scan_reading_report.sql"
SETUP_SQL, REPORT_SQL = SQL_PATH.read_text().split("-- Report\n", 1)
COLUMNS = [
    "station", "day_no", "previous_day", "previous_total",
    "days_elapsed", "new_scans",
]
EXPECTED = [
    ("lake", 2, None, None, None, None),
    ("lake", 3, 2, 5, 1, 4),
    ("lake", 6, 3, 9, 3, 3),
    ("quay", 1, None, None, None, None),
    ("quay", 2, 1, 8, 1, 0),
    ("quay", 5, 2, 8, 3, 12),
    ("ridge", 1, None, None, None, None),
    ("ridge", 3, 1, 40, 2, 15),
    ("ridge", 4, 3, 55, 1, None),
    ("ridge", 6, 4, None, 2, None),
]


class ScanReadingReportTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript(SETUP_SQL)

    def report(self):
        return self.db.execute(REPORT_SQL).fetchall()

    def replace_input(self, rows):
        self.db.execute("DELETE FROM scan_readings")
        self.db.executemany("INSERT INTO scan_readings VALUES (?, ?, ?)", rows)

    def test_original_output_contract_and_grain(self):
        cursor = self.db.execute(REPORT_SQL)
        rows = cursor.fetchall()
        self.assertEqual([column[0] for column in cursor.description], COLUMNS)
        self.assertEqual(rows, EXPECTED)
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row[:2] for row in rows}), 10)
        self.assertEqual(
            len(rows), self.db.execute("SELECT COUNT(*) FROM scan_readings").fetchone()[0]
        )

    def test_unreadable_previous_row_is_not_skipped(self):
        rows = {row[:2]: row for row in self.report()}
        self.assertEqual(rows[("ridge", 4)], ("ridge", 4, 3, 55, 1, None))
        self.assertEqual(rows[("ridge", 6)], ("ridge", 6, 4, None, 2, None))

    def test_zero_is_distinct_from_unknown(self):
        rows = {row[:2]: row for row in self.report()}
        self.assertEqual(rows[("quay", 2)][-1], 0)
        self.assertIsNone(rows[("ridge", 6)][-1])

    def test_empty_input(self):
        self.replace_input([])
        self.assertEqual(self.report(), [])

    def test_one_reading_has_no_predecessor(self):
        self.replace_input([("solo", 8, 30)])
        self.assertEqual(self.report(), [("solo", 8, None, None, None, None)])

    def test_partitions_and_nonconsecutive_days(self):
        self.replace_input([("a", 7, 16), ("b", 7, 100), ("a", 2, 10)])
        self.assertEqual(self.report(), [
            ("a", 2, None, None, None, None),
            ("a", 7, 2, 10, 5, 6),
            ("b", 7, None, None, None, None),
        ])

    def test_reverse_insertion_order_preserves_output(self):
        rows = self.db.execute(
            "SELECT station, day_no, total FROM scan_readings ORDER BY station, day_no"
        ).fetchall()
        self.replace_input(list(reversed(rows)))
        self.assertEqual(self.report(), EXPECTED)

    def test_duplicate_station_day_is_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO scan_readings VALUES ('ridge', 1, 999)")


if __name__ == "__main__":
    unittest.main()
