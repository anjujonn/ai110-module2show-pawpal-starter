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