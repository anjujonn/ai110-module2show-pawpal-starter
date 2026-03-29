from pawpal_system import PetOwner, Pet, Task, Scheduler, Priority, Frequency

# --- Setup Owner ---
owner = PetOwner.create_owner_profile(
    name="Maria Lopez",
    address="123 Maple Street",
    phone_number="555-0192"
)

# --- Create Pets ---
buddy = Pet.create(
    name="Buddy",
    animal_type="Dog",
    age=3,
    gender="Male",
    allergies="Chicken",
    medical_background="Vaccinated, neutered",
    notes="Loves fetch, gets anxious during thunderstorms"
)

luna = Pet.create(
    name="Luna",
    animal_type="Cat",
    age=5,
    gender="Female",
    allergies="None",
    medical_background="Vaccinated, spayed",
    notes="Indoor only, shy around strangers"
)

owner.add_pet(buddy)
owner.add_pet(luna)

# --- Create Tasks for Buddy ---
morning_walk = Task.create_task(
    name="Morning Walk",
    type_of_task="Exercise",
    duration=30,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    specific_time="07:00",
    notes="At least 2 laps around the block"
)

medication = Task.create_task(
    name="Allergy Medication",
    type_of_task="Medical",
    duration=5,
    priority=Priority.URGENT,
    frequency=Frequency.DAILY,
    specific_time="08:00",
    notes="Half tablet mixed into food"
)

# --- Create Tasks for Luna ---
feeding = Task.create_task(
    name="Feeding",
    type_of_task="Feeding",
    duration=10,
    priority=Priority.HIGH,
    frequency=Frequency.DAILY,
    specific_time="08:30",
    notes="1/4 cup dry food, fresh water"
)

vet_checkup = Task.create_task(
    name="Vet Checkup",
    type_of_task="Medical",
    duration=60,
    priority=Priority.MEDIUM,
    frequency=Frequency.ONCE,
    specific_time="14:00",
    notes="Annual wellness exam — bring vaccine records"
)

evening_play = Task.create_task(
    name="Evening Playtime",
    type_of_task="Exercise",
    duration=20,
    priority=Priority.LOW,
    frequency=Frequency.DAILY,
    specific_time="18:00",
    notes="Feather wand or laser pointer"
)

buddy.add_task(morning_walk)
buddy.add_task(medication)
luna.add_task(feeding)
luna.add_task(vet_checkup)
luna.add_task(evening_play)

# --- Create Scheduler ---
scheduler = Scheduler.create_schedule(
    pet_owner=owner,
    pet=buddy,
    status="Active",
    additional_notes="Check buddy's paws after the walk",
    extra_items="Leash, poop bags, medication"
)

# --- Print Today's Schedule ---
all_tasks = owner.get_all_tasks()
all_tasks_sorted = sorted(all_tasks, key=lambda t: t.specific_time or "99:99")

print("=" * 45)
print(f"  TODAY'S SCHEDULE — {owner.name}")
print("=" * 45)

for pet in owner.pets_list:
    print(f"\n  {pet.name} ({pet.animal_type}, Age {pet.age})")
    print(f"  {'-' * 38}")
    if not pet.tasks_list:
        print("    No tasks scheduled.")
    for task in sorted(pet.tasks_list, key=lambda t: t.specific_time or "99:99"):
        status = "[x]" if task.completed else "[ ]"
        time_label = task.specific_time if task.specific_time else "Anytime"
        print(f"  {status} [{time_label}]  {task.name}")
        print(f"      Type: {task.type_of_task}  |  Duration: {task.duration} min  |  Priority: {task.priority.value.upper()}")
        if task.notes:
            print(f"      Notes: {task.notes}")

print(f"\n{'-' * 45}")
print(f"  Total tasks today : {len(all_tasks)}")
print(f"  Estimated time    : {sum(t.duration for t in all_tasks)} min")
print(f"  Urgent tasks      : {len(scheduler.get_urgent_tasks_across_pets())}")
print("=" * 45)
