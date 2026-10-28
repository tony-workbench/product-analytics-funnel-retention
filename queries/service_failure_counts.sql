-- Made-up data only; run it in a fresh SQLite database.
-- Counts failed requests (status 400 or higher) per service.
-- One output row represents one service.
CREATE TABLE services(id INTEGER, name TEXT);
INSERT INTO services VALUES (1, 'login'), (2, 'search'), (3, 'profile');
CREATE TABLE logs(id INTEGER, service_id INTEGER, status INTEGER);
INSERT INTO logs VALUES
    (10, 1, 200), (11, 1, 500), (12, 2, 404),
    (13, 2, 503), (14, 3, 200);

-- A temporary view lets the test runner inspect the same query.
CREATE TEMP VIEW service_failure_counts AS
WITH failures AS (
    SELECT service_id
    FROM logs
    WHERE status >= 400
)
SELECT
    services.id AS service_id,
    services.name,
    COUNT(failures.service_id) AS failure_count
FROM services
LEFT JOIN failures ON services.id = failures.service_id
GROUP BY services.id, services.name
ORDER BY services.id;

SELECT * FROM service_failure_counts ORDER BY service_id;

-- Validation queries: expect 3 output rows, 3 distinct service IDs,
-- and 3 total failures matching the source logs.
SELECT COUNT(*) AS output_rows,
       COUNT(DISTINCT service_id) AS unique_services,
       SUM(failure_count) AS total_failures
FROM service_failure_counts;
SELECT COUNT(*) AS source_failures FROM logs WHERE status >= 400;
