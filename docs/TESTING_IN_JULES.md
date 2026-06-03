# Testing in the Jules VM Environment

When working within the Jules VM on Ubuntu 24.04, the standard `test.py` Linux Mount Namespace isolations (`unshare`) are restricted due to permission limitations of the environment.

Instead, the test runner detects the Jules VM automatically via the `IN_JULES_VM` or `JULES_SESSION_ID` environment variables. When detected, the runner bypasses namespace isolations and executes directly.

To facilitate this, new flags have been added to provision the dependencies required for testing natively on the VM.

## Prerequisites

Before running tests, ensure that a `tmp` directory exists in your home folder for log output:

```bash
mkdir -p ~/tmp
```

## 1. Initial Provisioning (First Run)

To bootstrap the local Ubuntu environment with Odoo 19, PostgreSQL, Redis, RabbitMQ, and the required Python dependencies, run the test runner with the `--provision-jules` flag:

```bash
IN_JULES_VM=1 python3 tools/test.py --provision-jules
```

This command will:
- Add the Odoo 19 Nightly APT repository.
- Install `odoo` and other required system dependencies.
- Initialize a local PostgreSQL cluster in `/opt/hams/pgdata` listening on `/opt/hams/pgsock`.
- Provision the necessary PostgreSQL roles (`odoo` and the current user).
- Run the full Odoo test suite sequentially.

## 2. Subsequent Runs (Fast Execution)

Once the Jules environment is successfully provisioned, you do not need to reinstall dependencies. Simply use the `--already-provisioned` flag:

```bash
IN_JULES_VM=1 python3 tools/test.py --already-provisioned
```

This skips the APT operations and starts testing immediately, seamlessly connecting to the local database cluster at `/opt/hams/pgsock`.

You can append standard test runner arguments alongside this flag:

```bash
IN_JULES_VM=1 python3 tools/test.py -m integration --already-provisioned
```

## 3. Targeting Specific Modules (-u flag)

By default, the test runner executes against all local modules. To restrict the testing scope to a single module (which saves significant time), use the `-u <module_name>` flag.

This flag works globally across **all** execution modes (`standard`, `integration`, `individual`, `xml`, `downloads`).

**Examples:**

Run the standard test suite but ONLY for the `user_websites` module:
```bash
IN_JULES_VM=1 python3 tools/test.py -u user_websites --already-provisioned
```

Run integration tests specifically for `pager_duty`:
```bash
IN_JULES_VM=1 python3 tools/test.py -m integration -u pager_duty --already-provisioned
```

Run the highly isolated individual test mode for `zero_sudo`:
```bash
IN_JULES_VM=1 python3 tools/test.py -m individual -u zero_sudo --already-provisioned
```

## Note on Python Execution

When running the tests under `--provision-jules` or `--already-provisioned`, the system-installed Python (`/usr/bin/python3`) is utilized rather than the local `.venv`, ensuring that global Debian/Ubuntu python packages associated with the global Odoo 19 install remain accessible.

## 4. Handling UI Tour Failures & Headless Chrome Watchdogs

> **NOTICE:** For the exhaustive, centralized guide on constructing resilient UI tours, you MUST consult [docs/LLM_WRITING_TOURS.md](LLM_WRITING_TOURS.md).

**CRITICAL:** The platform natively patches `HttpCase.browser_js` to suppress fatal headless Chrome teardown crashes (e.g., `Fetch API Error`, "Owl un-mounted component", and "element below a modal"). **You MUST NOT use `@unittest.skip` to evade UI tour failures.** If a tour fails, you must fix the underlying JavaScript logic or race condition.

Due to the asynchronous nature of Odoo 19's Owl UI framework, tours can still suffer from race conditions where the tour executor attempts to click elements before they are fully rendered (especially modals and wizards).

To guarantee architectural compliance and stabilize the build, you MUST utilize the centralized DOM wait macros provided by `zero_sudo`.

**Import the Utilities:**
```javascript
import { TourUtils } from "@zero_sudo/js/tour_utils";
```

**Available Wait Macros:**
* `TourUtils.waitForAbsence(selector, description)`: Pauses the tour until the element is entirely removed from the DOM (e.g., waiting for an RPC loading overlay to vanish).

**Usage Example:**
```javascript
steps: () => [
    {
        content: "Click open wizard",
        trigger: 'button[name="action_confirm"]',
        run: 'click',
    },
    { trigger: '.modal-dialog', run: function() {} }, // Native DOM polling
    {
        content: "Interact with wizard",
        trigger: 'button[name="action_confirm"]',
        run: 'click',
    }
]
```

## 5. Linter and Anchor Verification (AI Guidance)

When operating in this environment, any code generated is strictly audited by two custom DevSecOps tools. You should actively test your output against these tools:

* **`tools/check_burn_list.py`**: A strict AST (Abstract Syntax Tree) linter that enforces architectural mandates (e.g., Zero-Sudo, safe dynamic SQL, UI tour stability).
* **`tools/verify_anchors.py`**: A script that enforces bidirectional traceability between source code, tests, and documentation using `[@ANCHOR: ...]` tags.

**CRITICAL GUIDANCE FOR AI ASSISTANTS:** If you encounter a confusing error or failure from either of these scripts in your test logs, **DO NOT GUESS**. You possess the ability to read files. You MUST autonomously fetch and read the source code of `tools/check_burn_list.py` and `tools/verify_anchors.py`.

Their internal source code contains explicit `[!] DIAGNOSTIC FOR AI` messages, regex patterns, and detailed AST matching logic. Reading their source code will instantly explain exactly what formatting or architectural rule you violated and how to correct it.
