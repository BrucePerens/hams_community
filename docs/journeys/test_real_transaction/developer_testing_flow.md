# Developer Testing Journey

This journey describes the lifecycle of a test execution using the `RealTransactionCase` facility.

1.  **Test Initialization**: The test runner starts a test class inheriting from `RealTransactionCase`.
2.  **Environment Setup**: Inside `setUp()`, the facility performs cursor hijacking ([@ANCHOR: cursor_hijacking]) to provide a real database connection.
3.  **State Snapshot**: The facility records the current state of the database ([@ANCHOR: leak_snapshotting]) to enable later leak detection.
4.  **ORM Instrumentation**: The `BaseModel.create` method is instrumented ([@ANCHOR: orm_instrumentation]) to track any records created by the developer during the test.
5.  **Test Execution**: The developer's test code runs, potentially performing multiple `self.env.cr.commit()` calls.
6.  **Teardown Initiation**: When the test finishes (successfully or not), `tearDown()` is called.
7.  **Automated Cleanup**: The facility attempts to delete all tracked records ([@ANCHOR: automated_cleanup]) in multiple passes.
8.  **Leak Verification**: The facility compares the final database state against the initial snapshot ([@ANCHOR: leak_verification]).
9.  **Environment Restoration**: The ORM and cursor factory are restored to their original state, and the real database connection is closed.
