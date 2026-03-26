# 📻 Ham Radio Propagation Maps (`ham_propagation`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Live High Frequency (HF) propagation forecasting and Maximum Usable Frequency (MUF) mapping. [@ANCHOR: doc_inject_ham_propagation]
</overview>

<features>
## 2. Features
* Integrates with `ham.space.weather` to drive a lightweight VOACAP-style empirical calculation.
* Returns geographic path polygons intersecting the user's unworked DXCC goals. [@ANCHOR: calculate_muf_paths]
* Fully accessible via an `aria-live` tabular text fallback for visually impaired operators. [@ANCHOR: UX_A11Y_PROPAGATION_TABLE]
* The frontend displays a visual heatmap. [@ANCHOR: UX_FRONTEND_PROPAGATION_DASHBOARD]
</features>

<dependencies>
## 3. External Dependencies
* **Python:** `redis` (Declared in `__manifest__.py`).
</dependencies>
