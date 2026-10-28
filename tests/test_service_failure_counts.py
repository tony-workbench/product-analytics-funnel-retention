"""Tests for the per-service failure counts in service_failure_counts.sql."""
import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / 'queries/service_failure_counts.sql'


class ServiceFailureTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.executescript(SQL.read_text(encoding='utf-8'))

    def rows(self):
        return self.db.execute(
            'SELECT * FROM service_failure_counts ORDER BY service_id'
        ).fetchall()

    def test_normal(self):
        self.assertEqual(self.rows()[0], (1, 'login', 1))

    def test_fanout_counterexample_and_fix(self):
        direct = self.db.execute('''
            WITH failures AS (SELECT service_id FROM logs WHERE status >= 400)
            SELECT services.id, services.name FROM services
            LEFT JOIN failures ON services.id = failures.service_id
            WHERE services.id = 2
        ''').fetchall()
        self.assertEqual(direct, [(2, 'search'), (2, 'search')])
        self.assertEqual(self.rows()[1], (2, 'search', 2))

    def test_zero_failures(self):
        self.assertEqual(self.rows()[2], (3, 'profile', 0))

    # The remaining tests cover extra edge cases beyond the original exercise.
    def test_one_row_per_service(self):
        self.assertEqual(len(self.rows()), 3)
        self.assertEqual(len({row[0] for row in self.rows()}), 3)

    def test_reconciliation(self):
        total = self.db.execute(
            'SELECT COUNT(*) FROM logs WHERE status >= 400'
        ).fetchone()[0]
        self.assertEqual(sum(row[2] for row in self.rows()), total)
        self.assertEqual(total, 3)

    def test_service_without_logs(self):
        self.db.execute("INSERT INTO services VALUES (4, 'empty')")
        self.assertEqual(self.rows()[-1], (4, 'empty', 0))

    def test_unknown_status_not_counted(self):
        self.db.execute('INSERT INTO logs VALUES (15, 3, NULL)')
        self.assertEqual(self.rows()[2], (3, 'profile', 0))


if __name__ == '__main__':
    unittest.main()
