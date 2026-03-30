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
ownership, time window overlap, completion status, and recurrence frequency. 

- How did you decide which constraints mattered most?
Well I thought about what would be the most important to me if I ran a pet shop and also thought about what I would think about when designing a schedule, but I also consulted Claude to help me build on it later on with the multiple checks that we are to do for this assignment.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
when adding tasks, I think my code works overtime because it adds the task to the owner but also to the master schedule. 
- Why is that tradeoff reasonable for this scenario?
Well, the requirement isn't really to track schedules based on owner, rather just to have a general day-to-day schedule for the pet owner.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI to help me find better ways to improve my ideas for each feature as well as the application, debug my code, as well as help me code some parts as I'm not fully familiar with some of the modules and ways we use code
- What kinds of prompts or questions were most helpful?
One specific question that really helped me was where I asked Claude to go through my project to come up with any issues that could arise as I use the app. It basically gave me a list of missing connections and issues with my data sctructure. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
Well, when I was tyring to implement the feature where you have an owner view where you could see the pets and their schedules related to that owner, Claude first implemented a feature where whenever I created a new owner it would override the previous owner and they would be gone--i.e there is no owner history. 
- How did you evaluate or verify what the AI suggested?
I would evaluate and verify by going through and manually testing the feature out until I found a way to break the feature. I would also skim through the code to get an idea of what it's doing and what it's missing

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested task completion to check the creation and brehavior after they are marked complete. I also testing the sorting behavior to make sure there were no issues there. I tested the recurrence behavior to ensure that tasks that were to be repeated were infact being repeated, but also the feature that is supposed to reset this auto-repetition. Fourthly, I tested the conflict detection bit to ensure that any feature that could have conflcits would have some sort of warning to prevent that. I also tested the filtering to ensure that data was being filtered correctly based off the user-specified constraint(s). Lastly, I tested schedle creation to ensure that they are being created as intended, but also the case where pets are not registered to owners.
- Why were these tests important?
They are important because they test the main functionality as well as exceptions. They allow certainty that atleast the main aspects of the application function without issues.

**b. Confidence**

- How confident are you that your scheduler works correctly?
4/5
- What edge cases would you test next if you had more time?
I would also test the UI more throroughly because a lot of my tests are more code-related than they are UI. Often times, despite the code working flawlessly, the UI logic can be flawed and allow bugs. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
Probably the feature to select which owner and which pet the user wants to add tasks for

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would focus a bit more on UI and ensure that it works flawlessly and looks better as well (it looks cute right now I wont lie)

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI can be really helpful with the data admin bit. Data schemas I feel like are something that are better made with a group of people, but AI made it a lot easier for me because it was like a companion that told me where and when I was short of something.
