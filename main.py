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

# Add tasks out of order (dates and pets interleaved) to prove sorting works.
scheduler.add_task(luna, luna_task_1)   # 2026-08-09
scheduler.add_task(chibi, chibi_task_3)  # today
scheduler.add_task(luna, luna_task_3)   # 2026-07-05
scheduler.add_task(chibi, chibi_task_1)  # today
scheduler.add_task(luna, luna_task_2)   # 2026-05-30
scheduler.add_task(chibi, chibi_task_2)  # 2026-07-04

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

def print_task_line(task: Task) -> None:
    """Print one task as: status, priority, title, pet, due date."""
    status = "X" if task.is_complete else " "
    print(f"  [{status}] {task.priority.value:<6} {task.title:<22} "
          f"{task.pet.name:<8} {task.due_date.strftime('%a, %b %d')}")


print(format_schedule_by_pet(scheduler))

# --- Sorted by time (added out of order above, printed earliest-first) ---
print(f"\n{'='*50}")
print("  ALL TASKS SORTED BY TIME")
print(f"{'='*50}")
for task in scheduler.sort_by_time():
    print_task_line(task)

# --- Filter by pet name ---
print(f"\n{'='*50}")
print("  FILTER: pet = chibi")
print(f"{'='*50}")
for task in scheduler.filter_tasks(pet_name="chibi"):
    print_task_line(task)

# --- Filter by status ---
print(f"\n{'='*50}")
print("  FILTER: incomplete tasks")
print(f"{'='*50}")
for task in scheduler.filter_tasks(is_complete=False):
    print_task_line(task)

# --- Combined filter: pet + status ---
print(f"\n{'='*50}")
print("  FILTER: chibi + incomplete")
print(f"{'='*50}")
for task in scheduler.filter_tasks(pet_name="chibi", is_complete=False):
    print_task_line(task)

# --- Conflict detection: warn on dates with 2+ tasks ---
conflicts = scheduler.check_conflicts()
if conflicts:
    for msg in conflicts:
        print(msg)