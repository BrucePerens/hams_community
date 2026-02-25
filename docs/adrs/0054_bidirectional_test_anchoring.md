# ADR 0054: Bidirectional Test-to-Code Semantic Anchoring

## Status
Accepted

## Context
ADR-0004 established Semantic Anchors mapping requirements to code. ADR-0052 extended this to map linter bypasses to tests. However, standard business logic lacks explicit, discoverable links to the unit tests that verify it. When a developer refactors code at a specific anchor, it is not immediately clear which test anchor covers that logic.

## Decision
We mandate explicit bidirectional referencing between source code anchors and test anchors.
1. **Source Code:** Near a semantic anchor in the execution logic, developers MUST add a comment pointing to the test anchor(s) verifying it. Example: `# Verified by [%ANCHOR: example_test_qso_cross_match]`.
2. **Test Code:** In the test method, developers MUST add an anchor for the test itself AND a comment referencing the source code anchor it verifies. Example: `# Tests [%ANCHOR: example_qso_cross_match]`.
3. **Frontend 
Web Tours (JavaScript):** User-side JS interactions (OWL components or HTML UI flows) MUST utilize bidirectional anchoring between the UI source and the Web Tour. Example (JS): `// Verified by [%ANCHOR: example_test_tour_my_feature]` -> `// Tests [%ANCHOR: example_my_feature]`.

## Consequences
* **Positive:** Drastically improves test discoverability. Ensures that when code is modified, the corresponding tests are easily identified and updated.
* **Negative:** Increases comment boilerplate slightly. Requires discipline to maintain the dual references when renaming anchors.
