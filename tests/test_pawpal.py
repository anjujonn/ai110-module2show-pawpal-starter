import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Pet, Task


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

    task1 = Task.create_task(name="Feeding", type_of_task="Feeding", duration=10)
    task2 = Task.create_task(name="Walk", type_of_task="Exercise", duration=20)
    task3 = Task.create_task(name="Medication", type_of_task="Medical", duration=5)

    pet.add_task(task1)
    assert len(pet.tasks_list) == 1, "Task count should be 1 after adding first task"

    pet.add_task(task2)
    assert len(pet.tasks_list) == 2, "Task count should be 2 after adding second task"

    pet.add_task(task3)
    assert len(pet.tasks_list) == 3, "Task count should be 3 after adding third task"

    print("PASS: add_task() correctly increases pet task count")


if __name__ == "__main__":
    test_mark_complete_changes_status()
    test_add_task_increases_pet_task_count()
    print("\nAll tests passed.")
