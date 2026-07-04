from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import List, Dict


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """A task assigned to a pet with priority and due date."""
    title: str
    description: str
    priority: Priority
    due_date: date
    pet: "Pet"
    is_complete: bool = False

    def get_details(self) -> str:
        """Return formatted task details."""
        return f"{self.title}: {self.description} (Priority: {self.priority.value})"

    def mark_complete(self) -> None:
        """Mark task as complete."""
        self.is_complete = True


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
