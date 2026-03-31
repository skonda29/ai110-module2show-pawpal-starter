from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_mark_complete_sets_completed_true() -> None:
    task = Task(description="Test task", at=time(10, 0))
    assert task.completed is False
    next_task = task.mark_complete()
    assert task.completed is True
    assert next_task is None


def test_pet_add_task_increases_task_count() -> None:
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    start_count = len(pet.tasks)
    pet.add_task(Task(description="Walk", at=time(8, 0)))
    assert len(pet.tasks) == start_count + 1


def test_daily_task_completion_creates_next_day_task() -> None:
    today = date.today()
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    pet.add_task(Task(description="Morning walk", at=time(8, 0), due_date=today, frequency="daily"))

    did_complete = pet.mark_task_complete(description="Morning walk", at=time(8, 0), day=today)

    assert did_complete is True
    tomorrow = today + timedelta(days=1)
    tomorrow_tasks = pet.tasks_for_day(tomorrow)
    assert len(tomorrow_tasks) == 1
    assert tomorrow_tasks[0].description == "Morning walk"
    assert tomorrow_tasks[0].completed is False


def test_detect_conflicts_warns_for_same_time() -> None:
    owner = Owner(owner_name="Jordan")
    mochi = Pet(pet_id="p1", name="Mochi", species="dog")
    luna = Pet(pet_id="p2", name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    today = date.today()

    mochi.add_task(Task(description="Walk", at=time(8, 0), due_date=today))
    luna.add_task(Task(description="Meds", at=time(8, 0), due_date=today))

    schedule, warnings = Scheduler().build_schedule(owner=owner, day=today)

    assert len(schedule) == 2
    assert any("Conflict at 08:00" in warning for warning in warnings)


def test_sorting_correctness_chronological() -> None:
    today = date.today()
    scheduler = Scheduler()

    tasks = [
        Task(description="B", at=time(9, 0), due_date=today),
        Task(description="A", at=time(8, 30), due_date=today),
        Task(description="C", at=time(9, 0), due_date=today),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)
    assert [t.description for t in sorted_tasks] == ["A", "B", "C"]


def test_no_tasks_returns_empty_schedule_and_no_warnings() -> None:
    owner = Owner(owner_name="Jordan")
    owner.add_pet(Pet(pet_id="p1", name="Mochi", species="dog"))
    scheduler = Scheduler()
    schedule, warnings = scheduler.build_schedule(owner=owner, day=date.today())

    assert schedule == []
    assert warnings == []

