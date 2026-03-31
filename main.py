from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(owner_name="Jordan")

    mochi = Pet(pet_id="pet-1", name="Mochi", species="dog")
    luna = Pet(pet_id="pet-2", name="Luna", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task(description="Morning walk", at=time(8, 0), frequency="daily"))
    mochi.add_task(Task(description="Dinner", at=time(18, 30), frequency="daily"))
    luna.add_task(Task(description="Meds", at=time(9, 15), frequency="daily"))

    scheduler = Scheduler()
    schedule = scheduler.todays_schedule(owner=owner, day=date.today())

    print("Today's Schedule")
    print("-" * 16)
    print(scheduler.format_schedule(schedule))


if __name__ == "__main__":
    main()

