from dataclasses import dataclass, field
from enum import Enum
from datetime import date, timedelta
from typing import List, Dict, Optional


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recurrence(Enum):
    """How often a task repeats."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


def _add_month(d: date) -> date:
    """Return the date one calendar month after ``d``.

    Clamps the day to the target month's length, so Jan 31 -> Feb 28
    (or Feb 29 in a leap year).
    """
    month = d.month + 1
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    # First day of the month after the target gives us the target's length.
    if month == 12:
        last_day = 31
    else:
        last_day = (date(year, month + 1, 1) - timedelta(days=1)).day
    return date(year, month, min(d.day, last_day))


@dataclass
class Task:
    """A task assigned to a pet with priority and due date."""
    title: str
    description: str
    priority: Priority
    due_date: date
    pet: "Pet"
    is_complete: bool = False
    recurrence: Recurrence = Recurrence.NONE

    def get_details(self) -> str:
        """Return formatted task details."""
        return f"{self.title}: {self.description} (Priority: {self.priority.value})"

    def next_due_date(self) -> Optional[date]:
        """Return the due date of the next occurrence, or None if not recurring.

        Advances due_date by one interval based on recurrence: +1 day, +1 week,
        or +1 calendar month (via ``_add_month``, which clamps the day). O(1).
        """
        if self.recurrence == Recurrence.DAILY:
            return self.due_date + timedelta(days=1)
        if self.recurrence == Recurrence.WEEKLY:
            return self.due_date + timedelta(weeks=1)
        if self.recurrence == Recurrence.MONTHLY:
            return _add_month(self.due_date)
        return None

    def mark_complete(self) -> Optional["Task"]:
        """Mark task as complete.

        If this is a recurring task (daily, weekly, or monthly), create the
        next occurrence — same title/description/priority/pet/recurrence with
        due_date advanced by the interval — and add it to the pet's scheduler.
        Returns the new Task, or None if the task is not recurring.
        """
        # address edge case if button is clicked twice to mark task complete and the same completed task is appended
        if self.is_complete:    # already done - do nothing
            return None
        self.is_complete = True

        next_date = self.next_due_date()
        if next_date is None:
            return None

        next_task = Task(
            title=self.title,
            description=self.description,
            priority=self.priority,
            due_date=next_date,
            pet=self.pet,
            recurrence=self.recurrence,
        )

        scheduler = getattr(self.pet, "scheduler", None)
        if scheduler is not None:
            scheduler.add_task(self.pet, next_task)
        return next_task


@dataclass
class Pet:
    """A pet owned by an owner with assigned tasks."""
    name: str
    owner: "Owner"
    scheduler: "Scheduler" = None

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        if not self.scheduler:
            raise ValueError(f"Pet {self.name} not registered with scheduler")
        return self.scheduler.get_tasks_by_pet(self)


@dataclass
class Scheduler:
    """Manages tasks for multiple pets."""
    tasks: List[Task] = field(default_factory=list)
    pet_tasks: Dict[str, List[Task]] = field(default_factory=dict)

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a task to the scheduler for a given pet."""
        if task.pet != pet:
            raise ValueError(f"Task pet {task.pet.name} does not match {pet.name}")
        self.tasks.append(task)
        pet_key = id(pet)
        if pet_key not in self.pet_tasks:
            self.pet_tasks[pet_key] = []
        self.pet_tasks[pet_key].append(task)

    def remove_task(self, task: Task) -> bool:
        """Remove a task from the scheduler; return True if successful."""
        if task not in self.tasks:
            return False
        self.tasks.remove(task)
        pet_key = id(task.pet)
        if pet_key in self.pet_tasks:
            self.pet_tasks[pet_key].remove(task)
        return True

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        """Return all tasks assigned to a specific pet."""
        return self.pet_tasks.get(id(pet), [])

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks in the scheduler."""
        return self.tasks

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Return all tasks with a given priority level."""
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_status(self, is_complete: bool) -> List[Task]:
        """Return all tasks matching the given completion status."""
        return [task for task in self.tasks if task.is_complete == is_complete]

    def sort_by_time(self, reverse: bool = False) -> List[Task]:
        """Return all tasks sorted by due date (earliest first by default).

        Uses Python's built-in Timsort via ``sorted()``: O(n log n) time,
        O(n) space, and stable (tasks with the same due_date keep their
        insertion order). Returns a new list; ``self.tasks`` is unchanged.
        """
        return sorted(self.tasks, key=lambda task: task.due_date, reverse=reverse)

    def filter_tasks(self, pet_name: str = None, is_complete: bool = None) -> List[Task]:
        """Return tasks matching the given pet name and/or status.

        Each filter is optional; None means "any". Supply both to require both
        (e.g. incomplete tasks for "chibi"). Pet name match is case-insensitive.

        Algorithm: a single linear scan applying each supplied predicate, so
        O(n) time in the number of tasks. Result preserves insertion order.
        """
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet.name.lower() == pet_name.lower()]
        if is_complete is not None:
            result = [t for t in result if t.is_complete == is_complete]
        return result

    def detect_conflicts(self, same_pet_only: bool = False) -> Dict[date, List[Task]]:
        """Return dates that have two or more tasks scheduled (a conflict).

        Since tasks are tracked by due_date only, "same time" means same date.
        By default a conflict is any date with 2+ tasks, whether they belong to
        the same pet or different pets. Set same_pet_only=True to only flag
        dates where one pet has 2+ tasks.

        Algorithm: bucket tasks into a dict keyed by due_date (one linear pass,
        O(n)), then keep only buckets with a collision. This hash-bucket
        approach avoids the O(n^2) cost of comparing every task pair. Overall
        O(n) time and O(n) space; the final sort of conflicting dates is
        O(k log k) where k is the number of conflicting days.
        """
        by_date: Dict[date, List[Task]] = {}
        for task in self.tasks:
            by_date.setdefault(task.due_date, []).append(task)

        conflicts: Dict[date, List[Task]] = {}
        for day, tasks in by_date.items():
            if same_pet_only:
                # Flag the day if any single pet has more than one task on it.
                per_pet: Dict[int, int] = {}
                for t in tasks:
                    per_pet[id(t.pet)] = per_pet.get(id(t.pet), 0) + 1
                if any(count >= 2 for count in per_pet.values()):
                    conflicts[day] = tasks
            elif len(tasks) >= 2:
                conflicts[day] = tasks

        return dict(sorted(conflicts.items()))

    def check_conflicts(self, same_pet_only: bool = False) -> List[str]:
        """Lightweight conflict check that warns instead of crashing.

        Returns a list of human-readable warning messages, one per conflicting
        date. Returns an empty list when there are no conflicts, so callers can
        print warnings and keep running rather than raising an error.
        """
        warnings = []
        for day, tasks in self.detect_conflicts(same_pet_only=same_pet_only).items():
            names = ", ".join(f"{t.title} ({t.pet.name})" for t in tasks)
            warnings.append(
                f"WARNING: {len(tasks)} tasks scheduled on "
                f"{day.strftime('%a, %b %d %Y')}: {names}"
            )
        return warnings


@dataclass
class Owner:
    """An owner who manages multiple pets."""
    username: str
    scheduler: "Scheduler"
    pets: List[Pet] = field(default_factory=list)

    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's collection."""
        if pet in self.pets:
            raise ValueError(f"Pet {pet.name} already owned by {self.username}")
        pet.scheduler = self.scheduler
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> bool:
        """Remove a pet from this owner's collection; return True if successful."""
        if pet not in self.pets:
            return False
        self.pets.remove(pet)
        pet.scheduler = None
        return True
