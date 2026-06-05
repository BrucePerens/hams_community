# JULES ISSUES - backup_management

## Missing Resources
- None identified.

## Framework Bugs
- None identified.

## Test Environment Hurdles
- RabbitMQ sometimes takes longer than 5 seconds to start in the Jules VM environment, causing the test runner to report errors (though it usually succeeds on the second attempt or later).
- Initial Chrome headless start-up can be flaky in the VM, but subsequent runs are stable.
