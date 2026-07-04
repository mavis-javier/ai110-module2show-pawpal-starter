from pawpal_system import Owner, Pet, Task, Scheduler, Priority
from datetime import date

scheduler = Scheduler()
pets = []
owner = Owner("owner1", scheduler, pets)

chibi = Pet("chibi", owner, scheduler)
pets.append(chibi)
luna = Pet("luna", owner, scheduler)
pets.append(luna)

chibi_task_1 = Task("walk chibi", "make her potty!", Priority.HIGH, date.today(), chibi, True)
chibi_task_2 = Task("bathtime", "", Priority.HIGH, date(2026, 7, 4), chibi)
chibi_task_3 = Task("trim nails", "cut and grind", Priority.LOW, date.today(), chibi)

luna_task_1 = Task("clean Luna's litter", "refill litter powder as well", Priority.MEDIUM, date(2026, 8, 9), luna)
luna_task_2 = Task("buy cat food", "buy treats if available", Priority.MEDIUM, date(2026, 5, 30), luna)
luna_task_3 = Task("brush Luna", "", Priority.MEDIUM, date(2026, 7, 5), luna)

scheduler.add_task(chibi, chibi_task_1)
scheduler.add_task(chibi, chibi_task_2)
scheduler.add_task(chibi, chibi_task_3)
scheduler.add_task(luna, luna_task_1)
scheduler.add_task(luna, luna_task_2)
scheduler.add_task(luna, luna_task_3)

def format_schedule_by_pet(scheduler: Scheduler) -> str:
    output = []

    for pet in owner.get_pets():
        pet_tasks = scheduler.get_tasks_by_pet(pet)
        if not pet_tasks:
            continue

        output.append(f"\n{'='*50}")
        output.append(f"  {pet.name.upper()}")
        output.append(f"{'='*50}")

        sorted_tasks = sorted(pet_tasks, key=lambda t: t.due_date)

        for task in sorted_tasks:
            status = "X" if task.is_complete else " "
            priority_icon = {"high": "***", "medium": "**", "low": "*"}[task.priority.value]

            output.append(f"[{status}] {priority_icon} {task.title:<28} {task.due_date.strftime('%a, %b %d')}")
            if task.description:
                output.append(f"             {task.description}")

    return "\n".join(output)

print(format_schedule_by_pet(scheduler))