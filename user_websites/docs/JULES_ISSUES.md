# Issues encountered while testing in Jules VM

## Issue 1: Permission Error during Jules Provisioning

When running the initial provisioning script `IN_JULES_VM=1 python3 tools/test.py --provision-jules -u user_websites` without `sudo`, it fails with a `PermissionError` when trying to modify APT sources.

```
Traceback (most recent call last):
  File "/app/tools/test.py", line 893, in <module>
    main()
  File "/app/tools/test.py", line 850, in main
    provision_jules(base_dir)
  File "/app/tools/test.py", line 668, in provision_jules
    infrastructure.provision_static_files(run_sys, env_vars, environment="prod")
  File "/app/tools/infrastructure.py", line 1697, in provision_static_files
    fd = os.open(path, flags, int(file_spec.get("mode", "644"), 8))
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: '/etc/apt/sources.list.d/odoo.list'
```

## Issue 2: Missing `setuptools` during sudo Jules Provisioning

Running the provisioning script with `sudo` (`IN_JULES_VM=1 sudo python3 tools/test.py --provision-jules -u user_websites`) fails due to a missing `setuptools` module when trying to build PyPDF2.

```
Traceback (most recent call last):
  File "/mnt/upper/tmp/PyPDF2-2.12.1/setup.py", line 1, in <module>
    from setuptools import setup, find_packages
ModuleNotFoundError: No module named 'setuptools'
Traceback (most recent call last):
  File "/app/tools/test.py", line 893, in <module>
    main()
  File "/app/tools/test.py", line 749, in main
    setup_namespace_and_run_tests(real_log_dir, sys_args)
  File "/app/tools/test.py", line 535, in setup_namespace_and_run_tests
    infrastructure.provision_static_files(_safe_run, dict(os.environ), environment="test", dest_dir="/mnt/upper")
  File "/app/tools/infrastructure.py", line 1730, in provision_static_files
    hook(env_vars or {}, dest_dir, path, run_cmd_func)
  File "/app/tools/infrastructure.py", line 108, in hook_install_pypdf2
    run_cmd_func(['python3', 'setup.py', '--command-packages=stdeb.command', 'bdist_deb'])
  File "/app/tools/test.py", line 532, in _safe_run
    def _safe_run(cmd, **kw): return subprocess.run(cmd, check=True, **kw)
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['python3', 'setup.py', '--command-packages=stdeb.command', 'bdist_deb']' returned non-zero exit status 1.
```

## Issue 3: Missing `psql` during Standard Test Run

When running standard tests `python3 tools/test.py -u user_websites`, it fails because PostgreSQL is not installed or `psql` is not in the PATH.

```
[*] Dropping and Rebuilding Database Schema (hams_test)...
❌ ERROR: Could not find PostgreSQL binary: psql
```
