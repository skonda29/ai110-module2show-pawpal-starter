"""PawPal+ backend logic layer.

This module defines the core objects used by the app's scheduling logic.
It is designed to be usable from both a CLI script (for early verification)
and the Streamlit UI in `app.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Iterable, List, Optional


@dataclass
class Task:
    """Represents a single care activity that can be scheduled."""

    description: str
    at: time
    frequency: str = "once"  # e.g., "once", "daily", "weekly"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""

        self.completed = True


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


class Scheduler:
    """The “brain” that retrieves, organizes, and manages tasks across pets."""

    def todays_schedule(self, *, owner: Owner, day: Optional[date] = None) -> List[dict]:
        """Build today's schedule as a sorted list of lightweight dicts."""

        _ = day  # reserved for future date-aware rules (frequency, etc.)
        items: List[dict] = []
        for pet, task in owner.all_tasks():
            if task.completed:
                continue
            items.append(
                {
                    "time": task.at,
                    "pet_name": pet.name,
                    "pet_id": pet.pet_id,
                    "species": pet.species,
                    "description": task.description,
                    "frequency": task.frequency,
                    "completed": task.completed,
                }
            )

        items.sort(key=lambda x: (x["time"], x["pet_name"], x["description"]))
        return items

    def format_schedule(self, schedule: Iterable[dict]) -> str:
        """Format a schedule into a readable multi-line string."""

        lines: List[str] = []
        for item in schedule:
            t: time = item["time"]
            lines.append(f"{t.strftime('%H:%M')}  {item['pet_name']}: {item['description']}")
        return "\n".join(lines) if lines else "(no tasks scheduled)"

