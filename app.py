import streamlit as st

from datetime import date
from uuid import uuid4

from pawpal_system import Owner, Pet, Scheduler, Task

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

st.subheader("Quick Demo Inputs (wired to logic)")

owner_name = st.text_input("Owner name", value="Jordan")

# Streamlit reruns top-to-bottom; store the Owner in session_state so it persists.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name=owner_name)

owner: Owner = st.session_state.owner
owner.owner_name = owner_name

st.markdown("### Pets")
colp1, colp2 = st.columns([2, 1])
with colp1:
    pet_name = st.text_input("Pet name", value="Mochi")
with colp2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    new_pet = Pet(pet_id=str(uuid4()), name=pet_name, species=species)
    owner.add_pet(new_pet)

if owner.pets:
    pet_options = {f"{p.name} ({p.species})": p.pet_id for p in owner.pets}
    selected_pet_label = st.selectbox("Select pet", list(pet_options.keys()))
    selected_pet_id = pet_options[selected_pet_label]
    selected_pet = next(p for p in owner.pets if p.pet_id == selected_pet_id)
    st.caption(f"Tasks will be added to **{selected_pet.name}**.")
else:
    selected_pet = None
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks; these will be stored on the selected Pet object.")

col1, col2, col3 = st.columns(3)
with col1:
    description = st.text_input("Task description", value="Morning walk")
with col2:
    at_time = st.time_input("Time", value=None)
with col3:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)

if st.button("Add task", disabled=selected_pet is None):
    if at_time is None:
        st.error("Please choose a time for the task.")
    else:
        selected_pet.add_task(Task(description=description, at=at_time, frequency=frequency))

if selected_pet and selected_pet.tasks:
    st.write("Current tasks for selected pet:")
    st.table(
        [
            {
                "time": t.at.strftime("%H:%M"),
                "due": t.due_date.isoformat(),
                "description": t.description,
                "frequency": t.frequency,
                "completed": t.completed,
            }
            for t in sorted(selected_pet.tasks, key=lambda x: (x.due_date, x.at, x.description))
        ]
    )
elif selected_pet:
    st.info("No tasks yet for this pet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button calls your scheduling logic and displays the result (sorted + conflict warnings).")

today = date.today()

pet_filter_name = None
if owner.pets:
    pet_filter_name = st.selectbox("Filter schedule by pet (optional)", ["(all)"] + [p.name for p in owner.pets])
    if pet_filter_name == "(all)":
        pet_filter_name = None

if st.button("Generate schedule"):
    scheduler = Scheduler()

    # Build schedule items so we can optionally filter by pet and still show conflict warnings.
    pairs = scheduler.filter_tasks(owner=owner, day=today, pet_name=pet_filter_name, completed=False)
    schedule_items: list[dict] = []
    for pet, task in pairs:
        schedule_items.append(
            {
                "time": task.at,
                "date": task.due_date,
                "pet_name": pet.name,
                "pet_id": pet.pet_id,
                "species": pet.species,
                "description": task.description,
                "frequency": task.frequency,
                "completed": task.completed,
            }
        )

    schedule_items.sort(key=lambda x: (x["time"], x["pet_name"], x["description"]))
    warnings = scheduler.detect_conflicts(schedule_items)

    st.markdown("#### Today's Schedule")
    st.table(
        [
            {
                "Time": item["time"].strftime("%H:%M"),
                "Pet": item["pet_name"],
                "Task": item["description"],
                "Frequency": item["frequency"],
                "Due": item["date"].isoformat(),
            }
            for item in schedule_items
        ]
    )

    if warnings:
        # Conflict warnings should be visually prominent and list all issues.
        st.warning("Scheduling conflicts detected:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No scheduling conflicts detected.")

st.divider()
st.subheader("Complete a Task (demo)")
st.caption("Marking a daily/weekly task complete will automatically create the next occurrence.")

if selected_pet is None:
    st.info("Add/select a pet above to enable task completion.")
else:
    todays_incomplete = [t for t in selected_pet.tasks if t.due_date == today and not t.completed]
    todays_incomplete.sort(key=lambda t: (t.at, t.description))

    if not todays_incomplete:
        st.info("No incomplete tasks due today for this pet.")
    else:
        # Pick a single task to mark complete (simpler than a button per-row).
        task_labels = [
            f"{t.at.strftime('%H:%M')} - {t.description} ({t.frequency})" for t in todays_incomplete
        ]
        selected_task_label = st.selectbox("Task to mark complete", task_labels)
        selected_task_index = task_labels.index(selected_task_label)
        t = todays_incomplete[selected_task_index]

        if st.button("Mark complete"):
            did_complete = selected_pet.mark_task_complete(description=t.description, at=t.at, day=today)
            if did_complete:
                st.success(f"Marked complete: {t.description} ({t.at.strftime('%H:%M')}). Recurrence, if any, was rolled forward.")
            else:
                st.error("Could not find the selected task (it may have changed).")
