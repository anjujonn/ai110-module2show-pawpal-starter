from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
from enum import Enum

"""
pawpal_system.py — Core data model for the PawPal pet care app.

Classes:
    Priority   - Enum for task urgency: LOW, MEDIUM, HIGH, URGENT
    Frequency  - Enum for how often a task repeats: ONCE, DAILY, WEEKLY, MONTHLY
    Task       - A single care activity with completion status and frequency.
    Pet        - Stores pet details and owns a list of Tasks directly.
    PetOwner   - Manages multiple pets; provides access to all tasks across them.
    Scheduler  - The "brain": retrieves, organizes, and manages tasks across pets.

Relationships:
    PetOwner  1 ──< Pet        (pets_list / add_pet / remove_pet)
    PetOwner  1 ──< Scheduler  (schedules_list)
    Pet       1 ──< Task       (tasks_list / add_task / remove_task)
    Scheduler  ──> PetOwner   (brain that operates on owner's pets and tasks)
    Scheduler  ──> Pet        (can focus on a single pet's tasks)
"""


class Priority(Enum):
    """Urgency levels for a task, from least to most critical."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Frequency(Enum):
    """How often a task repeats. ONCE means it is a one-time event."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Task:
    """
    Represents a single care activity for a pet.

    Attributes:
        name          : Short label for the task (e.g. "Morning walk")
        type_of_task  : Category (e.g. "exercise", "medication", "feeding")
        duration      : How long the task takes, in minutes
        priority      : Urgency level — must be a Priority enum value
        frequency     : How often the task recurs — must be a Frequency enum value
        specific_time : Optional time string (e.g. "08:00") if time-sensitive
        notes         : Any extra directions or context
        completed     : Whether this task has been marked done
    """
    name: str
    type_of_task: str
    duration: int
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE
    specific_time: Optional[str] = None
    notes: str = ""
    completed: bool = False
    due_date: Optional[str] = None   # "YYYY-MM-DD"; set on creation, auto-advanced on complete

    @classmethod
    def create_task(cls, name, type_of_task, duration, priority=Priority.MEDIUM,
                    frequency=Frequency.ONCE, specific_time=None, notes="",
                    due_date=None):
        """Create and return a new Task instance."""
        return cls(name, type_of_task, duration, priority, frequency,
                   specific_time, notes, False, due_date)

    def edit_task(self, **kwargs):
        """Update any Task field by keyword. e.g. task.edit_task(priority=Priority.HIGH)"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self, pet: "Pet" = None):
        """
        Mark this task as done.
        For DAILY tasks  → schedules a new instance due tomorrow (today + 1 day).
        For WEEKLY tasks → schedules a new instance due next week (today + 7 days).
        Pass the owning pet so the new instance can be added to its task list.
        """
        self.completed = True
        if pet is not None and self.frequency in (Frequency.DAILY, Frequency.WEEKLY):
            delta = timedelta(days=1) if self.frequency == Frequency.DAILY else timedelta(weeks=1)
            base = date.fromisoformat(self.due_date) if self.due_date else date.today()
            next_task = Task.create_task(
                name=self.name,
                type_of_task=self.type_of_task,
                duration=self.duration,
                priority=self.priority,
                frequency=self.frequency,
                specific_time=self.specific_time,
                notes=self.notes,
                due_date=(base + delta).isoformat(),
            )
            pet.add_task(next_task)

    def delete_task(self, pet: "Pet"):
        """Remove this task from the given pet's task list."""
        pet.remove_task(self)


