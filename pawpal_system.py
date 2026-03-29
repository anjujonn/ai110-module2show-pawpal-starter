from dataclasses import dataclass
from typing import Optional


@dataclass
class Pet:
    name: str
    animal_type: str
    age: int
    gender: str
    allergies: str = ""
    medical_background: str = ""
    notes: str = ""

    @classmethod
    def create(cls, name, animal_type, age, gender, allergies="", medical_background="", notes=""):
        return cls(name, animal_type, age, gender, allergies, medical_background, notes)

    def delete_pet(self):
        pass


@dataclass
class Task:
    name: str
    type_of_task: str
    duration: int
    priority: str
    specific_time: Optional[str] = None
    notes: str = ""

    @classmethod
    def create_task(cls, name, type_of_task, duration, priority, specific_time=None, notes=""):
        return cls(name, type_of_task, duration, priority, specific_time, notes)

    def edit_task(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def delete_task(self):
        pass


class PetOwner:
    def __init__(self):
        self.name: str = ""
        self.address: str = ""
        self.phone_number: str = ""
        self.pets_list: list[Pet] = []

    @classmethod
    def create_owner_profile(cls, name, address, phone_number):
        owner = cls()
        owner.name = name
        owner.address = address
        owner.phone_number = phone_number
        return owner


class Schedule:
    def __init__(self):
        self.status: str = ""
        self.tasks_list: list[Task] = []
        self.pet_owner: Optional[PetOwner] = None
        self.pet: Optional[Pet] = None
        self.estimated_duration: int = 0
        self.actual_duration: int = 0
        self.additional_notes: str = ""
        self.extra_items: str = ""

    @classmethod
    def create_schedule(cls, pet_owner, pet, status="", estimated_duration=0, additional_notes="", extra_items=""):
        schedule = cls()
        schedule.pet_owner = pet_owner
        schedule.pet = pet
        schedule.status = status
        schedule.estimated_duration = estimated_duration
        schedule.additional_notes = additional_notes
        schedule.extra_items = extra_items
        return schedule
