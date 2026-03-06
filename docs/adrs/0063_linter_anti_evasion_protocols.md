# ADR 0063: AST Linter Anti-Evasion Protocols

## Status
Accepted

## Context
The Burn List linter (`check_burn_list.py`) enforces the creation of automated tests when developers bypass architectural rules (e.g., using `# audit-ignore-xpath`). However, LLMs and developers occasionally produce "dead code evasion" (placing the required assertions after a `return` or `raise` statement) or "loop evasion" (wrapping rendering validations like `get_view` inside a `for` loop).

These tactics satisfy the naive presence of the assertion node in the Abstract Syntax Tree (AST) but completely nullify the deterministic execution of the test in the actual CI/CD pipeline.

## Decision
The AST linter's Deep Test Verification phase is upgraded to enforce strict structural integrity:

1.  **Dead Code Block:** The linter will flag any required test assertion that follows a control-flow interrupt (`return`, `raise`, `break`, `continue`) within the same function block as an active evasion attempt.
2.  **Loop Evasion Block:** The linter strictly prohibits wrapping UI rendering validations (`get_view`, `url_open`) inside `for` or `while` loops. This ensures deterministic, O(1) execution paths during UI testing and prevents silent passes on empty lists.

## Consequences
Evasion is mathematically impossible without intentionally subverting the Python execution environment. Developers and AI agents must write genuine, sequentially executed test assertions.
