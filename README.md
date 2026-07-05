# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
==================================================
  CHIBI
==================================================
[X] *** walk chibi                   Fri, Jul 03
             make her potty!
[ ] * trim nails                   Fri, Jul 03
             cut and grind
[ ] *** bathtime                     Sat, Jul 04

==================================================
  LUNA
==================================================
[ ] ** buy cat food                 Sat, May 30
             buy treats if available
[ ] ** brush Luna                   Sun, Jul 05
[ ] ** clean Luna's litter          Sun, Aug 09
             refill litter powder as well
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Verbose, one line per test:
python -m pytest -v
```

The suite lives in `tests/test_pawpal.py` and covers the smarter-scheduling
behaviors plus their edge cases:

| Area | What's covered |
|------|----------------|
| **Sorting** (`sort_by_time`) | Empty scheduler, earliest-first order, `reverse=True`, tie stability (same-day tasks keep insertion order), and that the source list is not mutated. |
| **Conflict detection** (`detect_conflicts` / `check_conflicts`) | No conflict when dates are distinct, flagging a shared date, 3+ tasks on one date, ascending date order of results, `same_pet_only` ignoring cross-pet collisions but flagging one pet with 2+ tasks, and `check_conflicts` returning `[]` when clean. |
| **Recurring tasks** (`next_due_date` / `mark_complete`) | `NONE` → `None`, daily/weekly advance, monthly day-clamp (Jan 31 → Feb 28 non-leap, Feb 29 leap), Dec → Jan year rollover, non-recurring completion returns `None`, recurring completion spawns the next occurrence into the scheduler, the no-scheduler branch (task returned but not added), and **idempotent re-complete** (a second `mark_complete()` is a no-op — no duplicate occurrence). |

Sample test output:

```
============================= test session starts =============================
collected 24 items

tests/test_pawpal.py::test_mark_complete_changes_task_status PASSED      [  4%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  8%]
tests/test_pawpal.py::test_sort_by_time_empty PASSED                     [ 12%]
tests/test_pawpal.py::test_sort_by_time_orders_earliest_first PASSED     [ 16%]
tests/test_pawpal.py::test_sort_by_time_reverse PASSED                   [ 20%]
tests/test_pawpal.py::test_sort_by_time_is_stable_on_ties PASSED         [ 25%]
tests/test_pawpal.py::test_sort_by_time_does_not_mutate_source PASSED    [ 29%]
tests/test_pawpal.py::test_detect_conflicts_none_when_all_distinct_dates PASSED [ 33%]
tests/test_pawpal.py::test_detect_conflicts_flags_shared_date PASSED     [ 37%]
tests/test_pawpal.py::test_detect_conflicts_three_tasks_same_date PASSED [ 41%]
tests/test_pawpal.py::test_detect_conflicts_output_is_date_sorted PASSED [ 45%]
tests/test_pawpal.py::test_detect_conflicts_same_pet_only_ignores_cross_pet PASSED [ 50%]
tests/test_pawpal.py::test_detect_conflicts_same_pet_only_flags_single_pet PASSED [ 54%]
tests/test_pawpal.py::test_check_conflicts_empty_when_no_conflicts PASSED [ 58%]
tests/test_pawpal.py::test_next_due_date_none_when_not_recurring PASSED  [ 62%]
tests/test_pawpal.py::test_next_due_date_daily PASSED                    [ 66%]
tests/test_pawpal.py::test_next_due_date_weekly PASSED                   [ 70%]
tests/test_pawpal.py::test_monthly_clamps_jan31_to_feb28_non_leap PASSED [ 75%]
tests/test_pawpal.py::test_monthly_clamps_jan31_to_feb29_leap PASSED     [ 79%]
tests/test_pawpal.py::test_monthly_rolls_over_year PASSED                [ 83%]
tests/test_pawpal.py::test_mark_complete_non_recurring_returns_none PASSED [ 87%]
tests/test_pawpal.py::test_mark_complete_recurring_spawns_next_in_scheduler PASSED [ 91%]
tests/test_pawpal.py::test_mark_complete_recurring_without_scheduler_not_added PASSED [ 95%]
tests/test_pawpal.py::test_mark_complete_is_idempotent PASSED            [100%]

============================= 24 passed in 0.15s ==============================
```
### Confidence Level
5 stars for reliability

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. Tasks are tracked by
`due_date` (calendar day), so "time" throughout means the due date.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time(reverse=False)` | Returns a new list sorted by `due_date`, earliest first (`reverse=True` for latest first). Built-in Timsort, O(n log n), stable — same-day tasks keep insertion order. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, is_complete=None)` | Filter by pet name (case-insensitive), completion status, or both (AND). `None` means "any". Single linear scan, O(n). |
| Conflict handling | `Scheduler.detect_conflicts(same_pet_only=False)` · `Scheduler.check_conflicts(...)` | Flags any date with 2+ tasks. `same_pet_only=True` flags only when one pet has 2+ on a day. `detect_conflicts` returns `{date: [tasks]}`; `check_conflicts` returns human-readable warning strings and never raises, so callers warn and keep running. Hash-bucket by date, O(n) — no pairwise comparison. |
| Recurring tasks | `Recurrence` enum · `Task.next_due_date()` · `Task.mark_complete()` | Recurrence is one of `NONE`, `DAILY`, `WEEKLY`, `MONTHLY`. Completing a recurring task auto-creates the next occurrence (due date advanced by the interval) and adds it to the scheduler. Monthly advance clamps the day (Jan 31 → Feb 28). `mark_complete()` returns the new `Task`, or `None` if not recurring. |

### Example

```python
scheduler.sort_by_time()                                   # all tasks, earliest due first
scheduler.filter_tasks(pet_name="chibi", is_complete=False)  # chibi's incomplete tasks

for msg in scheduler.check_conflicts():                    # warn on double-booked days
    print(msg)
# WARNING: 3 tasks scheduled on Sun, Jul 05 2026: trim nails (chibi), brush Luna (luna), walk chibi (chibi)

daily = Task("walk", "", Priority.HIGH, date.today(), chibi, recurrence=Recurrence.DAILY)
scheduler.add_task(chibi, daily)
next_walk = daily.mark_complete()   # next_walk.due_date is tomorrow, already in the scheduler
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
