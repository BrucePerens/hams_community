# Pager-Duty Implementation Test Plan

## Phase 1: Environment Preparation
1. **Isolate the Sandbox:** Ensure the staging environment has Odoo, PostgreSQL, and Redis running. Disable outgoing email delivery in Odoo to prevent spamming test accounts.
2. **Start the Monitor:** Launch the `os_monitor.py` daemon in the background. Tail its output to observe ping and check cycles.
3. **Monitor Redis:** Open a terminal and run `redis-cli monitor | grep pager_rate_limit` to watch cache keys in real-time.

## Phase 2: Simulating Memory Overload
1. Create a temporary script `memory_hog.py` that continuously appends large strings to a list to rapidly consume RAM.
2. Execute the script and monitor system memory via `htop`.
3. Wait for the memory usage to breach the 90% threshold.

## Phase 3: Evaluating Redis Rate-Limiting
1. **First Strike Validation:** Verify in the Redis monitor that a `SETEX pager_rate_limit:os_monitor 60 1` command executes.
2. **Incident Verification:** Open the Odoo UI. Verify one new incident (`INC-AUTO`) from `os_monitor` is created.
3. **Rate Limit Validation:** Leave the memory hog running so the daemon reports the breach again on its next loop.
4. **Cache Hit Verification:** Watch the Redis monitor for a `GET pager_rate_limit:os_monitor` request returning `1`.
5. **Spam Prevention Verification:** Check the Odoo UI to ensure NO duplicate incident was created, confirming the XML-RPC request was safely dropped.

## Phase 4: Teardown
1. Terminate the `memory_hog.py` script.
2. Verify system memory returns to baseline.
3. Wait 60 seconds for the Redis TTL to expire, or run `redis-cli keys pager_rate_limit:*` to confirm clearance.
