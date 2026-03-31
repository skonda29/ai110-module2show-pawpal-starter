from datetime import time

from pawpal_system import Pet, Task


def test_task_mark_complete_sets_completed_true() -> None:
    task = Task(description="Test task", at=time(10, 0))
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_pet_add_task_increases_task_count() -> None:
    pet = Pet(pet_id="p1", name="Mochi", species="dog")
    start_count = len(pet.tasks)
    pet.add_task(Task(description="Walk", at=time(8, 0)))
    assert len(pet.tasks) == start_count + 1

