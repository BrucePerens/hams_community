# Epics & User Stories: Testing & Education

## Epic: Spaced Repetition Exam Prep
* **Story:** As a prospective ham, I want my practice exams to prioritize questions I previously failed, so I can learn efficiently.
    * **BDD Criteria:**
        * *Given* an operator taking practice tests
        * *When* the backend generates the test
        * *Then* the system MUST sort the pool by historical failure weight. *(Reference: [@ANCHOR: swl_spaced_repetition])*
* **Story:** As a student, I want detailed AI-generated explanations for incorrect answers to understand the core concept rather than just memorizing letters.
    * **BDD Criteria:**
        * *Given* a completed exam
        * *When* the user requests an explanation
        * *Then* the backend MUST return the static HTML context debunking the distractors. *(Reference: [@ANCHOR: swl_exam_explanations])*

## Epic: Morse Code Academy
* **Story:** As a beginner, I want the system to track my progress using the Koch method, automatically unlocking new characters as I prove proficiency.
    * **BDD Criteria:**
        * *Given* an uninitiated user
        * *When* they start the Academy
        * *Then* the system MUST restrict the pool to 'KM' and expand as they pass. *(Reference: [@ANCHOR: morse_koch_progression])*
* **Story:** As a learner, I want audio playback to use Farnsworth timing, spacing characters further apart without slowing down the character's internal speed, so I learn rhythm rather than counting dots.
    * **BDD Criteria:**
        * *Given* an overall WPM slower than the character WPM
        * *When* the audio engine calculates spacing
        * *Then* it MUST dynamically expand the inter-character and inter-word gaps using standard Farnsworth math. *(Reference: [@ANCHOR: morse_farnsworth_timing])*
* **Story:** As an instructor, I want the system to simulate a standardized Volunteer Examiner comprehension test, generating dynamic simulated QSOs.
    * **BDD Criteria:**
        * *Given* an operator requesting an exam
        * *When* the UI constructs the challenge
        * *Then* the system MUST generate a dynamic QSO payload and questions. *(Reference: [@ANCHOR: morse_ve_exam_generation])*
