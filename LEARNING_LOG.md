# Learning Log

## 2026-09-19 — Week 4 (Sep 13–19): service failure counts

Week numbering follows the existing study-material folder, not completion of
four project stages. This is the first packaged project entry.

- **Learned:** CTE scope, LEFT JOIN row multiplication, grouped counts, and why
  counting a matched column preserves a zero for an unmatched service.
- **Built:** the service failure query and corrected explanation in the completed
  Python/SQLite exercise. The SQL was extracted and the project organized with
  Codex assistance; that packaging is not an additional personal skill claim.
- **Verified:** all 7 automated tests passed on 2026-09-19 using
  `python3 -B -m unittest discover -s tests -v`. The standalone command
  `sqlite3 :memory: < queries/service_failure_counts.sql` also ran successfully,
  returning 3 service rows and 3 total failures, matching the source count.
  Four of the seven tests are additional Codex packaging QA, not original
  submitted exercise checks.
- **Evidence:** `queries/service_failure_counts.sql` and
  `tests/test_service_failure_counts.py`.
- **What I Can Explain Now:** why the direct join returns two search rows, why
  grouping produces a single service summary, and why COUNT of the matched
  column gives zero for the unmatched row. Personal participation and ability
  to explain the submitted exercise were confirmed during review.
- **Next Milestone:** compare a preaggregated version against the same sample,
  explain its join grain, and test it. Not yet completed.

## 2026-10-09 — Week 7 (Oct 4–10): Lesson Practice 2 — ROW_NUMBER

Week numbering follows the current study-material week, not completion of a
project stage. Tony confirmed the completed exercise and requested its upload
on this date; scheduled lessons alone are not completion evidence.

- **Learned:** partitioned row numbering, separate ranking and display order,
  timestamp-first selection, explicit ID tie-breaking, and why MAX(ts) with
  a bare state column does not encode that tie-break.
- **Built:** newest and earliest device-update queries, a row-choice trace,
  and normal/tie test inputs in the completed Python/SQLite exercise. Codex
  extracted the same query logic into SQL views and organized the repository;
  six added QA tests are packaging assistance, not extra independent work.
- **Verified:** the original file ran successfully with all four assertions.
  `python3 -B -m unittest discover -s tests -v` passed all 17 repository tests
  (7 existing tests and 10 Lesson Practice 2 tests). Both standalone SQL scripts
  ran successfully in fresh databases. The new script returned two device rows
  per query, two tied maximum-time candidates for a, and counts of 2/2/2.
  The packaged permutation check passed newest and earliest expectations for
  all 120 insertion orders of the five-row tie fixture. These are local checks,
  not hosted CI or a production benchmark.
- **Evidence:** `queries/lesson_practice_2.sql` and
  `tests/test_lesson_practice_2.py`; existing service-count evidence is retained.
- **What I Can Explain Now:** the submitted explanation and trace show how
  PARTITION BY restarts numbering, why ts is compared before id, why the outer
  query filters rn, and why identical displayed states can come from different
  newest/earliest records. Tony confirmed the work as completed; private
  interview notes are not included in the public repository.
- **Next Milestone:** an independently completed LAG comparison and its
  validation, or the previously planned service-count preaggregation exercise.
  Neither is recorded as completed.
