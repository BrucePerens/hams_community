# Jules VM Provisioning & Testing Issues

When running the `test.py` provisioning step (`IN_JULES_VM=1 python3 ./tools/test.py --provision-jules`) and testing step (`IN_JULES_VM=1 python3 ./tools/test.py -u user_websites --already-provisioned`), the following errors were encountered:

1. Manifest Parse Error in `hams_test`
   ```
   ❌ ERROR: Failed to parse /app/hams_test/__manifest__.py: invalid syntax (<unknown>, line 35)
   ```

2. Dependency Graph Linter Failure
   ```
   [*] Running Manifest Dependency Graph Linter...
   🛑 Halting due to manifest load-order violations.
   ```

3. Permissions Error during Test Reporting
   ```
   Exception ignored in atexit callback: <bound method FailureExtractor.finish_and_write of <__main__.FailureExtractor object at 0x7f3e38b661b0>>
   Traceback (most recent call last):
     File "/app/./tools/test.py", line 228, in finish_and_write
       with open(self.output_path, "w", encoding="utf-8") as out:
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   PermissionError: [Errno 13] Permission denied: '/opt/hams/spool/filtered_test.txt'
   ```
