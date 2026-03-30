# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling
Feature 1: Owner Management
- you can add multiple owners
- you can select owners given that you can have multiple per day
- duplicate prevention where you can't add duplicate owners (this does a name-to-name check which isn't proper, however, just for simplicity I had it implemented in that manner)

Feature 2: Pet Management
- owners can have multiple pets
- users can select which pet they are reffering to
- users can also remove pets
- there is also a duplicate-prevention feature here (same thing, so if duplicate names exist, it wont allow for it to exist)

Feature 3: Task Management (per pet)
- theres a three-tab task view (all, pending, completed)
- theres an option to mark a task complete
- when a daily is marked done, a new copy is created. This is the same for weekly tasks 
- users can delete tasks
- lastly, every task carries a due_date field

Feature 4: Master Schedule
- this is where all scheduled tasks are displayed for all owners' pets.
- there are filtering features to allow filtering by owner, pet, status, priority
- users are able to sort by time
- conflicts are detected
- there's a button to reset daily and weekly tasks 
- the metric bar shows the tasks, pending, estimated duration, and time conflicts

Feature 5: Summary Panels
- there's a per-owner summary with total tasks, pending count, and urgent count across all of the owner's pets
- theres an overall summery which appears when more than 2 owners exist, where it's one row per owner shiwing their pet name plus task, pending/urgent counts

## Testing PawPal+
### Command to run tests: `python -m pytest`
### Description: 
1. Sorting (5 tests)
- Chronological order with out-of-order insertion
- Anytime tasks (specific_time=None) land at the end
- Two tasks at the exact same time -> no crash
- Pet with zero tasks returns []
- Tasks merged correctly across multiple pets

2. Recurrence Logic (5 tests)
- daily -> new task due tomorrow
- weekly -> new task due 7 days later
- once -> no new task created
- New occurrence copies all attributes (name, priority, time, notes, etc.) -> shouldn't go through
- Bug discovered: calling mark_complete twice creates a duplicate occurrence -> the test documents this and notes the fix (if not self.completed guard in mark_complete) ** NOTE: I'm not sure if this was okay because the test passes, but obv this is to detect a bug. So, I apologize if it wasn't allowed

3. Conflict Detection (7 tests)
- Same-pet overlap flagged
- Cross-pet overlap flagged
- Identical start times flagged
- Back-to-back tasks (A ends exactly when B starts) -> correctly NOT flagged
- No tasks → empty list, no crash
- Completed tasks are ignored
- Anytime tasks (no time) are ignored

4. Filter Tasks (4 tests) -> pending only, completed only, by pet name, unknown pet name should return []

5. Scheduler Creation (1 test) -> tests the ValueError that should be raised when pet doesn't belong to the owner

### Reliability Level: 4

## Features

### Owner & Pet Profile Management
Create, store, and switch between multiple owners and pets. Owners hold a list of pets; adding the same name twice is blocked.

### Task Creation with Typed Fields
Tasks are created with enforced types — Priority (LOW / MEDIUM / HIGH / URGENT) and Frequency (ONCE / DAILY / WEEKLY / MONTHLY) are enums, not free-form strings, so invalid values are impossible.

### Task Completion Tracking
Calling mark_complete() flips a task's completed flag from False to True, enabling pending vs. done filtering across the app.

### Daily & Weekly Recurrence
When a DAILY or WEEKLY task is marked complete, the algorithm automatically calculates the next due date (today + 1 day or today + 7 days) and spawns a fresh task instance on the pet's list. ONCE tasks complete without spawning anything.

### Chronological Sorting
sort_by_time() converts all HH:MM time strings to minutes-since-midnight and sorts all tasks across every pet into a single chronological list. Tasks with no specific time are pushed to the end using a sentinel value ("99:99").

### Cross-Pet Task Aggregation
get_all_tasks_across_pets() walks every pet owned by the owner and merges their task lists into one flat list, letting the Scheduler operate across pets without knowing which pet owns what.

### Task Filtering
filter_tasks(completed, pet_name) lets you slice the full task list by completion status, by a specific pet, or both at once — without modifying the underlying data.

### Computed Estimated Duration
estimated_duration is a @property that always sums task.duration across the current task list in real time. It can never go stale because it's never stored manually.

### Conflict Detection
detect_conflicts() converts every pending timed task to a [start, end] window in minutes and runs an O(n²) overlap check: two tasks conflict if start_A < end_B AND start_B < end_A. Works across same-pet and cross-pet task pairs and returns human-readable warning strings.

### Ownership Validation
Scheduler.create_schedule() checks that the given pet is actually in the owner's pets_list before creating a session — raising a ValueError immediately if there's a mismatch.

### Session State Persistence (UI)
st.session_state guards every object (owners, selected_owner_name, selected_pet_name) so that Streamlit's stateless reruns don't reset live data on every button click.

### Duplicate Guard (UI)
Before creating an owner or pet, the app checks for a name collision in the existing list and shows a warning instead of creating a duplicate.

<a href="/course_images/ai110/your_screenshot_name.png" target="_blank"><img src='/course_images/ai110/demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.