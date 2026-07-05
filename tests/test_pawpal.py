import pytest
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Recurrence


@pytest.fixture
def scheduler():
    return Scheduler()


@pytest.fixture
def owner(scheduler):
    return Owner(username="john_doe", scheduler=scheduler)


@pytest.fixture
def pet(owner):
    pet = Pet(name="Buddy", owner=owner)
    owner.add_pet(pet)
    return pet


@pytest.fixture
def task(pet):
    return Task(
        title="Walk the dog",
        description="Take Buddy for a 30-minute walk",
        priority=Priority.HIGH,
        due_date=date(2026, 7, 5),
        pet=pet
    )


def test_mark_complete_changes_task_status(task):
    """Verify that mark_complete() changes task status from incomplete to complete."""
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_adding_task_increases_pet_task_count(pet, scheduler):
    """Verify that adding a task to scheduler increases the pet's task count."""
    initial_count = len(pet.get_tasks())
    assert initial_count == 0

    task = Task(
        title="Feed the dog",
        description="Give Buddy their dinner",
        priority=Priority.MEDIUM,
        due_date=date(2026, 7, 4),
        pet=pet
    )
    scheduler.add_task(pet, task)

    final_count = len(pet.get_tasks())
    assert final_count == 1
    assert final_count == initial_count + 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(pet, title, due_date, recurrence=Recurrence.NONE,
               priority=Priority.MEDIUM):
    """Build a Task without registering it (tests add explicitly when needed)."""
    return Task(
        title=title,
        description=f"{title} desc",
        priority=priority,
        due_date=due_date,
        pet=pet,
        recurrence=recurrence,
    )


# ---------------------------------------------------------------------------
# Sorting edge cases
# ---------------------------------------------------------------------------

def test_sort_by_time_empty(scheduler):
    """Empty scheduler sorts to empty list, no crash."""
    assert scheduler.sort_by_time() == []


def test_sort_by_time_orders_earliest_first(pet, scheduler):
    """Default sort puts earliest due_date first."""
    late = _make_task(pet, "late", date(2026, 7, 10))
    early = _make_task(pet, "early", date(2026, 7, 1))
    mid = _make_task(pet, "mid", date(2026, 7, 5))
    for t in (late, early, mid):
        scheduler.add_task(pet, t)

    assert scheduler.sort_by_time() == [early, mid, late]


def test_sort_by_time_reverse(pet, scheduler):
    """reverse=True puts latest due_date first."""
    a = _make_task(pet, "a", date(2026, 7, 1))
    b = _make_task(pet, "b", date(2026, 7, 5))
    c = _make_task(pet, "c", date(2026, 7, 10))
    for t in (a, b, c):
        scheduler.add_task(pet, t)

    assert scheduler.sort_by_time(reverse=True) == [c, b, a]


def test_sort_by_time_is_stable_on_ties(pet, scheduler):
    """Tasks with same due_date keep insertion order (Timsort is stable)."""
    same = date(2026, 7, 5)
    first = _make_task(pet, "first", same)
    second = _make_task(pet, "second", same)
    third = _make_task(pet, "third", same)
    for t in (first, second, third):
        scheduler.add_task(pet, t)

    assert scheduler.sort_by_time() == [first, second, third]


def test_sort_by_time_does_not_mutate_source(pet, scheduler):
    """sort_by_time returns a new list; self.tasks order is unchanged."""
    late = _make_task(pet, "late", date(2026, 7, 10))
    early = _make_task(pet, "early", date(2026, 7, 1))
    scheduler.add_task(pet, late)
    scheduler.add_task(pet, early)

    result = scheduler.sort_by_time()
    assert result is not scheduler.tasks
    assert scheduler.tasks == [late, early]  # original insertion order intact


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_none_when_all_distinct_dates(pet, scheduler):
    """No two tasks share a date -> empty conflict dict."""
    scheduler.add_task(pet, _make_task(pet, "a", date(2026, 7, 1)))
    scheduler.add_task(pet, _make_task(pet, "b", date(2026, 7, 2)))
    assert scheduler.detect_conflicts() == {}


def test_detect_conflicts_flags_shared_date(pet, scheduler):
    """Two tasks on same date are flagged as a conflict."""
    day = date(2026, 7, 5)
    a = _make_task(pet, "a", day)
    b = _make_task(pet, "b", day)
    scheduler.add_task(pet, a)
    scheduler.add_task(pet, b)

    conflicts = scheduler.detect_conflicts()
    assert list(conflicts.keys()) == [day]
    assert conflicts[day] == [a, b]


def test_detect_conflicts_three_tasks_same_date(pet, scheduler):
    """3+ tasks on one date all land in the conflict bucket."""
    day = date(2026, 7, 5)
    tasks = [_make_task(pet, f"t{i}", day) for i in range(3)]
    for t in tasks:
        scheduler.add_task(pet, t)

    assert scheduler.detect_conflicts()[day] == tasks


