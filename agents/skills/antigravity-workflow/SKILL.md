---
name: antigravity-workflow
description: Workflow and git commit mandates for the Antigravity agent working on the hams_community project.
---

# Antigravity Workflow Mandates

1. **Automatic Git Commits:** When you complete a task or a logical chunk of work that represents a stable, working state (e.g., after fixing bugs or refactoring), you MUST automatically stage and commit the changes using `git add .` and `git commit -m "..."`. Do not wait for the user to explicitly ask you to commit.
2. **Clear Commit Messages:** Write clear, descriptive commit messages summarizing the technical changes and the rationale behind them.
3. **Turbo Mode Compliance:** If the user is operating in "turbo mode", prioritize execution velocity. Do not block execution by asking for permission or feedback on plans unless it is an absolutely critical, dangerous, or irreversible architectural decision.
