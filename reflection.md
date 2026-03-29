# PawPal+ Project Reflection

## 1. System Design

So in response to the question in Section 1, the main user functionalities are these:
1. let users enter information about themselves and their pet
2. allow the user to add and edit tasks and their info
3. generate a daily schedule based on the provided information

**a. Initial design**

- Briefly describe your initial UML design.
I have four classes (Pet, Owner, Task, Schedule) and this is the basic overview of the design/relationships: 
1. PetOwner -> Pet: one-to-many (an owner can have multiple pets)
2. Schedule -> PetOwner: many-to-one (a schedule belongs to one owner)
3. Schedule -> Pet: many-to-one (a schedule is for one specific pet)
4. Schedule -> Tasks: one-to-many (a schedule contains multiple tasks)
- What classes did you include, and what responsibilities did you assign to each?
So I have four classes:
1. PetOwner - basically stores all the information related to the pet owner, including name, list of pets, and ways to contact the owner.
2. Pet - this class stores information about each individual pet including name, type of pet, allergies
3. Task - this class stores information related to individual tasks including name, type, and any time constraints.
4. Schedule - this class is regarding the order of tasks, status, owner and pet references. 

**b. Design changes**

- Did your design change during implementation?
Yes
- If yes, describe at least one change and why you made it.
So I've implemented these following changes:
    1. Added back-reference Schedule list to PetOwner (schedules_list), because originally you couldn't look up all schedules belonging to an owner, you would only be able to look at the owner tied to a schedule, but not the other way around, which is crucial because it's important to record history
    2. Added back-reference Schedule list to Pet (schedules_list), so you can look up all schedules for a specific pet.
    3. Added owner/pet validation in Schedule.create_schedule(), which raises a ValueError if the pet doesn't belong to the given owner
    4. Replaced manual estimated_duration field with a computed @property that always reflects the sum of task durations in tasks_list.
    5. Lastly, replaced free-form priority string on Task with a Priority Enum to prevent inconsistent values like "urgent" vs "URGENT" vs "1".


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
