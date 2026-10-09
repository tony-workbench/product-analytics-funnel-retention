"""Retain the four submitted checks; distinguish six added packaging QA checks."""
import itertools
import sqlite3
import unittest
from pathlib import Path

SQL = Path(__file__).resolve().parents[1] / 'queries/lesson_practice_2.sql'
NORMAL_ROWS = [
    (30, 'c', 4, 'offline'),
    (10, 'c', 9, 'online'),
    (50, 'a', 7, 'online'),
    (60, 'a', 3, 'offline'),
]
COUNTEREXAMPLE_ROWS = [
    (8, 'b', 20, 'online'),
    (3, 'b', 20, 'offline'),
    (99, 'b', 5, 'offline'),
    (7, 'a', 10, 'offline'),
    (2, 'a', 10, 'online'),
]


class DeviceUpdateTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.executescript(SQL.read_text(encoding='utf-8'))

    def replace_rows(self, rows):
        self.db.execute('DELETE FROM updates')
        self.db.executemany('INSERT INTO updates VALUES (?, ?, ?, ?)', rows)

    def newest(self):
        return self.db.execute(
            'SELECT * FROM newest_device_updates ORDER BY device'
        ).fetchall()

    def earliest(self):
        return self.db.execute(
            'SELECT * FROM earliest_device_updates ORDER BY device'
        ).fetchall()

    # These four assertions reproduce the completed source exercise.
    def test_original_newest_sample(self):
        self.assertEqual(self.newest(), [('a', 'online'), ('b', 'offline')])

    def test_original_earliest_sample(self):
        self.assertEqual(self.earliest(), [('a', 'online'), ('b', 'offline')])

    def test_original_normal_timestamp_priority(self):
        self.replace_rows(NORMAL_ROWS)
        self.assertEqual(self.newest(), [('a', 'online'), ('c', 'online')])

    def test_original_newest_tie_counterexample(self):
        self.replace_rows(COUNTEREXAMPLE_ROWS)
        self.assertEqual(self.newest(), [('a', 'offline'), ('b', 'online')])

    # The following six tests were added by Codex during project packaging.
    def test_empty_input(self):
        self.replace_rows([])
        self.assertEqual(self.newest(), [])
        self.assertEqual(self.earliest(), [])

    def test_single_update(self):
        self.replace_rows([(9, 'single', 3, 'offline')])
        self.assertEqual(self.newest(), [('single', 'offline')])
        self.assertEqual(self.earliest(), [('single', 'offline')])

    def test_earliest_tie_and_timestamp_priority(self):
        self.replace_rows([
            (50, 'd', 7, 'online'),
            (10, 'd', 9, 'offline'),
            (60, 'd', 7, 'offline'),
        ])
        self.assertEqual(self.earliest(), [('d', 'online')])
        self.assertEqual(self.newest(), [('d', 'offline')])

    def test_all_counterexample_insertion_orders(self):
        # Five distinct records have 120 possible insertion orders.
        for rows in itertools.permutations(COUNTEREXAMPLE_ROWS):
            with self.subTest(rows=rows):
                self.replace_rows(rows)
                self.assertEqual(self.newest(), [('a', 'offline'), ('b', 'online')])
                self.assertEqual(self.earliest(), [('a', 'online'), ('b', 'offline')])

    def test_output_population_and_grain(self):
        source_devices = self.db.execute(
            'SELECT DISTINCT device FROM updates ORDER BY device'
        ).fetchall()
        for result in [self.newest(), self.earliest()]:
            self.assertEqual([(row[0],) for row in result], source_devices)
            self.assertEqual(len(result), len({row[0] for row in result}))

    def test_max_timestamp_leaves_two_candidate_states(self):
        candidates = self.db.execute('''
            SELECT id, state FROM updates
            WHERE device = 'a'
              AND ts = (SELECT MAX(ts) FROM updates WHERE device = 'a')
            ORDER BY id
        ''').fetchall()
        self.assertEqual(candidates, [(2, 'offline'), (3, 'online')])
        self.assertEqual(self.newest()[0], ('a', 'online'))


if __name__ == '__main__':
    unittest.main()
