# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- The user can (1) enter basic owner + pet info, 
(2) add/edit pet care tasks with duration and priority, and 
(3) generate a daily schedule/plan that fits within time constraints and shows an explanation for the chosen order.
- `Owner` stores the owner profile, owner-level scheduling preferences, and the list of `Pet` objects that belong to the owner.
- `Pet` stores pet identity (name/species), pet-level preferences, and the list of `Task` items that need to be scheduled.
- `Task` represents one care activity (title, duration, priority) and provides priority scoring behavior (stubbed for now) that the scheduler can use.
- `Scheduler` is responsible for taking the owner + day + constraints and producing an ordered daily plan (plus a human-readable explanation).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
- One tradeoff is that conflict detection only checks for exact same start times (for example, two tasks both at 08:00) instead of full duration overlap analysis.
- This is reasonable for the current project scope because it keeps the algorithm simple and easy to explain, while still catching the most obvious scheduling issues for a busy pet owner.
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
