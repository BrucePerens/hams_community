# JULES ISSUES - database_management

## AI Hallucinations & Laziness
- **`database_management/tests/test_pg_config.py`**: [FIXED] Replaced `hasattr(call[0][0], "as_string")` with `isinstance(call[0][0], (sql.SQL, sql.Composed))`.
- **Linter Rule Proposal**: Propose adding a check to `check_burn_list.py` that flags `hasattr(..., "as_string")` when used on mock call arguments, as it is a common lazy alternative to proper type checking with `psycopg2.sql` classes.

## Fallbacks & Missing Resources
- None identified.

## Zero-Sudo & Micro-Privilege
- Verified compliance.

## Multi-Tenant Awareness
- [RESOLVED] Added justifications and marked models as logically global in `db_stats.py` and `pg_config.py`.

## Security Audit
- [VERIFIED] AST-compliance and parameterization are correctly used.

## UI Tours
- `database_management/static/src/tours/db_bloat_tour.js`: [HARDENED] Added wait steps for breadcrumbs and enabled button state.
- `database_management/static/src/tours/db_slow_query_tour.js`: [HARDENED] Added wait step for breadcrumbs.
