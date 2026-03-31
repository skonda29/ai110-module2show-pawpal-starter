"""PawPal+ backend logic layer.

This module defines the core objects used by the app's scheduling logic.
It is designed to be usable from both a CLI script (for early verification)
and the Streamlit UI in `app.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Iterable, List, Optional


@dataclass
class Task:
    """Represents a single care activity that can be scheduled."""

    description: str
    at: time
    due_date: date = field(default_factory=date.today)
    frequency: str = "once"  # e.g., "once", "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next recurring instance (if any)."""

        self.completed = True
        return self._next_recurring_instance()

    def _next_recurring_instance(self) -> Optional["Task"]:
        """Create the next task instance for recurring tasks."""

        freq = self.frequency.strip().lower()
        if freq == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif freq == "weekly":
            next_date = self.due_date + timedelta(days=7)
        else:
            return None

        return Task(
            description=self.description,
            at=self.at,
            due_date=next_date,
            frequency=self.frequency,
            completed=False,
        )


@dataclass
class Pet:
    """Stores pet details and a list of tasks."""

    pet_id: str
    name: str
    species: str

    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a new task to this pet."""

        self.tasks.append(task)

    def tasks_for_day(self, day: date) -> List[Task]:
        """Return tasks that are due on the given day."""

        return [t for t in self.tasks if t.due_date == day]

    def mark_task_complete(
        self,
        *,
        description: str,
        at: time,
        day: date,
    ) -> bool:
        """Mark a matching task complete; auto-create next instance if recurring."""

        for task in self.tasks:
            if task.description == description and task.at == at and task.due_date == day:
                next_task = task.mark_complete()
                if next_task is not None:
                    self.add_task(next_task)
                return True
        return False

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""

        self.tasks.remove(task)


@dataclass
class Owner:
    """Manages multiple pets and provides access to their tasks."""

    owner_name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""

        self.pets.append(pet)

    def all_tasks(self) -> List[tuple[Pet, Task]]:
        """Return all tasks across all pets as (pet, task) pairs."""

        pairs: List[tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                pairs.append((pet, task))
        return pairs

    def find_pet_by_name(self, name: str) -> Optional[Pet]:
        """Find the first pet with the given name (case-insensitive)."""

        needle = name.strip().lower()
        for pet in self.pets:
            if pet.name.strip().lower() == needle:
                return pet
        return None


class Scheduler:
    """The “brain” that retrieves, organizes, and manages tasks across pets."""

    def sort_by_time(self, tasks: Iterable[Task]) -> List[Task]:
        """Return tasks sorted by their `at` time (then description)."""

        return sorted(tasks, key=lambda t: (t.at, t.description))

    def filter_tasks(
        self,
        *,
        owner: Owner,
        day: Optional[date] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[tuple[Pet, Task]]:
        """Filter tasks by day, pet name, and/or completion status."""

        pairs = owner.all_tasks()

        if day is not None:
            pairs = [(p, t) for (p, t) in pairs if t.due_date == day]

        if pet_name is not None:
            needle = pet_name.strip().lower()
            pairs = [(p, t) for (p, t) in pairs if p.name.strip().lower() == needle]

        if completed is not None:
            pairs = [(p, t) for (p, t) in pairs if t.completed == completed]

        return pairs

    def build_schedule(
        self,
        *,
        owner: Owner,
        day: Optional[date] = None,
    ) -> tuple[List[dict], List[str]]:
        """Build a schedule plus lightweight conflict warnings."""

        if day is None:
            day = date.today()

        items: List[dict] = []
        for pet, task in self.filter_tasks(owner=owner, day=day, completed=False):
            if task.completed:
                continue
            items.append(
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

        items.sort(key=lambda x: (x["time"], x["pet_name"], x["description"]))
        warnings = self.detect_conflicts(items)
        return items, warnings

    def todays_schedule(self, *, owner: Owner, day: Optional[date] = None) -> List[dict]:
        """Build a day’s schedule as a sorted list of lightweight dicts."""

        schedule, _warnings = self.build_schedule(owner=owner, day=day)
        return schedule

    def detect_conflicts(self, schedule: Iterable[dict]) -> List[str]:
        """Detect exact-time conflicts and return warning strings."""

        by_time: dict[tuple[date, time], List[dict]] = {}
        for item in schedule:
            key = (item.get("date"), item["time"])
            by_time.setdefault(key, []).append(item)

        warnings: List[str] = []
        for (d, t), items in sorted(by_time.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            if len(items) <= 1:
                continue

            pets = sorted({it["pet_name"] for it in items})
            if len(pets) == 1:
                warnings.append(
                    f"Conflict at {t.strftime('%H:%M')} for {pets[0]}: multiple tasks scheduled."
                )
            else:
                warnings.append(
                    f"Conflict at {t.strftime('%H:%M')}: tasks scheduled at the same time for {', '.join(pets)}."
                )
        return warnings

    def format_schedule(self, schedule: Iterable[dict]) -> str:
        """Format a schedule into a readable multi-line string."""

        lines: List[str] = []
        for item in schedule:
            t: time = item["time"]
            lines.append(f"{t.strftime('%H:%M')}  {item['pet_name']}: {item['description']}")
        return "\n".join(lines) if lines else "(no tasks scheduled)"

