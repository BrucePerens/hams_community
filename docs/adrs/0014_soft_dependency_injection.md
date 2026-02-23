# ADR 0014: Soft Dependency Injection for Documentation

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

## Status
Accepted

## Context
The platform includes comprehensive HTML manuals for every module. These manuals are designed to be read within Odoo's `knowledge` app. However, forcing a strict dependency on `knowledge` in the `__manifest__.py` makes the platform brittle; if an administrator uninstalls the Knowledge app, the entire custom ecosystem would be forcibly uninstalled alongside it.

## Decision
Documentation injection must utilize the Soft Dependency Pattern.
1. Modules MUST NOT list `knowledge` or `manual_library` in their `depends` array.
2. Instead, injection logic is placed inside a `post_init_hook`.
3. The hook explicitly checks for the model's presence (`if 'knowledge.article' in env:`). If present, it safely reads the HTML payload via `odoo.tools.file_open` (to prevent path traversal) and creates the article record natively.

## Consequences
* **Positive:** Highly resilient architecture. Modules can function perfectly without the documentation app installed.
* **Negative:** Documentation records are not tracked by Odoo's standard `ir.model.data` XML registry, meaning they will not automatically update or delete if the underlying module is upgraded or uninstalled.
