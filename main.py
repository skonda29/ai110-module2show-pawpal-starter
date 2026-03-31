from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(owner_name="Jordan")

    mochi = Pet(pet_id="pet-1", name="Mochi", species="dog")
    luna = Pet(pet_id="pet-2", name="Luna", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()

    # Add tasks out-of-order on purpose (to demonstrate sorting).
    mochi.add_task(Task(description="Dinner", at=time(18, 30), due_date=today, frequency="daily"))
    luna.add_task(Task(description="Meds", at=time(9, 15), due_date=today, frequency="daily"))
    mochi.add_task(Task(description="Morning walk", at=time(8, 0), due_date=today, frequency="daily"))

    # Add an intentional conflict (same time as Mochi's walk).
    luna.add_task(Task(description="Play time", at=time(8, 0), due_date=today, frequency="once"))

    scheduler = Scheduler()
    schedule, warnings = scheduler.build_schedule(owner=owner, day=today)

    print("Today's Schedule")
    print("-" * 16)
    print(scheduler.format_schedule(schedule))
    if warnings:
        print("\nWarnings")
        print("-" * 8)
        for w in warnings:
            print(f"- {w}")

    # Filtering demo: only Mochi's incomplete tasks today.
    print("\nFiltered (Mochi, incomplete)")
    print("-" * 26)
    mochi_pairs = scheduler.filter_tasks(owner=owner, day=today, pet_name="Mochi", completed=False)
    mochi_only_schedule = [
        {
            "time": t.at,
            "date": t.due_date,
            "pet_name": p.name,
            "pet_id": p.pet_id,
            "species": p.species,
            "description": t.description,
            "frequency": t.frequency,
            "completed": t.completed,
        }
        for (p, t) in mochi_pairs
    ]
    mochi_only_schedule.sort(key=lambda x: (x["time"], x["description"]))
    print(scheduler.format_schedule(mochi_only_schedule))

    # Recurring demo: complete Mochi's morning walk and show the next instance created.
    print("\nRecurring demo")
    print("-" * 14)
    did_complete = mochi.mark_task_complete(description="Morning walk", at=time(8, 0), day=today)
    print(f"Marked complete? {did_complete}")
    tomorrow = today + timedelta(days=1)
    tomorrow_pairs = scheduler.filter_tasks(owner=owner, day=tomorrow, pet_name="Mochi", completed=False)
    if tomorrow_pairs:
        print("Tomorrow's newly generated tasks for Mochi:")
        for t in scheduler.sort_by_time([t for (_p, t) in tomorrow_pairs]):
            print(f"- {t.due_date.isoformat()} {t.at.strftime('%H:%M')} {t.description} ({t.frequency})")
    else:
        print("No recurring tasks were generated for tomorrow.")


if __name__ == "__main__":
    main()