@dataclass
class Pet:
    """
    Stores a pet's profile and owns its list of care tasks.

    Attributes:
        name               : Pet's name
        animal_type        : Species/breed (e.g. "dog", "cat")
        age                : Age in years
        gender             : Gender of the pet
        allergies          : Known allergies, if any
        medical_background : Medical history or conditions
        notes              : Any other relevant notes
        tasks_list         : All tasks assigned to this pet
    """
    name: str
    animal_type: str
    age: int
    gender: str
    allergies: str = ""
    medical_background: str = ""
    notes: str = ""
    tasks_list: list = field(default_factory=list)

    @classmethod
    def create(cls, name, animal_type, age, gender, allergies="", medical_background="", notes=""):
        """Create and return a new Pet instance."""
        return cls(name, animal_type, age, gender, allergies, medical_background, notes)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks_list.append(task)

    def remove_task(self, task: Task):
        """Remove a task from this pet's task list."""
        if task in self.tasks_list:
            self.tasks_list.remove(task)

    def get_pending_tasks(self) -> list:
        """Return all tasks that have not been completed yet."""
        return [t for t in self.tasks_list if not t.completed]

    def get_completed_tasks(self) -> list:
        """Return all tasks that have been marked complete."""
        return [t for t in self.tasks_list if t.completed]

    def delete_pet(self, owner: "PetOwner"):
        """Remove this pet from the given owner's pets list."""
        owner.remove_pet(self)


class PetOwner:
    """
    Manages multiple pets and provides a unified view of all their tasks.

    Attributes:
        name           : Owner's full name
        address        : Owner's home address
        phone_number   : Owner's contact number
        pets_list      : All pets belonging to this owner
        schedules_list : All Scheduler sessions created for this owner
    """

    def __init__(self):
        """Initialise a blank PetOwner. Use create_owner_profile() to build one with data."""
        self.name: str = ""
        self.address: str = ""
        self.phone_number: str = ""
        self.pets_list: list[Pet] = []
        self.schedules_list: list["Scheduler"] = []

    @classmethod
    def create_owner_profile(cls, name, address, phone_number):
        """Create and return a new PetOwner instance."""
        owner = cls()
        owner.name = name
        owner.address = address
        owner.phone_number = phone_number
        return owner

    def add_pet(self, pet: Pet):
        """Register a pet under this owner."""
        self.pets_list.append(pet)

    def remove_pet(self, pet: Pet):
        """Remove a pet from this owner's list."""
        if pet in self.pets_list:
            self.pets_list.remove(pet)

    def get_all_tasks(self) -> list:
        """Return every task across all of this owner's pets."""
        all_tasks = []
        for pet in self.pets_list:
            all_tasks.extend(pet.tasks_list)
        return all_tasks

    def get_all_pending_tasks(self) -> list:
        """Return all incomplete tasks across all pets."""
        return [t for t in self.get_all_tasks() if not t.completed]


