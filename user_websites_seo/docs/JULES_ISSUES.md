# Jules VM Testing Issues - user_websites_seo

## Provisioning
No issues encountered during provisioning.

## Standard Tests
- **Test Skip**: `TestSEOUI.test_01_seo_widget_tour` was skipped.
    - **Reason**: `Failed to detect chrome devtools port after 10.0s.`
    - **Logs**:
      ```
      2026-05-29 02:18:29,023 20673 WARNING zero_sudo odoo.addons.user_websites_seo.tests.test_seo_ui_tour.TestSEOUI.test_01_seo_widget_tour: Chrome headless failed to start:
      [20781:20806:0529/021820.411692:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
      [20818:20818:0529/021822.165363:WARNING:sandbox/policy/linux/sandbox_linux.cc:405] InitializeSandbox() called with multiple threads in process gpu-process.
      [20781:20806:0529/021827.148191:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
      [20781:20781:0529/021827.190976:INFO:components/enterprise/browser/controller/chrome_browser_cloud_management_controller.cc:225] No machine level policy manager exists.
      [20781:20806:0529/021827.442607:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
      [20781:20806:0529/021828.695350:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
      ```
    - **Note**: This appears to be an environment issue with Chrome headless in the Jules VM.
