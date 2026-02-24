# ADR 0052: Linter Bypass Testing Mandate

## Status
Accepted

## Context
To eliminate "cybercrud" and false-positive architectural warnings from the project's strict AST linter (`check_burn_list.py`), we introduced explicit bypass tags (`# burn-ignore`, `# audit-ignore-mail`, `# audit-ignore-search`, and `<!-- audit-ignore-cron -->`).
While these tags allow the CI/CD pipeline to proceed, relying purely on the manual assertion of a human developer or AI agent to verify the safety of the bypassed code introduces a severe vulnerability surface. Without verification, bypasses can easily mask regressions, out-of-memory (OOM) vectors, or privilege escalation flaws.

## Decision
Anywhere there is **ANY** linter bypass comment applied to the codebase, we MUST exhaustively test the operation to ensure its correctness.

1. **Mandatory Specificity:** Generic `# burn-ignore` tags are strictly prohibited. The bypass comment MUST specify the exact rule or pattern being bypassed (e.g., `# burn-ignore-sudo`, `# audit-ignore-mail`, `# audit-ignore-search`).
2. **Mandatory Coverage:** Every single instance of a specific bypass tag MUST be backed by a corresponding automated unit test.
3. **Semantic Anchor Cross-Reference:** ANY bypassed line MUST include an inline comment cross-referencing the specific Semantic Anchor of the test that validates it (e.g., `# burn-ignore-sudo: Tested by [%ANCHOR: unique_name]` or `# audit-ignore-mail: Tested by [%ANCHOR: unique_name]`).
4. **Behavioral Proof:** The test MUST explicitly and mathematically prove that the bypassed architectural requirement is fulfilled. For example:
    * If `<!-- audit-ignore-cron -->` is used, the test must prove that the underlying Python method correctly chunks the dataset and utilizes `_trigger()` to loop.
    * If `# burn-ignore` is used for cryptographic parameter fetching, the test must prove that the secret is securely generated, validated, and resists tampering.
    * If `# audit-ignore-search` is used, the test must prove that the search executes safely and bounds the data correctly without causing an OOM crash or data loss.

## Consequences
* **Positive:** Mathematically protects the system from regressions. Ensures that the linter can be bypassed for valid edge cases without sacrificing the project's strict security and performance boundaries.
* **Negative:** Increases development overhead. Developers and AI agents cannot simply silence a linter warning; they must actively construct a mock environment and test suite to prove the warning is safely handled.