class Scheduler:
    """
    The 'brain' of PawPal. Retrieves, organizes, and manages tasks
    across all pets for a given owner.

    Can operate on a single pet's tasks or across all pets at once.

    Attributes:
        status            : Current state of the schedule (e.g. "active", "complete")
        pet_owner         : The owner this scheduler belongs to
        pet               : The specific pet currently in focus (optional)
        actual_duration   : How long the session actually took, in minutes
        additional_notes  : Extra context for the session
        extra_items       : Items needed or provided during the session
    """

    def __init__(self):
        """Initialise a blank Scheduler. Use create_schedule() to build one with data."""
        self.status: str = ""
        self.pet_owner: Optional[PetOwner] = None
        self.pet: Optional[Pet] = None
        self.actual_duration: int = 0
        self.additional_notes: str = ""
        self.extra_items: str = ""

    @property
    def tasks_list(self) -> list:
        """Live view of the focused pet's tasks. Always up to date."""
        if self.pet:
            return self.pet.tasks_list
        return []

    @property
    def estimated_duration(self) -> int:
        """Auto-computed from the focused pet's task durations. Never drifts."""
        return sum(task.duration for task in self.tasks_list)

    @classmethod
    def create_schedule(cls, pet_owner: PetOwner, pet: Pet, status="",
                        additional_notes="", extra_items=""):
        """
        Create a new Scheduler session for a specific pet.
        Raises ValueError if the pet doesn't belong to the given owner.
        Automatically registers itself on the owner's schedules_list.
        """
        if pet not in pet_owner.pets_list:
            raise ValueError(f"{pet.name} does not belong to {pet_owner.name}")
        scheduler = cls()
        scheduler.pet_owner = pet_owner
        scheduler.pet = pet
        scheduler.status = status
        scheduler.additional_notes = additional_notes
        scheduler.extra_items = extra_items
        pet_owner.schedules_list.append(scheduler)
        return scheduler

    def get_pending_tasks(self) -> list:
        """Return all incomplete tasks for the focused pet."""
        return [t for t in self.tasks_list if not t.completed]

    def get_tasks_by_priority(self, priority: Priority) -> list:
        """Return tasks for the focused pet filtered by priority level."""
        return [t for t in self.tasks_list if t.priority == priority]

    def get_tasks_by_frequency(self, frequency: Frequency) -> list:
        """Return tasks for the focused pet filtered by frequency."""
        return [t for t in self.tasks_list if t.frequency == frequency]

    def get_all_tasks_across_pets(self) -> list:
        """Return every task across all of the owner's pets."""
        if self.pet_owner:
            return self.pet_owner.get_all_tasks()
        return []

    def get_urgent_tasks_across_pets(self) -> list:
        """Return all URGENT tasks across every pet the owner has."""
        return [t for t in self.get_all_tasks_across_pets()
                if t.priority == Priority.URGENT]

    def get_pending_tasks_across_pets(self) -> list:
        """Return all incomplete tasks across every pet the owner has."""
        return [t for t in self.get_all_tasks_across_pets() if not t.completed]

    def sort_by_time(self) -> list:
        """
        Return all tasks across the owner's pets sorted by specific_time (HH:MM).
        Tasks without a specific_time are placed at the end.
        Uses a lambda as the sort key so strings like '08:00' sort lexicographically,
        which works correctly for zero-padded HH:MM format.
        """
        return sorted(
            self.get_all_tasks_across_pets(),
            key=lambda t: t.specific_time if t.specific_time else "99:99"
        )

    def filter_tasks(self, completed=None, pet_name=None) -> list:
        """
        Filter tasks by completion status and/or pet name.

        completed : True  → completed tasks only
                    False → pending tasks only
                    None  → all tasks regardless of status
        pet_name  : name of a specific pet to restrict results to;
                    None means include all pets
        """
        if pet_name is not None:
            target = next(
                (p for p in self.pet_owner.pets_list if p.name == pet_name),
                None
            ) if self.pet_owner else None
            tasks = target.tasks_list if target else []
        else:
            tasks = self.get_all_tasks_across_pets()

        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]

        return tasks

    # ── conflict detection ────────────────────────────────────────────────────

    @staticmethod
    def _parse_time(time_str) -> Optional[int]:
        """Convert 'HH:MM' to minutes since midnight. Returns None if missing or invalid."""
        if not time_str:
            return None
        try:
            h, m = time_str.strip().split(":")
            return int(h) * 60 + int(m)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _mins_to_str(mins: int) -> str:
        """Convert minutes since midnight back to 'HH:MM'."""
        return f"{mins // 60:02d}:{mins % 60:02d}"

    def detect_conflicts(self) -> list:
        """
        Scan all pending, timed tasks across every pet for overlapping windows.

        Two tasks conflict when their time windows overlap:
            start_A < end_B  AND  start_B < end_A

        Strategy is lightweight — returns a list of human-readable warning
        strings instead of raising exceptions. An empty list means no conflicts.
        Works across same-pet and different-pet task pairs.
        """
        # Build (task, pet, start_mins) for every pending task that has a time
        timed = []
        pets = self.pet_owner.pets_list if self.pet_owner else []
        for pet in pets:
            for task in pet.tasks_list:
                if task.completed:
                    continue
                start = self._parse_time(task.specific_time)
                if start is not None:
                    timed.append((task, pet, start))

        warnings = []
        for i, (task_a, pet_a, start_a) in enumerate(timed):
            end_a = start_a + task_a.duration
            for j, (task_b, pet_b, start_b) in enumerate(timed):
                if j <= i:          # avoid duplicates and self-comparison
                    continue
                end_b = start_b + task_b.duration
                if start_a < end_b and start_b < end_a:
                    same = "same pet" if pet_a is pet_b else f"{pet_a.name} & {pet_b.name}"
                    warnings.append(
                        f"WARNING: '{task_a.name}' ({pet_a.name}, "
                        f"{task_a.specific_time}-{self._mins_to_str(end_a)}) "
                        f"overlaps with '{task_b.name}' ({pet_b.name}, "
                        f"{task_b.specific_time}-{self._mins_to_str(end_b)}) "
                        f"[{same}]"
                    )

        return warnings
