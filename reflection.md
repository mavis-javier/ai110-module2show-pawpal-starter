# PawPal+ Project Reflection

## 1. System Design
** Actions
- User can create a task for a pet.
- User can create a daily plan that consists of multiple tasks with a deadline and priority.
- User can see today's task and other tasks due in other dates.

**a. Initial design**

- Briefly describe your initial UML design.
UML design will keep track of the pets the user have and tasks they have for each pet.
- What classes did you include, and what responsibilities did you assign to each?
The UML design will have an Owner class that has 1 or multiple pets, a Task class to store task details, Pet class to store pet information, and a scheduler class to perform other operations on task.


**b. Design changes**

- Did your design change during implementation?
Yes.
- If yes, describe at least one change and why you made it.
Claude recommended changes in pawpal_system.py to make Task.pet assigment required and not optional.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
scheduler only stores due date and not time
- Why is that tradeoff reasonable for this scenario?
it keeps implementation more simple.

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
