# Provisioning Issues

## Provisioning Error

When running `./tools/test.py --provision-jules`, the following error occurred:
```
/usr/bin/python3: No module named pip
PyPDF2 pip install failed: Command '['/usr/bin/python3', '-m', 'pip', 'install', '--break-system-packages', 'PyPDF2==2.12.1']' returned non-zero exit status 1.
```

The script `test.py` tried to run `/usr/bin/python3 -m pip install` but pip was not installed on the system python.

## Test Run Error

When running `./tools/test.py -u user_websites --already-provisioned`, the following error occurred:
```
"root" execution of the PostgreSQL server is not permitted.
The server must be started under an unprivileged user ID to prevent
possible system security compromise.  See the documentation for
more information on how to properly start the server.
child process exited with exit code 1
initdb: removing contents of data directory "/opt/hams/pgdata"
Traceback (most recent call last):
  File "/app/tools/test.py", line 930, in <module>
    main()
  File "/app/tools/test.py", line 844, in main
    provision_jules(base_dir, already_provisioned=args.already_provisioned)
  File "/app/tools/test.py", line 737, in provision_jules
    subprocess.run([initdb_cmd, "-D", pg_data], check=True)
  File "/home/jules/.pyenv/versions/3.12.13/lib/python3.12/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/usr/lib/postgresql/18/bin/initdb', '-D', '/opt/hams/pgdata']' returned non-zero exit status 1.
```

The script `test.py` tried to run `initdb` as root, which is not permitted.
