from dataclasses import dataclass, field
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
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Frequency(Enum):
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

    @classmethod
    def create_task(cls, name, type_of_task, duration, priority=Priority.MEDIUM,
                    frequency=Frequency.ONCE, specific_time=None, notes=""):
        """Create and return a new Task instance."""
        return cls(name, type_of_task, duration, priority, frequency, specific_time, notes)

    def edit_task(self, **kwargs):
        """Update any Task field by keyword. e.g. task.edit_task(priority=Priority.HIGH)"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

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
