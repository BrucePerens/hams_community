# Issues found during Jules VM Testing

## Provisioning
No issues found during provisioning.

## Standard Tests
Module: `binary_downloader`

### Test Failures
1. `TestBinaryDownloaderTour.test_binary_install_tour` failed (or was skipped after failing to start Chrome).

**Error Log:**
```
2026-05-29 02:15:42,036 21386 INFO zero_sudo odoo.addons.binary_downloader.tests.test_ui_tours_api: Starting TestBinaryDownloaderTour.test_binary_install_tour ...
2026-05-29 02:15:42,053 21386 INFO zero_sudo odoo.addons.zero_sudo.tests.common: TRACING: Entering start_tour wrapper.
2026-05-29 02:15:42,053 21386 INFO zero_sudo odoo.addons.zero_sudo.tests.common: TRACING: Entering browser_js wrapper.
2026-05-29 02:15:55,713 21386 WARNING zero_sudo odoo.addons.binary_downloader.tests.test_ui_tours_api.TestBinaryDownloaderTour.test_binary_install_tour: Chrome headless failed to start:
[21441:21464:0529/021547.089150:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
[21478:21478:0529/021548.790838:WARNING:sandbox/policy/linux/sandbox_linux.cc:405] InitializeSandbox() called with multiple threads in process gpu-process.
[21441:21464:0529/021553.174761:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
[21441:21441:0529/021553.219785:INFO:components/enterprise/browser/controller/chrome_browser_cloud_management_controller.cc:225] No machine level policy manager exists.
[21441:21464:0529/021553.496941:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
[21441:21464:0529/021554.788415:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
[21441:21441:0529/021555.576474:ERROR:dbus/object_proxy.cc:572] Failed to call method: org.freedesktop.DBus.NameHasOwner: object_path= /org/freedesktop/DBus: unknown error type:
[21441:21464:0529/021555.576620:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon

2026-05-29 02:15:55,717 21386 INFO zero_sudo odoo.addons.binary_downloader.tests.test_ui_tours_api.TestBinaryDownloaderTour.test_binary_install_tour: Chrome Log in: /tmp/odoo_tests/zero_sudo/chrome_logs/chrome_log_20260529_021555_715088_test_binary_install_tour.txt
2026-05-29 02:15:55,717 21386 INFO zero_sudo odoo.addons.binary_downloader.tests.test_ui_tours_api.TestBinaryDownloaderTour.test_binary_install_tour: Removing chrome user profile "/tmp/tmpq1pzrzlk_chrome_odoo"
2026-05-29 02:15:55,725 21386 INFO zero_sudo odoo.addons.zero_sudo.tests.common: TRACING: Exiting browser_js wrapper.
2026-05-29 02:15:55,725 21386 ERROR zero_sudo odoo.addons.zero_sudo.tests.common:
=== TOUR FAILED OR HUNG. DUMPING COMPILED ASSETS ===
2026-05-29 02:15:55,726 21386 ERROR zero_sudo odoo.addons.zero_sudo.tests.common: Dumped compiled JS bundle to /var/tmp/failed_tour_bundle.js
2026-05-29 02:15:55,726 21386 INFO zero_sudo odoo.addons.binary_downloader.tests.test_ui_tours_api: skipped TestBinaryDownloaderTour.test_binary_install_tour : Failed to detect chrome devtools port after 10.0s.
```

**Observation:**
Chrome headless failed to start, causing the UI tour to be skipped and the overall test run to report a failure. This might be due to environment limitations or missing dependencies for Chrome in the Jules VM.
