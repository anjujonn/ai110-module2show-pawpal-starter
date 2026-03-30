import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, timedelta
from pawpal_system import Pet, Task, PetOwner, Scheduler, Priority, Frequency


# ── helper ────────────────────────────────────────────────────────────────────

def make_owner_with_pets(*pets):
    """Create a PetOwner and register every pet passed in."""
    owner = PetOwner.create_owner_profile(
        name="Test Owner", address="1 Test Lane", phone_number="000-0000"
    )
    for pet in pets:
        owner.add_pet(pet)
    return owner


# ── existing tests (unchanged) ────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task.create_task(
        name="Morning Walk",
        type_of_task="Exercise",
        duration=30
    )

    assert task.completed == False, "Task should start as not completed"

    task.mark_complete()

    assert task.completed == True, "Task should be completed after calling mark_complete()"
    print("PASS: mark_complete() correctly changes task status to True")


def test_add_task_increases_pet_task_count():
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")

    assert len(pet.tasks_list) == 0, "Pet should start with no tasks"

    task1 = Task.create_task(name="Feeding",    type_of_task="Feeding",  duration=10)
    task2 = Task.create_task(name="Walk",       type_of_task="Exercise", duration=20)
    task3 = Task.create_task(name="Medication", type_of_task="Medical",  duration=5)

    pet.add_task(task1)
    assert len(pet.tasks_list) == 1, "Task count should be 1 after adding first task"

    pet.add_task(task2)
    assert len(pet.tasks_list) == 2, "Task count should be 2 after adding second task"

    pet.add_task(task3)
    assert len(pet.tasks_list) == 3, "Task count should be 3 after adding third task"

    print("PASS: add_task() correctly increases pet task count")


