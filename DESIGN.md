# AI Tutoring System Design Document

## 1. Agent Roles and Responsibilities

This system will use five distinct AI agents, each with a specific role to create a comprehensive and interactive learning experience.

### 1.1. Assessment Agent
- **Responsibilities:**
    - Understand the student's initial knowledge level for a chosen topic. This could be through direct questions, analysis of prior performance, or by allowing the student to self-assess.
    - Determine the most suitable starting point or learning module for the student.
    - Identify knowledge gaps if the student has prior experience with the topic.
- **Interactions:**
    - Receives topic selection from the user/frontend.
    - Publishes an "AssessmentComplete" message with the student's identified learning path or starting point.

### 1.2. Teaching Agent
- **Responsibilities:**
    - Deliver learning content, explanations, and examples for the current lesson or topic.
    - Break down complex topics into smaller, manageable chunks.
    - Adapt the teaching style or depth of explanation based on student progress and feedback (potentially guided by the Feedback Agent).
    - Generate lesson content using LLM (Vertex AI Gemini).
- **Interactions:**
    - Subscribes to "AssessmentComplete" messages or "NextLesson" requests.
    - Publishes "LessonContent" messages containing the material for the student to study.

### 1.3. Quizmaster Agent
- **Responsibilities:**
    - Generate relevant quiz questions (multiple choice, short answer, interactive exercises) based on the material covered by the Teaching Agent.
    - Ensure questions accurately assess understanding of the current lesson.
    - Store quiz questions and their correct answers.
    - Vary question types and difficulty.
- **Interactions:**
    - Subscribes to "LessonCompleted" messages or direct quiz requests.
    - Publishes "QuizReady" messages containing the questions for the student.
    - Stores quiz details (questions, correct answers, explanations) in Firestore.

### 1.4. Feedback Agent
- **Responsibilities:**
    - Evaluate student's answers to quiz questions.
    - Provide immediate, constructive feedback:
        - Confirm correct answers.
        - Explain why an answer is incorrect.
        - Offer hints or point to relevant lesson material for incorrect answers.
    - Track student performance and identify areas needing more attention.
    - Update user progress and learning history.
    - Use LLM (Vertex AI Gemini) to generate personalized feedback and explanations.
- **Interactions:**
    - Subscribes to "QuizAttemptSubmitted" messages containing the student's answers.
    - Publishes "FeedbackProvided" messages with detailed feedback for the student.
    - Updates Firestore with quiz results and learning progress.
    - May publish "FurtherStudyRecommended" messages to the Teaching Agent if significant gaps are identified.

### 1.5. Motivation Agent
- **Responsibilities:**
    - Monitor student progress, effort, and engagement.
    - Provide encouragement, positive reinforcement, and motivational messages.
    - Implement gamification elements: track streaks, award points/badges (virtual).
    - Nudge inactive students or celebrate achievements.
- **Interactions:**
    - Subscribes to "FeedbackProvided", "LessonCompleted", "QuizAttemptSubmitted" messages to track activity.
    - Publishes "MotivationalMessage" to be displayed to the student.
    - Updates gamification-related data in Firestore.

## 2. Communication Protocols (Pub/Sub Messages)

Communication between agents will be asynchronous using Google Cloud Pub/Sub. Messages will be in JSON format.

### 2.1. `AssessmentComplete`
- **Published by:** Assessment Agent
- **Consumed by:** Teaching Agent
- **Purpose:** To inform the Teaching Agent about the student's starting point or learning plan.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "topicId": "algebra-basics",
    "assessment": {
      "initialLevel": "beginner", // beginner, intermediate, advanced
      "recommendedModules": ["module1", "module2"],
      "focusAreas": ["solving-equations"] // specific sub-topics if any
    },
    "timestamp": "2024-07-28T10:00:00Z"
  }
  ```

### 2.2. `LessonContent`
- **Published by:** Teaching Agent
- **Consumed by:** Frontend (directly or via a backend service), Quizmaster Agent (to know when a lesson is delivered)
- **Purpose:** To provide the learning material for the current lesson.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "topicId": "algebra-basics",
    "lessonId": "module1-lesson1",
    "contentType": "text/html", // or markdown, interactive_component_id
    "content": "<p>This is an explanation of basic algebraic expressions...</p>",
    "estimatedReadingTime": 5, // minutes
    "order": 1,
    "timestamp": "2024-07-28T10:05:00Z"
  }
  ```

