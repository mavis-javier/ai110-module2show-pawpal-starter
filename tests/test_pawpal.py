import pytest
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler, Priority


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
