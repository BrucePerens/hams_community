# 🎓 Ham Radio Testing & CAPTCHA (`ham_testing`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Manages NCVEC study pools and exposes Ham-CAPTCHAs to block bots during signup. Deploys its documentation to the Knowledge base automatically. [@ANCHOR: doc_inject_ham_testing]
</overview>

<caching_and_optimization>
## 2. Caching & Optimization
* The `survey.question` model heavily utilizes memory caching for rapid CAPTCHA generation.
* It explicitly invalidates the active question cache on question creation [@ANCHOR: survey_question_cache_invalidation_create], modification [@ANCHOR: survey_question_cache_invalidation], or deletion [@ANCHOR: survey_question_cache_invalidation_unlink] to maintain distributed coherence.
</caching_and_optimization>

<models>
## 3. Models
* **`ham.testing.captcha.session`**: Uses Python's `secrets` module to issue secure 15-minute challenge tokens.
* **`ham.testing.progress`**: Tracks exam performance for spaced-repetition algorithms.
* **`ham.morse.progress`**: Tracks Koch method progression and WPM capability.
</models>

<engine_features>
## 4. NCVEC & Examination Engine
* The system implements spaced repetition learning [@ANCHOR: swl_spaced_repetition].
* Provides AI-generated explanations debunking incorrect distractors [@ANCHOR: swl_exam_explanations].
* Simulates standard VE exams [@ANCHOR: morse_ve_exam_generation].
* Generates Ham-CAPTCHAs [@ANCHOR: generate_ham_captcha] and verifies answers [@ANCHOR: verify_ham_captcha].
* Tracks Koch method progression [@ANCHOR: morse_koch_progression] and calculates Farnsworth timing [@ANCHOR: morse_farnsworth_timing].
</engine_features>

<dependencies>
## 5. External Dependencies
* **Python:** `redis` (Declared in `__manifest__.py`).
</dependencies>
