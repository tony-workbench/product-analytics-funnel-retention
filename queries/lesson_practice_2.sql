-- Lesson Practice 2: deterministic newest/earliest update per device.
-- Synthetic data only; execute in a fresh SQLite database.
-- Query logic is retained from Tony's completed Python/SQLite exercise.
-- Codex added reusable views and packaging checks, not new personal skill claims.
-- Assumptions: unique IDs and non-null, comparable device/ts/state values.
-- The schema does not enforce those assumptions. Exact ts/id ties, NULLs,
-- duplicate IDs, and invalid types are outside the validated input contract.

CREATE TABLE updates (
    id INTEGER,
    device TEXT,
    ts INTEGER,
    state TEXT
);

INSERT INTO updates VALUES
    (1, 'a', 10, 'online'),
    (2, 'a', 12, 'offline'),
    (3, 'a', 12, 'online'),
    (4, 'b', 7, 'offline');

-- One output row represents one device and the state of its selected update.
-- PARTITION BY device restarts numbering for each device.
-- Compare ts first; the greater id resolves a newest-time tie.
-- The CTE computes rn before the outer WHERE filters it.
-- The outer ORDER BY controls display order, not winner selection.
CREATE TEMP VIEW newest_device_updates AS
WITH ranked AS (
    SELECT id, device, ts, state,
        ROW_NUMBER() OVER (
            PARTITION BY device
            ORDER BY ts DESC, id DESC
        ) AS rn
    FROM updates
)
SELECT device, state
FROM ranked
WHERE rn = 1
ORDER BY device;

-- Reverse both sort directions for the earliest update.
-- At an earliest-time tie, the smaller id wins.
CREATE TEMP VIEW earliest_device_updates AS
WITH ranked AS (
    SELECT id, device, ts, state,
        ROW_NUMBER() OVER (
            PARTITION BY device
            ORDER BY ts ASC, id ASC
        ) AS rn
    FROM updates
)
SELECT device, state
FROM ranked
WHERE rn = 1
ORDER BY device;

SELECT * FROM newest_device_updates ORDER BY device;
SELECT * FROM earliest_device_updates ORDER BY device;

-- Both sample outputs: a|online, b|offline.
-- Newest selects id 3 for a and id 4 for b.
-- Earliest selects id 1 for a and id 4 for b: equal displayed states do not
-- imply that the selected input rows are the same.
-- Newest hand trace for a: id 3 -> rn 1, id 2 -> rn 2, id 1 -> rn 3.

-- Why SELECT device, MAX(ts), state ... GROUP BY device is insufficient:
-- device a has two updates at ts=12 with different states. MAX(ts) does not
-- encode the id tie-break. SQLite can choose either tied row's bare state.
-- The check below exposes both tied candidates; it does not depend on which
-- arbitrary state SQLite returns from the aggregate shortcut.
SELECT device, ts, COUNT(*) AS tied_candidates
FROM updates
WHERE (device, ts) IN (
    SELECT device, MAX(ts) FROM updates GROUP BY device
)
GROUP BY device, ts
HAVING COUNT(*) > 1;
-- Expected: a|12|2.

-- Reconcile output grain to the source device population; expect 2|2|2.
SELECT (SELECT COUNT(*) FROM newest_device_updates) AS newest_rows,
       (SELECT COUNT(*) FROM earliest_device_updates) AS earliest_rows,
       (SELECT COUNT(DISTINCT device) FROM updates) AS source_devices;

-- Original normal test inputs (id, device, ts, state):
-- (30,'c',4,'offline'), (10,'c',9,'online'),
-- (50,'a',7,'online'), (60,'a',3,'offline').
-- Newest expected: [('a','online'), ('c','online')]. Time outranks ID.
-- Original tie counterexample inputs:
-- (8,'b',20,'online'), (3,'b',20,'offline'), (99,'b',5,'offline'),
-- (7,'a',10,'offline'), (2,'a',10,'online').
-- Newest expected: [('a','offline'), ('b','online')]. Greater ID wins the tie.
-- Executable versions of these inputs and checks are in tests/test_lesson_practice_2.py.
