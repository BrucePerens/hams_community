# ADR 0044: Fast-Fail Test Pipeline

## Status
Accepted

## Context
Executing the Odoo test suite requires tearing down and completely rebuilding the PostgreSQL database (`dropdb` and `-i base,target_module`). This process is highly time-consuming. If a developer or AI introduces a simple Python syntax error, XML malformation, or linter violation, discovering it *after* the database rebuild cycle forces the developer to endure massive, unnecessary wait times before they can iterate.

## Decision
The platform MUST employ a Fast-Fail Test Architecture.
1. All testing and initialization scripts (e.g., `START.sh`, GitHub Actions pipelines) MUST front-load static analysis tools.
2. The scripts MUST execute Dependency Pre-Flights, the Burn List Linter, Syntax Checkers, and Semantic Anchor verification sequentially.
3. If any of these static tools detect an error, the script MUST instantly abort (`exit 1`) BEFORE initiating any heavy infrastructure modifications, such as database teardowns or container rebuilds.

## Consequences
* **Positive:** Drastically shortens the feedback loop during development. Prevents testing infrastructure from wasting compute cycles on fundamentally broken code.
* **Negative:** Requires strict maintenance of the `START.sh` pipeline. Developers cannot temporarily bypass the static linters to 'just see if the tests run'.