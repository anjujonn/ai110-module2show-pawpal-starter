from datetime import date
from pawpal_system import PetOwner, Pet, Task, Scheduler, Priority, Frequency

today = date.today().isoformat()

# -- helpers ------------------------------------------------------------------
def print_tasks(tasks, label):
    """Print a labelled, formatted list of Task objects to the terminal.

    tasks : list of Task objects to display
    label : heading string printed above the task rows
    Each row shows completion status, scheduled time, due date, task name,
    priority, and frequency. Prints '(none)' if the list is empty.
    """
    print(f"\n  {label}")
    print(f"  {'-' * 54}")
    if not tasks:
        print("    (none)")
        return
    for t in tasks:
        status     = "[x]" if t.completed else "[ ]"
        time_label = t.specific_time if t.specific_time else "Anytime"
        due_label  = f"  due {t.due_date}" if t.due_date else ""
        print(f"  {status} [{time_label}]{due_label}  {t.name}"
              f"  |  {t.priority.value.upper()}  |  {t.frequency.value}")

# -- owner & pets -------------------------------------------------------------
owner = PetOwner.create_owner_profile(
    name="Maria Lopez", address="123 Maple Street", phone_number="555-0192"
)
buddy = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
luna  = Pet.create(name="Luna",  animal_type="Cat", age=5, gender="Female")
owner.add_pet(buddy)
owner.add_pet(luna)

# -- tasks added OUT OF ORDER (to confirm sort_by_time works) -----------------
# Buddy  (added: 18:00 -> 07:00 -> no-time -> 08:00)
evening_walk = Task.create_task(
    name="Evening Walk",       type_of_task="Exercise",
    duration=25,               priority=Priority.MEDIUM,
    frequency=Frequency.DAILY, specific_time="18:00",
    due_date=today,
)
morning_walk = Task.create_task(
    name="Morning Walk",       type_of_task="Exercise",
    duration=30,               priority=Priority.HIGH,
    frequency=Frequency.DAILY, specific_time="07:00",
    notes="2 laps around the block",
    due_date=today,
)
grooming = Task.create_task(
    name="Grooming",           type_of_task="Hygiene",
    duration=40,               priority=Priority.LOW,
    frequency=Frequency.WEEKLY, specific_time=None,
    notes="Brush coat and trim nails",
    due_date=today,
)
medication = Task.create_task(
    name="Allergy Medication", type_of_task="Medical",
    duration=5,                priority=Priority.URGENT,
    frequency=Frequency.DAILY, specific_time="08:00",
    notes="Half tablet mixed into food",
    due_date=today,
)
buddy.add_task(evening_walk)   # 18:00  <- out of order
buddy.add_task(morning_walk)   # 07:00
buddy.add_task(grooming)       # Anytime
buddy.add_task(medication)     # 08:00

# Luna  (added: 14:00 -> 08:30 -> no-time)
vet_checkup = Task.create_task(
    name="Vet Checkup",        type_of_task="Medical",
    duration=60,               priority=Priority.MEDIUM,
    frequency=Frequency.ONCE,  specific_time="14:00",
    notes="Annual wellness exam",
    due_date=today,
)
feeding = Task.create_task(
    name="Feeding",            type_of_task="Feeding",
    duration=10,               priority=Priority.HIGH,
    frequency=Frequency.DAILY, specific_time="08:30",
    notes="1/4 cup dry food, fresh water",
    due_date=today,
)
playtime = Task.create_task(
    name="Playtime",           type_of_task="Exercise",
    duration=20,               priority=Priority.LOW,
    frequency=Frequency.WEEKLY, specific_time=None,
    due_date=today,
)
luna.add_task(vet_checkup)     # 14:00  <- out of order
luna.add_task(feeding)         # 08:30
luna.add_task(playtime)        # Anytime

