# 🎓 Ham Radio Testing & CAPTCHA (`ham_testing`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Manages official NCVEC study pools. Exposes a secure internal API to generate and verify "Ham-CAPTCHAs" to authenticate human radio operators during onboarding and bypass standard image CAPTCHAs. It features a Spaced Repetition Exam Simulator for Prospective Hams (SWLs) and a comprehensive Morse Code Academy for interactive learning.

---

## 2. Data Model Reference

### Core Model: `ham.testing.captcha.session`
* **`token`** (`Char`, Indexed): Cryptographically secure token generated via Python's `secrets` module.
* **`question_id`** (`Many2one` to `survey.question`): The assigned NCVEC question.
* **`expires_at`** (`Datetime`): Set to 15 minutes after creation.

### Extended `survey.survey` (Pools)
* **`license_class`** (`Selection`): Technician, General, Amateur Extra.
* **`active_dates`** (`Char`): e.g., '2022-2026'.

### Extended `survey.question`
* **`ncvec_code`** (`Char`): e.g., 'T1A01'.
* **`explanation`** (`Text`): Deep technical HTML explanation for study feedback.

### New Model: `ham.testing.progress`
* **`user_id`**, **`question_id`**, **`times_asked`**, **`times_correct`**: Tracks the user's exam performance to algorithmically prioritize weak subjects during practice tests.

### New Model: `ham.morse.progress`
* **`unlocked_characters`**: Tracks Koch method state (e.g., starts with 'KM').
* **`current_wpm`**: Base speed setting.
* **`model.get_next_lesson()`**: Initializes or retrieves the operator's current Morse capability state.

---

## 3. Public Python API & Methods

### On `ham.testing.captcha.session`:
* **`model.generate_challenge(license_class='technician')`**: Randomly selects an active question and generates a secure session token. Returns `token`, `question_code`, `question_text`, and shuffled `choices`.
* **`model.verify_answer(token, submitted_answer)`**: Validates the selected letter against the stored question's correct answer and immediately `unlinks` the session.

### On `ham.testing.progress`:
* **`model.generate_exam(license_class='technician', limit=35)`**: Constructs a practice exam utilizing spaced repetition, prioritizing previously failed questions.

---

## 4. REST APIs
* **Explanation API:** `POST /api/v1/ham_testing/explanation/<ncvec_code>` - Returns the static AI-synthesized HTML explanation defining the core concept and debunking distractors.
