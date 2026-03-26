# 📻 Tactical AUXCOMM Simulator (`ham_auxcomm_training`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
A tabletop simulator and spaced-repetition engine for NIMS/ICS doctrines.
It injects its technical manual on install.
[@ANCHOR: doc_inject_ham_auxcomm]
[@ANCHOR: view_auxcomm_simulator_page]
[@ANCHOR: api_exam_error]
</overview>

<models_and_views>
## 2. Models & Views
* **`ham.auxcomm.scenario`**: Defines the tabletop environment.
  [@ANCHOR: auxcomm_scenario_model]
  [@ANCHOR: view_auxcomm_scenario_form]
  [@ANCHOR: view_auxcomm_scenario_list]
* **`ham.auxcomm.inject`**: Defines the specific operations and NIMS violations within a scenario.
  [@ANCHOR: auxcomm_inject_model]
  [@ANCHOR: view_auxcomm_inject_form]
* **`ham.auxcomm.course`**: Defines the curriculum courses.
  [@ANCHOR: view_auxcomm_course_list]
* **`ham.auxcomm.lesson`**: Defines the sequential instructional material.
  [@ANCHOR: view_auxcomm_lesson_form]
* **`ham.auxcomm.question`**: Defines the knowledge checks and spaced-repetition pool.
  [@ANCHOR: view_auxcomm_question_form]
</models_and_views>

<dependencies>
## 3. External Dependencies
* **Python:** None (Declared in `__manifest__.py`).
</dependencies>