### 2.3. `LessonCompleted`
- **Published by:** Frontend/User Action (implicitly when user moves to quiz or next lesson) or Teaching Agent (if it can determine completion)
- **Consumed by:** Quizmaster Agent, Feedback Agent, Motivation Agent
- **Purpose:** To indicate that the student has finished reviewing a lesson.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "topicId": "algebra-basics",
    "lessonId": "module1-lesson1",
    "timestamp": "2024-07-28T10:15:00Z"
  }
  ```

### 2.4. `QuizReady`
- **Published by:** Quizmaster Agent
- **Consumed by:** Frontend (directly or via a backend service)
- **Purpose:** To provide the quiz questions for the current lesson.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "topicId": "algebra-basics",
    "lessonId": "module1-lesson1",
    "quizId": "quiz001",
    "questions": [
      {
        "questionId": "q1",
        "type": "multiple-choice",
        "text": "What is 2 + 2?",
        "options": ["3", "4", "5"],
        // Correct answer stored in Firestore by Quizmaster, not sent to client
      },
      {
        "questionId": "q2",
        "type": "short-answer",
        "text": "Explain the concept of a variable."
      }
    ],
    "timestamp": "2024-07-28T10:20:00Z"
  }
  ```

### 2.5. `QuizAttemptSubmitted`
- **Published by:** Frontend/User Action
- **Consumed by:** Feedback Agent, Motivation Agent
- **Purpose:** To submit the student's answers for evaluation.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "quizId": "quiz001",
    "answers": [
      { "questionId": "q1", "answer": "4" },
      { "questionId": "q2", "answer": "A variable is a symbol that represents a value." }
    ],
    "timestamp": "2024-07-28T10:25:00Z"
  }
  ```

### 2.6. `FeedbackProvided`
- **Published by:** Feedback Agent
- **Consumed by:** Frontend, Motivation Agent
- **Purpose:** To deliver feedback on the student's quiz attempt.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "quizId": "quiz001",
    "overallScore": 0.5, // e.g., 1.0 for 100%
    "feedbackItems": [
      {
        "questionId": "q1",
        "isCorrect": true,
        "feedbackText": "Correct! Well done."
      },
      {
        "questionId": "q2",
        "isCorrect": false,
        "feedbackText": "Your explanation is on the right track, but could be more precise. A variable is a placeholder for a value that can change.",
        "correctAnswerPreview": "A variable is a symbol used to represent an unknown value or quantity that can change or vary."
      }
    ],
    "timestamp": "2024-07-28T10:30:00Z"
  }
  ```

