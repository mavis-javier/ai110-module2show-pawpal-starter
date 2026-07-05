import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_desc = st.text_input("Task description", value="Walk around the block")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

due_date = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    # Create Owner + Pet from inputs (once), then add Task via scheduler
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(username=owner_name, scheduler=st.session_state.scheduler)
    if "pet" not in st.session_state:
        pet = Pet(name=pet_name, owner=st.session_state.owner)
        st.session_state.owner.add_pet(pet)
        st.session_state.pet = pet

    task = Task(
        title=task_title,
        description=task_desc,
        priority=Priority[priority.upper()],
        due_date=due_date,
        pet=st.session_state.pet,
    )
    st.session_state.scheduler.add_task(st.session_state.pet, task)
    st.session_state.tasks.append(task)
    st.success(f"Added task '{task_title}' for {st.session_state.pet.name} ({species})")

def _task_rows(tasks):
    return [
        {
            "Title": t.title,
            "Description": t.description,
            "Priority": t.priority.value,
            "Due Date": str(t.due_date),
            "Complete": t.is_complete,
        }
        for t in tasks
    ]


if st.session_state.tasks:
    order = st.radio(
        "Sort by due date", ["Earliest first", "Latest first"], horizontal=True
    )
    sorted_tasks = st.session_state.scheduler.sort_by_time(
        reverse=(order == "Latest first")
    )
    st.write("Current tasks:")
    st.table(_task_rows(sorted_tasks))
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

same_pet_only = st.checkbox(
    "Only warn when one pet is double-booked", value=False
)

if st.button("Generate schedule"):
    sched = st.session_state.scheduler

    warnings = sched.check_conflicts(same_pet_only=same_pet_only)
    if warnings:
        for msg in warnings:
            st.warning(msg)
    else:
        st.info("No scheduling conflicts.")

    plan = sched.sort_by_time()
    if plan:
        st.write("Planned tasks (earliest due first):")
        st.table(_task_rows(plan))
    else:
        st.info("No tasks to schedule. Add one above.")