def test_detect_conflicts_output_is_date_sorted(pet, scheduler):
    """Conflict dates are returned in ascending order."""
    late = date(2026, 7, 20)
    early = date(2026, 7, 2)
    for day in (late, early):
        scheduler.add_task(pet, _make_task(pet, "x", day))
        scheduler.add_task(pet, _make_task(pet, "y", day))

    assert list(scheduler.detect_conflicts().keys()) == [early, late]


def test_detect_conflicts_same_pet_only_ignores_cross_pet(owner, scheduler):
    """Two pets on the same date: flagged by default, ignored when same_pet_only."""
    p1 = Pet(name="Buddy", owner=owner)
    p2 = Pet(name="Rex", owner=owner)
    owner.add_pet(p1)
    owner.add_pet(p2)
    day = date(2026, 7, 5)
    scheduler.add_task(p1, _make_task(p1, "walk", day))
    scheduler.add_task(p2, _make_task(p2, "feed", day))

    assert day in scheduler.detect_conflicts()                      # default: flagged
    assert scheduler.detect_conflicts(same_pet_only=True) == {}     # cross-pet ignored


def test_detect_conflicts_same_pet_only_flags_single_pet(pet, scheduler):
    """same_pet_only=True flags a date where one pet has 2+ tasks."""
    day = date(2026, 7, 5)
    scheduler.add_task(pet, _make_task(pet, "a", day))
    scheduler.add_task(pet, _make_task(pet, "b", day))

    assert day in scheduler.detect_conflicts(same_pet_only=True)


def test_check_conflicts_empty_when_no_conflicts(pet, scheduler):
    """check_conflicts returns [] so callers keep running."""
    scheduler.add_task(pet, _make_task(pet, "a", date(2026, 7, 1)))
    assert scheduler.check_conflicts() == []


# ---------------------------------------------------------------------------
# Recurring task edge cases
# ---------------------------------------------------------------------------

def test_next_due_date_none_when_not_recurring(pet):
    """Non-recurring task has no next occurrence."""
    t = _make_task(pet, "once", date(2026, 7, 5), Recurrence.NONE)
    assert t.next_due_date() is None


def test_next_due_date_daily(pet):
    t = _make_task(pet, "d", date(2026, 7, 5), Recurrence.DAILY)
    assert t.next_due_date() == date(2026, 7, 6)


def test_next_due_date_weekly(pet):
    t = _make_task(pet, "w", date(2026, 7, 5), Recurrence.WEEKLY)
    assert t.next_due_date() == date(2026, 7, 12)


def test_monthly_clamps_jan31_to_feb28_non_leap(pet):
    """Jan 31 -> Feb 28 in a non-leap year (day clamped to month length)."""
    t = _make_task(pet, "m", date(2026, 1, 31), Recurrence.MONTHLY)
    assert t.next_due_date() == date(2026, 2, 28)


def test_monthly_clamps_jan31_to_feb29_leap(pet):
    """Jan 31 -> Feb 29 in a leap year."""
    t = _make_task(pet, "m", date(2028, 1, 31), Recurrence.MONTHLY)
    assert t.next_due_date() == date(2028, 2, 29)


def test_monthly_rolls_over_year(pet):
    """Dec -> Jan increments the year."""
    t = _make_task(pet, "m", date(2026, 12, 15), Recurrence.MONTHLY)
    assert t.next_due_date() == date(2027, 1, 15)


def test_mark_complete_non_recurring_returns_none(pet, scheduler):
    """Completing a non-recurring task spawns nothing."""
    t = _make_task(pet, "once", date(2026, 7, 5), Recurrence.NONE)
    scheduler.add_task(pet, t)
    assert t.mark_complete() is None
    assert len(scheduler.get_all_tasks()) == 1


def test_mark_complete_recurring_spawns_next_in_scheduler(pet, scheduler):
    """Completing a daily task adds the next occurrence to the scheduler."""
    t = _make_task(pet, "daily", date(2026, 7, 5), Recurrence.DAILY)
    scheduler.add_task(pet, t)

    nxt = t.mark_complete()
    assert t.is_complete is True
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 6)
    assert nxt in scheduler.get_all_tasks()
    assert len(scheduler.get_all_tasks()) == 2


def test_mark_complete_recurring_without_scheduler_not_added(owner):
    """Recurring task on a pet with no scheduler: next task returned but not added."""
    lone = Pet(name="Lone", owner=owner, scheduler=None)
    t = _make_task(lone, "daily", date(2026, 7, 5), Recurrence.DAILY)
    nxt = t.mark_complete()
    assert nxt is not None
    assert nxt.due_date == date(2026, 7, 6)
    # No scheduler to assert against — just confirm no crash and a task returned.


def test_mark_complete_is_idempotent(pet, scheduler):
    """Completing an already-complete task spawns nothing (guarded re-complete)."""
    t = _make_task(pet, "daily", date(2026, 7, 5), Recurrence.DAILY)
    scheduler.add_task(pet, t)

    first = t.mark_complete()   # spawns Jul 6
    second = t.mark_complete()  # already complete -> no-op

    assert first is not None
    assert second is None
    # 1 original + 1 spawned = 2. Second call did not duplicate.
    assert len(scheduler.get_all_tasks()) == 2