### 2.7. `MotivationalMessage`
- **Published by:** Motivation Agent
- **Consumed by:** Frontend
- **Purpose:** To provide an encouraging message to the student.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "messageType": "encouragement", // or "achievement", "nudge"
    "messageText": "Great effort on that last quiz! Keep up the fantastic work!",
    "timestamp": "2024-07-28T10:31:00Z"
  }
  ```

### 2.8. `NextLesson` (Request)
- **Published by:** Frontend/User Action or Feedback Agent (if recommending a specific next step)
- **Consumed by:** Teaching Agent
- **Purpose:** To request the content for the next lesson in the sequence.
- **Payload Example:**
  ```json
  {
    "userId": "user123",
    "topicId": "algebra-basics",
    "currentLessonId": "module1-lesson1", // Optional, to help Teaching Agent determine context
    "requestedLessonId": "module1-lesson2", // Optional, if a specific lesson is requested
    "timestamp": "2024-07-28T10:35:00Z"
  }
  ```

## 3. Firestore Data Models

Firestore will be used to store user data, learning progress, quiz content, and other persistent information. Below are the proposed collections and their typical document structures.

### 3.1. `users`
- **Collection:** `users`
- **Document ID:** Firebase Auth User ID (`uid`)
- **Purpose:** Stores user profile information and links to their learning history.
- **Structure:**
  ```json
  {
    "email": "student@example.com",    // From Firebase Auth
    "displayName": "Student Name",     // From Firebase Auth or user input
    "photoURL": "url_to_photo",        // From Firebase Auth or user input
    "createdAt": "timestamp",          // Timestamp of account creation
    "lastLoginAt": "timestamp",        // Timestamp of last login
    "preferences": {
      "learningPace": "medium",      // e.g., slow, medium, fast
      "preferredTopics": ["math", "science"]
    }
    // Other user-specific settings
  }
  ```

### 3.2. `user_learning_progress`
- **Collection:** `user_learning_progress`
- **Document ID:** Auto-generated ID or a composite ID (e.g., `{userId}_{topicId}`)
- **Purpose:** Tracks a user's progress within a specific topic or learning path.
- **Structure:**
  ```json
  {
    "userId": "user123",               // Foreign key to users collection
    "topicId": "algebra-basics",
    "status": "in-progress",           // e.g., not-started, in-progress, completed
    "currentLessonId": "module1-lesson2",
    "completedLessons": ["module1-lesson1"],
    "scores": [
      { "quizId": "quiz001", "score": 0.8, "timestamp": "..." }
    ],
    "achievements": ["streak_3_days", "first_quiz_passed"], // Gamification
    "startedAt": "timestamp",
    "lastUpdatedAt": "timestamp",
    "notes": "Struggled a bit with linear equations." // Optional user or system notes
  }
  ```
  *Note: Alternatively, this could be a subcollection under each `user` document if preferred, e.g., `users/{userId}/learning_progress`.*

### 3.3. `topics`
- **Collection:** `topics`
- **Document ID:** Unique topic identifier (e.g., `algebra-basics`, `calculus-differentiation`)
- **Purpose:** Stores information about available learning topics and their structure.
- **Structure:**
  ```json
  {
    "topicName": "Algebra Basics",
    "description": "Fundamental concepts of algebra.",
    "category": "Mathematics",
    "difficulty": "Beginner",
    "estimatedDuration": "10 hours", // Total estimated time for the topic
    "modulesOrder": ["module1", "module2", "module3"] // Ordered list of module IDs
  }
  ```

### 3.4. `modules`
- **Collection:** `modules` (or could be `topic_modules` if namespacing is desired)
- **Document ID:** Unique module identifier (e.g., `algebra-module1-expressions`)
- **Purpose:** Stores details about a specific module within a topic.
- **Structure:**
  ```json
  {
    "topicId": "algebra-basics",         // Foreign key to topics collection
    "moduleName": "Introduction to Algebraic Expressions",
    "description": "Learn about variables, constants, and basic operations.",
    "lessonsOrder": ["lesson101", "lesson102", "lesson103"], // Ordered list of lesson IDs within this module
    "learningObjectives": [
        "Understand the definition of a variable.",
        "Identify constants and coefficients.",
        "Perform basic addition and subtraction of algebraic terms."
    ]
  }
  ```


### 3.5. `lessons`
- **Collection:** `lessons` (or `module_lessons`)
- **Document ID:** Unique lesson identifier (e.g., `algebra-lesson101-variables`)
- **Purpose:** Stores the actual learning content for each lesson.
- **Structure:**
  ```json
  {
    "moduleId": "algebra-module1-expressions", // Foreign key to modules collection
    "topicId": "algebra-basics",              // Foreign key to topics collection (denormalized for easier queries)
    "lessonTitle": "What is a Variable?",
    "contentType": "markdown", // or "html", "video_url", "interactive_exercise_id"
    "content": "A variable is a symbol used to represent a quantity that can change...",
    // For video: "videoUrl": "https://youtube.com/watch?v=xyz"
    // For interactive: "interactiveComponentId": "var-explorer-v1"
    "estimatedDurationMinutes": 15,
    "orderInModule": 1,
    "prerequisites": [] // List of lesson IDs that should be completed before this one
  }
  ```

### 3.6. `quizzes`
- **Collection:** `quizzes`
- **Document ID:** Unique quiz identifier (e.g., `quiz_algebra_lesson101`)
- **Purpose:** Stores quiz questions, answers, and explanations related to a lesson or module.
- **Structure:**
  ```json
  {
    "lessonId": "algebra-lesson101-variables", // Foreign key to lessons collection
    "moduleId": "algebra-module1-expressions", // Denormalized
    "topicId": "algebra-basics",               // Denormalized
    "title": "Quiz: Understanding Variables",
    "questions": [
      {
        "questionId": "q1",
        "type": "multiple-choice", // "short-answer", "true-false"
        "text": "Which of the following best describes a variable?",
        "options": [
          {"id": "opt1", "text": "A fixed number"},
          {"id": "opt2", "text": "A symbol for a quantity that can change"},
          {"id": "opt3", "text": "An operation like addition"}
        ],
        "correctOptionId": "opt2", // For multiple-choice
        "correctAnswerText": "A symbol for a quantity that can change", // For short-answer/explanation
        "explanation": "Variables are fundamental to algebra as they allow us to write general mathematical statements."
      },
      {
        "questionId": "q2",
        "type": "short-answer",
        "text": "In the expression 2x + 5, what is 'x' called?",
        "correctAnswerText": "variable",
        "explanation": "'x' is the variable, '2' is its coefficient, and '5' is a constant."
      }
    ],
    "passThreshold": 0.7 // e.g., 70% to pass
  }
  ```

### 3.7. `quiz_attempts`
- **Collection:** `quiz_attempts`
- **Document ID:** Auto-generated ID
- **Purpose:** Records each attempt a user makes on a quiz.
- **Structure:**
  ```json
  {
    "userId": "user123",                  // Foreign key to users collection
    "quizId": "quiz_algebra_lesson101",   // Foreign key to quizzes collection
    "lessonId": "algebra-lesson101-variables", // Denormalized
    "topicId": "algebra-basics",                // Denormalized
    "answers": [
      { "questionId": "q1", "selectedOptionId": "opt2", "isCorrect": true },
      { "questionId": "q2", "responseText": "variable", "isCorrect": true }
    ],
    "score": 1.0, // Calculated score (e.g., 0.0 to 1.0)
    "passed": true,
    "startedAt": "timestamp",
    "completedAt": "timestamp",
    "feedbackGivenRef": "feedback_doc_id" // Optional link to a more detailed feedback document if needed
  }
  ```

### 3.8. `agent_states` (Optional)
- **Collection:** `agent_states`
- **Document ID:** Agent-specific ID (e.g., `TeachingAgent_user123_topic_algebra`)
- **Purpose:** To store any necessary state for an agent to resume or maintain context over long interactions. This might not be needed if agents are mostly stateless and rely on Pub/Sub messages and Firestore data.
- **Structure:** (Highly dependent on agent needs)
  ```json
  {
    "agentId": "TeachingAgent",
    "userId": "user123",
    "topicId": "algebra-basics",
    "currentSubTopic": "linear-equations",
    "lastInteractionTimestamp": "timestamp",
    "internalState": {
      // agent-specific data blob
    }
  }
  ```
  *Consider if this is truly needed or if state can be derived from `user_learning_progress` and message payloads.*

---

## 4. User Authentication Flow (Firebase Auth)

User authentication will be managed by Firebase Authentication, providing a secure and robust system for user sign-up, sign-in, and profile management.

### 4.1. Core Principles
- **Security:** Leverage Firebase Auth's built-in security features (secure token handling, password hashing, etc.).
- **Ease of Use:** Offer common authentication methods (email/password, Google Sign-In).
- **Integration:** Firebase Auth UIDs will be the primary key for linking user data across Firestore collections (e.g., `users`, `user_learning_progress`).

### 4.2. Authentication Processes

#### 4.2.1. User Sign-Up
1.  **Frontend Interaction:** The user accesses the React/Vue.js frontend and navigates to the "Sign Up" page.
2.  **Input:** The user provides necessary information (e.g., email address, password). Optionally, Google Sign-Up can be offered.
3.  **Firebase SDK Call (Frontend):** The frontend uses the Firebase Auth SDK to call the appropriate sign-up method (e.g., `createUserWithEmailAndPassword` or `signInWithPopup` for Google).
4.  **Firebase Backend:** Firebase Auth handles the creation of the user account, securely stores credentials, and generates a unique User ID (UID).
5.  **User Record in Firestore (Backend/Cloud Function - Recommended):**
    *   Upon successful Firebase Auth user creation, a Cloud Function (triggered by `functions.auth.user().onCreate()`) should create a corresponding user document in the `users` collection in Firestore.
    *   This document will store additional application-specific profile information (e.g., display name if not set during auth, preferences). The UID from Firebase Auth will be the document ID.
6.  **Session Management:** Firebase Auth SDK on the client side manages the user's session (e.g., by issuing an ID token). The user is now signed in.
7.  **Redirection:** The user is redirected to their dashboard or a welcome page.

#### 4.2.2. User Sign-In
1.  **Frontend Interaction:** The user accesses the "Sign In" page.
2.  **Input:** User provides their credentials (email/password) or chooses a provider like Google.
3.  **Firebase SDK Call (Frontend):** The frontend uses the Firebase Auth SDK (e.g., `signInWithEmailAndPassword` or `signInWithPopup`).
4.  **Firebase Backend:** Firebase Auth verifies the credentials.
5.  **Session Management:** Upon successful authentication, Firebase Auth SDK manages the session and provides an ID token.
6.  **Firestore Record Update (Backend/Cloud Function - Optional but Recommended):**
    *   A Cloud Function (triggered by `functions.auth.user().onSignIn()` - though this trigger doesn't exist, alternative is to update `lastLoginAt` from client or a callable function post-login) can update fields like `lastLoginAt` in the `users` Firestore document.
7.  **Redirection:** User is redirected to their dashboard or the page they were trying to access.

#### 4.2.3. Password Reset
1.  **Frontend Interaction:** User clicks on a "Forgot Password?" link.
2.  **Input:** User provides their registered email address.
3.  **Firebase SDK Call (Frontend):** Frontend calls `sendPasswordResetEmail`.
4.  **Firebase Backend:** Firebase Auth sends a password reset email to the user.
5.  **User Action:** User follows the link in the email to set a new password.

#### 4.2.4. Sign Out
1.  **Frontend Interaction:** User clicks a "Sign Out" button.
2.  **Firebase SDK Call (Frontend):** Frontend calls `signOut()`.
3.  **Session Management:** Firebase Auth SDK clears the user's session.
4.  **Redirection:** User is redirected to the sign-in page or homepage.

### 4.3. Profile Management
- Users should be able to view and update their profile information (e.g., display name, photoURL if applicable, learning preferences).
- Changes made in the frontend will update the corresponding document in the `users` collection in Firestore.
- Firebase Auth provides methods to update basic profile info (like `updateProfile`) which can also be used.

### 4.4. Secure Access to Backend Resources
- **Cloud Run Services (Agents):** When agents (Cloud Run services) need to perform actions on behalf of a user or access user-specific data, they must verify the user's identity.
    - The frontend will send the Firebase ID token (obtained after login) in the `Authorization` header (e.g., `Bearer <ID_TOKEN>`) of requests made to backend services (or to an API Gateway in front of them).
    - Each Cloud Run service (or an API Gateway) will validate this ID token using the Firebase Admin SDK to ensure the request is authenticated and authorized.
- **Pub/Sub Messages:** Messages published to Pub/Sub by agents might contain the `userId`. Consuming agents will use this `userId` to perform actions or update data in Firestore related to that specific user. Direct user authentication isn't typically part of Pub/Sub messages themselves, but the initial action that triggered the agent workflow would have been authenticated.

---
