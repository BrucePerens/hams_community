# Jules VM Issues - manual_library

## Provisioning Issues
No issues encountered during provisioning.

## Test Issues
Standard tests for `manual_library` module failed with 3 issues detected.

### 1. ORM Logic Deletion Restriction Error
`TestManualORMLogic.test_04_parent_deletion_restriction` failed with a `psycopg2.errors.RestrictViolation`.
- **Traceback**:
  ```
  File "/app/manual_library/tests/test_orm_logic.py", line 78, in test_04_parent_deletion_restriction
    self.article_a.unlink()
  ...
  psycopg2.errors.RestrictViolation: update or delete on table "knowledge_article" violates RESTRICT setting of foreign key constraint "knowledge_article_parent_id_fkey" on table "knowledge_article"
  DETAIL:  Key (id)=(89) is referenced from table "knowledge_article".
  ```

### 2. UI Tour Failure (TOC Tour)
`TestManualLibraryUITours.test_01_manual_toc_tour` failed or hung.
- **Log**: `TOUR FAILED OR HUNG. DUMPING COMPILED ASSETS`

### 3. General Test Error
The test run finished with: `0 failed, 1 error(s) of 32 tests when loading database 'hams_test'`.
This seems related to the first error mentioned above.
