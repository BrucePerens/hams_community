# Jules Issues

1. **Jules Provisioning Failure**: When running `python3 tools/test.py --provision-jules`, pip installation fails because it attempts to upgrade system packages (like Werkzeug, which lacks a RECORD file because it was installed via apt).

    ```
    ERROR: Cannot uninstall Werkzeug 3.0.1, RECORD file not found. Hint: The package was installed by debian.
    ```

    Command that caused the error:
    ```
    /usr/bin/python3 -m pip install --break-system-packages -r /app/requirements.txt
    ```

    The test runner (`tools/test.py`) does not properly handle python dependencies that were installed using apt versus pip.

2. **Database Provisioning Issues**: When running subsequent tests via `python3 tools/test.py --already-provisioned`, the testing fails because PostgreSQL roles are not properly created when pip fails. Specifically, the "odoo" role is missing.

    ```
    FATAL:  role "odoo" does not exist
    createdb: error: connection to server on socket "/opt/hams/pgsock/.s.PGSQL.5432" failed: FATAL:  role "odoo" does not exist
    ```

    Command that caused the error:
    ```
    /usr/lib/postgresql/18/bin/createdb hams_test
    ```