# ── sorting tests ─────────────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order must come back sorted earliest → latest."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    pet.add_task(Task.create_task(name="Evening Walk",  type_of_task="Exercise",
                                   duration=25, specific_time="18:00"))
    pet.add_task(Task.create_task(name="Morning Walk",  type_of_task="Exercise",
                                   duration=30, specific_time="07:00"))
    pet.add_task(Task.create_task(name="Medication",    type_of_task="Medical",
                                   duration=5,  specific_time="08:00"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    times = [t.specific_time for t in scheduler.sort_by_time()]

    assert times == ["07:00", "08:00", "18:00"], (
        f"Expected ['07:00', '08:00', '18:00'] but got {times}"
    )
    print("PASS: sort_by_time() returns tasks in chronological HH:MM order")


def test_sort_by_time_anytime_tasks_go_to_end():
    """Tasks with no specific_time must appear after all timed tasks."""
    pet = Pet.create(name="Luna", animal_type="Cat", age=5, gender="Female")
    owner = make_owner_with_pets(pet)

    pet.add_task(Task.create_task(name="Grooming",    type_of_task="Hygiene",
                                   duration=40, specific_time=None))   # inserted first
    pet.add_task(Task.create_task(name="Morning Feed", type_of_task="Feeding",
                                   duration=10, specific_time="08:30"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0].specific_time == "08:30", "Timed task should come first"
    assert sorted_tasks[-1].name == "Grooming",       "Anytime task should be last"
    print("PASS: sort_by_time() places Anytime tasks at the end")


def test_sort_by_time_two_tasks_same_time_no_crash():
    """Two tasks at the exact same time must both appear — no crash."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    pet.add_task(Task.create_task(name="Task A", type_of_task="Exercise",
                                   duration=10, specific_time="09:00"))
    pet.add_task(Task.create_task(name="Task B", type_of_task="Exercise",
                                   duration=15, specific_time="09:00"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    sorted_tasks = scheduler.sort_by_time()
    times = [t.specific_time for t in sorted_tasks]

    assert len(sorted_tasks) == 2,              "Both tasks should be returned"
    assert times == ["09:00", "09:00"],          f"Expected two '09:00' entries, got {times}"
    print("PASS: sort_by_time() handles two tasks at the exact same time without crashing")


def test_sort_by_time_pet_with_no_tasks():
    """A pet with zero tasks should return an empty list — no crash."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    assert scheduler.sort_by_time() == [], "Expected [] for a pet with no tasks"
    print("PASS: sort_by_time() returns [] when the pet has no tasks")


def test_sort_by_time_merges_across_multiple_pets():
    """sort_by_time must pull tasks from ALL owner pets and sort them together."""
    buddy = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    luna  = Pet.create(name="Luna",  animal_type="Cat", age=5, gender="Female")
    owner = make_owner_with_pets(buddy, luna)

    buddy.add_task(Task.create_task(name="Evening Walk",  type_of_task="Exercise",
                                    duration=25, specific_time="18:00"))
    luna.add_task(Task.create_task( name="Feeding",       type_of_task="Feeding",
                                    duration=10, specific_time="08:30"))
    buddy.add_task(Task.create_task(name="Morning Walk",  type_of_task="Exercise",
                                    duration=30, specific_time="07:00"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=buddy)
    times = [t.specific_time for t in scheduler.sort_by_time()]

    assert times == ["07:00", "08:30", "18:00"], (
        f"Expected ['07:00', '08:30', '18:00'] across both pets, got {times}"
    )
    print("PASS: sort_by_time() correctly merges and sorts tasks from multiple pets")


# ── recurrence logic tests ────────────────────────────────────────────────────

def test_daily_task_creates_next_day_occurrence():
    """Completing a DAILY task must add a new task due tomorrow."""
    today_str     = date.today().isoformat()
    tomorrow_str  = (date.today() + timedelta(days=1)).isoformat()

    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    task = Task.create_task(name="Morning Walk", type_of_task="Exercise", duration=30,
                             frequency=Frequency.DAILY, due_date=today_str)
    pet.add_task(task)

    task.mark_complete(pet=pet)

    assert task.completed == True,        "Original task should be marked complete"
    assert len(pet.tasks_list) == 2,      "A new occurrence should have been added"

    new_task = pet.tasks_list[1]
    assert new_task.due_date  == tomorrow_str, (
        f"New daily task should be due {tomorrow_str}, got {new_task.due_date}"
    )
    assert new_task.completed == False,   "New occurrence should start as pending"
    assert new_task.name      == task.name, "New occurrence should share the same name"
    print("PASS: mark_complete() creates a next-day occurrence for a DAILY task")


def test_weekly_task_creates_next_week_occurrence():
    """Completing a WEEKLY task must add a new task due 7 days later."""
    today_str      = date.today().isoformat()
    next_week_str  = (date.today() + timedelta(weeks=1)).isoformat()

    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    task = Task.create_task(name="Grooming", type_of_task="Hygiene", duration=40,
                             frequency=Frequency.WEEKLY, due_date=today_str)
    pet.add_task(task)
    task.mark_complete(pet=pet)

    assert len(pet.tasks_list) == 2, "A new weekly occurrence should have been added"
    new_task = pet.tasks_list[1]
    assert new_task.due_date == next_week_str, (
        f"New weekly task should be due {next_week_str}, got {new_task.due_date}"
    )
    print("PASS: mark_complete() creates a next-week occurrence for a WEEKLY task")


def test_once_task_does_not_create_new_occurrence():
    """Completing a ONCE task must NOT add any new task."""
    pet = Pet.create(name="Luna", animal_type="Cat", age=5, gender="Female")
    task = Task.create_task(name="Vet Checkup", type_of_task="Medical", duration=60,
                             frequency=Frequency.ONCE, due_date=date.today().isoformat())
    pet.add_task(task)

    task.mark_complete(pet=pet)

    assert task.completed == True,     "Task should be marked complete"
    assert len(pet.tasks_list) == 1,   "ONCE task must not spawn a new occurrence"
    print("PASS: mark_complete() does NOT create a new occurrence for a ONCE task")


def test_mark_complete_twice_creates_duplicate():
    """
    Edge case (known bug): calling mark_complete() a second time on an already-completed
    DAILY task adds a second new occurrence because mark_complete() does not guard against
    self.completed already being True.

    This test documents the current behaviour. A future fix should check
    `if not self.completed` before spawning a new task.
    """
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    task = Task.create_task(name="Morning Walk", type_of_task="Exercise", duration=30,
                             frequency=Frequency.DAILY, due_date=date.today().isoformat())
    pet.add_task(task)

    task.mark_complete(pet=pet)   # first call  → task list: [original, next_1]      (2)
    task.mark_complete(pet=pet)   # second call → task list: [original, next_1, next_2] (3)

    # BUG: a second occurrence is created. Ideally this should still be 2.
    assert len(pet.tasks_list) == 3, (
        f"BUG documented: calling mark_complete twice creates a duplicate — "
        f"expected 3 (current behaviour), got {len(pet.tasks_list)}"
    )
    print("NOTE (known bug): mark_complete() called twice creates a duplicate occurrence — "
          "add an `if not self.completed` guard to fix")


def test_recurring_task_preserves_all_attributes():
    """The new occurrence must copy name, type, duration, priority, time, and notes."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    task = Task.create_task(
        name="Allergy Medication", type_of_task="Medical", duration=5,
        priority=Priority.URGENT, frequency=Frequency.DAILY,
        specific_time="08:00", notes="Half tablet mixed into food",
        due_date=date.today().isoformat()
    )
    pet.add_task(task)
    task.mark_complete(pet=pet)

    new_task = pet.tasks_list[1]
    assert new_task.name          == "Allergy Medication"
    assert new_task.type_of_task  == "Medical"
    assert new_task.duration      == 5
    assert new_task.priority      == Priority.URGENT
    assert new_task.frequency     == Frequency.DAILY
    assert new_task.specific_time == "08:00"
    assert new_task.notes         == "Half tablet mixed into food"
    print("PASS: new occurrence inherits all attributes from the original task")


# ── conflict detection tests ───────────────────────────────────────────────────

def test_detect_conflicts_same_pet_overlap():
    """Two overlapping tasks on the same pet must be flagged."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    # Walk: 07:00 – 07:30 | Stretch: 07:15 – 07:35 → overlap
    pet.add_task(Task.create_task(name="Morning Walk",    type_of_task="Exercise",
                                   duration=30, specific_time="07:00"))
    pet.add_task(Task.create_task(name="Pre-walk Stretch", type_of_task="Exercise",
                                   duration=20, specific_time="07:15"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1,               f"Expected 1 conflict, got {len(conflicts)}"
    assert "Morning Walk"     in conflicts[0]
    assert "Pre-walk Stretch" in conflicts[0]
    print("PASS: detect_conflicts() flags overlapping tasks on the same pet")


def test_detect_conflicts_different_pets_overlap():
    """Overlapping tasks across two different pets must be flagged."""
    buddy = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    luna  = Pet.create(name="Luna",  animal_type="Cat", age=5, gender="Female")
    owner = make_owner_with_pets(buddy, luna)

    # Buddy Breakfast: 08:25 – 08:45 | Luna Feeding: 08:30 – 08:40 → overlap
    buddy.add_task(Task.create_task(name="Buddy Breakfast", type_of_task="Feeding",
                                    duration=20, specific_time="08:25"))
    luna.add_task(Task.create_task( name="Luna Feeding",    type_of_task="Feeding",
                                    duration=10, specific_time="08:30"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=buddy)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1,               f"Expected 1 conflict, got {len(conflicts)}"
    assert "Buddy Breakfast" in conflicts[0]
    assert "Luna Feeding"    in conflicts[0]
    print("PASS: detect_conflicts() flags overlapping tasks across different pets")


def test_detect_conflicts_identical_start_times():
    """Two tasks that start at the exact same time must be flagged."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    pet.add_task(Task.create_task(name="Task A", type_of_task="Exercise",
                                   duration=30, specific_time="09:00"))
    pet.add_task(Task.create_task(name="Task B", type_of_task="Medical",
                                   duration=10, specific_time="09:00"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1, (
        f"Expected 1 conflict for duplicate start times, got {len(conflicts)}"
    )
    print("PASS: detect_conflicts() flags two tasks with the exact same start time")


def test_detect_conflicts_back_to_back_is_not_a_conflict():
    """Task A ending exactly when Task B starts is NOT a conflict."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    # Walk: 08:00 – 08:30 | Feeding: 08:30 – 08:40 (starts exactly when Walk ends)
    pet.add_task(Task.create_task(name="Walk",    type_of_task="Exercise",
                                   duration=30, specific_time="08:00"))
    pet.add_task(Task.create_task(name="Feeding", type_of_task="Feeding",
                                   duration=10, specific_time="08:30"))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts()

    assert conflicts == [], f"Back-to-back tasks should not conflict, got: {conflicts}"
    print("PASS: detect_conflicts() does NOT flag back-to-back (non-overlapping) tasks")


def test_detect_conflicts_no_tasks_returns_empty():
    """A pet with no tasks must produce an empty conflict list — no crash."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    assert scheduler.detect_conflicts() == [], "Expected no conflicts for empty task list"
    print("PASS: detect_conflicts() returns [] when there are no tasks")


def test_detect_conflicts_ignores_completed_tasks():
    """Completed tasks must be skipped by detect_conflicts."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    t1 = Task.create_task(name="Walk",    type_of_task="Exercise",
                           duration=30, specific_time="07:00")
    t2 = Task.create_task(name="Stretch", type_of_task="Exercise",
                           duration=20, specific_time="07:15")
    t1.mark_complete()   # mark done (no pet arg — no recurrence needed here)

    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts()

    assert conflicts == [], f"Completed tasks should be ignored, got: {conflicts}"
    print("PASS: detect_conflicts() ignores completed tasks")


def test_detect_conflicts_anytime_tasks_not_checked():
    """Tasks with no specific_time must not be included in conflict checks."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    pet.add_task(Task.create_task(name="Grooming", type_of_task="Hygiene",
                                   duration=40, specific_time=None))
    pet.add_task(Task.create_task(name="Playtime", type_of_task="Exercise",
                                   duration=30, specific_time=None))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    assert scheduler.detect_conflicts() == [], "Anytime tasks should not produce conflicts"
    print("PASS: detect_conflicts() does not flag Anytime tasks (no specific_time)")


# ── filter_tasks tests ────────────────────────────────────────────────────────

def test_filter_tasks_pending_only():
    """filter_tasks(completed=False) must return only incomplete tasks."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    done    = Task.create_task(name="Feeding", type_of_task="Feeding",  duration=10)
    pending = Task.create_task(name="Walk",    type_of_task="Exercise", duration=30)
    done.mark_complete()

    pet.add_task(done)
    pet.add_task(pending)

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    result = scheduler.filter_tasks(completed=False)

    assert len(result) == 1,            f"Expected 1 pending task, got {len(result)}"
    assert result[0].name == "Walk"
    print("PASS: filter_tasks(completed=False) returns only pending tasks")


def test_filter_tasks_completed_only():
    """filter_tasks(completed=True) must return only completed tasks."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)

    done    = Task.create_task(name="Feeding", type_of_task="Feeding",  duration=10)
    pending = Task.create_task(name="Walk",    type_of_task="Exercise", duration=30)
    done.mark_complete()

    pet.add_task(done)
    pet.add_task(pending)

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    result = scheduler.filter_tasks(completed=True)

    assert len(result) == 1,              f"Expected 1 completed task, got {len(result)}"
    assert result[0].name == "Feeding"
    print("PASS: filter_tasks(completed=True) returns only completed tasks")


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) must return only that specific pet's tasks."""
    buddy = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    luna  = Pet.create(name="Luna",  animal_type="Cat", age=5, gender="Female")
    owner = make_owner_with_pets(buddy, luna)

    buddy.add_task(Task.create_task(name="Buddy Walk", type_of_task="Exercise", duration=30))
    luna.add_task(Task.create_task( name="Luna Nap",   type_of_task="Rest",     duration=60))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=buddy)
    result = scheduler.filter_tasks(pet_name="Buddy")

    assert len(result) == 1,                f"Expected 1 task for Buddy, got {len(result)}"
    assert result[0].name == "Buddy Walk"
    print("PASS: filter_tasks(pet_name='Buddy') returns only Buddy's tasks")


def test_filter_tasks_unknown_pet_returns_empty():
    """Filtering by a pet name that doesn't exist must return []."""
    pet = Pet.create(name="Buddy", animal_type="Dog", age=3, gender="Male")
    owner = make_owner_with_pets(pet)
    pet.add_task(Task.create_task(name="Walk", type_of_task="Exercise", duration=30))

    scheduler = Scheduler.create_schedule(pet_owner=owner, pet=pet)
    assert scheduler.filter_tasks(pet_name="Fluffy") == [], (
        "Unknown pet name should return []"
    )
    print("PASS: filter_tasks() returns [] for a pet name that doesn't exist")


# ── scheduler creation tests ───────────────────────────────────────────────────

def test_create_schedule_raises_for_unowned_pet():
    """create_schedule() must raise ValueError when the pet is not registered to the owner."""
    owner = PetOwner.create_owner_profile(name="Maria", address="1 St", phone_number="000")
    stray = Pet.create(name="Stray", animal_type="Dog", age=2, gender="Male")

    raised = False
    try:
        Scheduler.create_schedule(pet_owner=owner, pet=stray)
    except ValueError:
        raised = True

    assert raised, "create_schedule() should raise ValueError for an unregistered pet"
    print("PASS: create_schedule() raises ValueError when pet is not owned by the owner")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running all tests...\n")

    # existing
    test_mark_complete_changes_status()
    test_add_task_increases_pet_task_count()

    # sorting
    test_sort_by_time_returns_chronological_order()
    test_sort_by_time_anytime_tasks_go_to_end()
    test_sort_by_time_two_tasks_same_time_no_crash()
    test_sort_by_time_pet_with_no_tasks()
    test_sort_by_time_merges_across_multiple_pets()

    # recurrence
    test_daily_task_creates_next_day_occurrence()
    test_weekly_task_creates_next_week_occurrence()
    test_once_task_does_not_create_new_occurrence()
    test_mark_complete_twice_creates_duplicate()
    test_recurring_task_preserves_all_attributes()

    # conflict detection
    test_detect_conflicts_same_pet_overlap()
    test_detect_conflicts_different_pets_overlap()
    test_detect_conflicts_identical_start_times()
    test_detect_conflicts_back_to_back_is_not_a_conflict()
    test_detect_conflicts_no_tasks_returns_empty()
    test_detect_conflicts_ignores_completed_tasks()
    test_detect_conflicts_anytime_tasks_not_checked()

    # filter_tasks
    test_filter_tasks_pending_only()
    test_filter_tasks_completed_only()
    test_filter_tasks_by_pet_name()
    test_filter_tasks_unknown_pet_returns_empty()

    # scheduler creation
    test_create_schedule_raises_for_unowned_pet()

    print("\nAll tests passed.")
