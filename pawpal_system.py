from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import List, Optional


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    title: str
    description: str
    priority: Priority
    due_date: date
    pet: Optional["Pet"] = None
    is_complete: bool = False

    def get_details(self) -> str:
        return f"{self.title}: {self.description} (Priority: {self.priority.value})"

    def mark_complete(self) -> None:
        self.is_complete = True


@dataclass
class Pet:
    name: str
    owner: "Owner"

    def get_tasks(self, scheduler: "Scheduler") -> List[Task]:
        return scheduler.get_tasks_by_pet(self)


@dataclass
class Scheduler:
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, pet: Pet, task: Task) -> None:
        task.pet = pet
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks_by_pet(self, pet: Pet) -> List[Task]:
        return [task for task in self.tasks if task.pet == pet]

    def get_all_tasks(self) -> List[Task]:
        return self.tasks

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        return [task for task in self.tasks if task.priority == priority]

    def get_tasks_by_status(self, is_complete: bool) -> List[Task]:
        return [task for task in self.tasks if task.is_complete == is_complete]


@dataclass
class Owner:
    username: str
    pets: List[Pet] = field(default_factory=list)

    def get_pets(self) -> List[Pet]:
        return self.pets

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pets:
            self.pets.remove(pet)
