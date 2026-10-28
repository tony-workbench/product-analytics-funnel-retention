-- Station reading changes using LAG.
-- Synthetic practice data. One row represents one recorded station reading.

-- Setup
CREATE TABLE scan_readings (
    station TEXT NOT NULL,
    day_no INTEGER NOT NULL,
    total INTEGER,
    PRIMARY KEY (station, day_no)
);

INSERT INTO scan_readings VALUES
    ('ridge', 1, 40),
    ('ridge', 3, 55),
    ('ridge', 4, NULL),
    ('ridge', 6, 70),
    ('quay', 1, 8),
    ('quay', 2, 8),
    ('quay', 5, 20),
    ('lake', 2, 5),
    ('lake', 3, 9),
    ('lake', 6, 12);

-- Report
WITH with_previous AS (
    SELECT station, day_no, total,
        LAG(day_no) OVER (
            PARTITION BY station ORDER BY day_no
        ) AS previous_day,
        LAG(total) OVER (
            PARTITION BY station ORDER BY day_no
        ) AS previous_total
    FROM scan_readings
)
SELECT station, day_no, previous_day, previous_total,
    day_no - previous_day AS days_elapsed,
    total - previous_total AS new_scans
FROM with_previous
ORDER BY station, day_no;

-- LAG reads the previous recorded row, including rows with unreadable totals.
-- A gap is not filled with invented readings. NULL is not converted to zero.
-- days_elapsed describes the interval; new_scans is an interval count, not a rate.
