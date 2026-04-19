# Testing in the Jules VM Environment

When working within the Jules VM on Ubuntu 24.04, the standard `test_runner.py` Linux Mount Namespace isolations (`unshare`) are restricted due to permission limitations of the environment.

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
IN_JULES_VM=1 python3 tools/test_runner.py --provision-jules
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
IN_JULES_VM=1 python3 tools/test_runner.py --already-provisioned
```

This skips the APT operations and starts testing immediately, seamlessly connecting to the local database cluster at `/opt/hams/pgsock`.

You can append standard test runner arguments alongside this flag:

```bash
IN_JULES_VM=1 python3 tools/test_runner.py -m individual -u user_websites --already-provisioned
IN_JULES_VM=1 python3 tools/test_runner.py -m integration --already-provisioned
```

## 3. Testing a Single Odoo Module

To test a single Odoo module specifically without running the entire suite, use the `-m individual` flag combined with `-u <module_name>`.

For example, to test the `user_websites` module:

```bash
IN_JULES_VM=1 python3 tools/test_runner.py -m individual -u user_websites --already-provisioned
```

## Note on Python Execution

When running the tests under `--provision-jules` or `--already-provisioned`, the system-installed Python (`/usr/bin/python3`) is utilized rather than the local `.venv`, ensuring that global Debian/Ubuntu python packages associated with the global Odoo 19 install remain accessible.