# -- INTENTIONAL CONFLICTS for detect_conflicts() demo -----------------------
# Conflict 1 (same pet): Buddy has Morning Walk 07:00-07:30.
#   "Pre-walk Stretch" starts at 07:15 and runs 20 min (07:15-07:35) — overlaps.
pre_walk_stretch = Task.create_task(
    name="Pre-walk Stretch",   type_of_task="Exercise",
    duration=20,               priority=Priority.LOW,
    frequency=Frequency.DAILY, specific_time="07:15",
    due_date=today,
)
buddy.add_task(pre_walk_stretch)

# Conflict 2 (different pets): Luna's Feeding is 08:30-08:40.
#   "Buddy Breakfast" starts at 08:25 and runs 20 min (08:25-08:45) — overlaps.
buddy_breakfast = Task.create_task(
    name="Buddy Breakfast",    type_of_task="Feeding",
    duration=20,               priority=Priority.HIGH,
    frequency=Frequency.DAILY, specific_time="08:25",
    due_date=today,
)
buddy.add_task(buddy_breakfast)

# -- scheduler ----------------------------------------------------------------
scheduler = Scheduler.create_schedule(
    pet_owner=owner, pet=buddy, status="Active",
    additional_notes="Check Buddy's paws after morning walk",
)

# =============================================================================
print("\n" + "=" * 56)
print("  BEFORE: tasks added out of order")
print("=" * 56)
print_tasks(buddy.tasks_list, "Buddy  (insertion order)")
print_tasks(luna.tasks_list,  "Luna   (insertion order)")

print("\n" + "=" * 56)
print("  sort_by_time()  -- all pets, sorted by HH:MM")
print("=" * 56)
print_tasks(scheduler.sort_by_time(), "All tasks sorted by time")

# =============================================================================
print("\n" + "=" * 56)
print("  filter_tasks() demos")
print("=" * 56)
print_tasks(scheduler.filter_tasks(completed=False),            "Pending  (all pets)")
print_tasks(scheduler.filter_tasks(pet_name="Buddy"),           "All tasks -- Buddy only")
print_tasks(scheduler.filter_tasks(completed=False, pet_name="Luna"), "Pending -- Luna only")

# =============================================================================
print("\n" + "=" * 56)
print("  mark_complete(pet=...)  -- auto-schedule next occurrence")
print("=" * 56)

print(f"\n  Completing 'Morning Walk' (daily, due {morning_walk.due_date}) ...")
morning_walk.mark_complete(pet=buddy)

print(f"  Completing 'Feeding'      (daily, due {feeding.due_date}) ...")
feeding.mark_complete(pet=luna)

print(f"  Completing 'Grooming'     (weekly, due {grooming.due_date}) ...")
grooming.mark_complete(pet=buddy)

print(f"  Completing 'Vet Checkup'  (once -- no new instance expected) ...")
vet_checkup.mark_complete(pet=luna)

print("\n  --- Buddy's tasks after completing Morning Walk + Grooming ---")
print_tasks(buddy.tasks_list, "Buddy (completed tasks + new next-occurrence tasks)")

print("\n  --- Luna's tasks after completing Feeding + Vet Checkup ---")
print_tasks(luna.tasks_list, "Luna  (completed tasks + new next-occurrence tasks)")

# =============================================================================
print("\n" + "=" * 56)
print("  detect_conflicts()  -- lightweight conflict detection")
print("=" * 56)

print("\n  Checking for scheduling conflicts across all pets ...")
conflicts = scheduler.detect_conflicts()

if not conflicts:
    print("\n  No conflicts found.")
else:
    print(f"\n  {len(conflicts)} conflict(s) detected:\n")
    for warning in conflicts:
        print(f"  {warning}")

# summary
all_tasks = owner.get_all_tasks()
print(f"\n{'=' * 56}")
print(f"  Total tasks (incl. new occurrences) : {len(all_tasks)}")
print(f"  Pending                             : {len(scheduler.filter_tasks(completed=False))}")
print(f"  Completed                           : {len(scheduler.filter_tasks(completed=True))}")
print("=" * 56 + "\n")
