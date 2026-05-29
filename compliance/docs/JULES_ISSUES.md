# Jules Issues - compliance module

## Provisioning Issues
(None)

## Test Failures
- `TestComplianceUITour.test_compliance_tour` failed/skipped with: `Failed to detect chrome devtools port after 10.0s.`
  - Context:
    ```
    2026-05-29 01:33:40,835 20225 WARNING zero_sudo odoo.addons.compliance.tests.test_ui_tours.TestComplianceUITour.test_compliance_tour: Chrome headless failed to start:
    [20288:20310:0529/013331.967538:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
    [20323:20323:0529/013333.765186:WARNING:sandbox/policy/linux/sandbox_linux.cc:405] InitializeSandbox() called with multiple threads in process gpu-process.
    [20288:20310:0529/013338.273768:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
    [20288:20288:0529/013338.315590:INFO:components/enterprise/browser/controller/chrome_browser_cloud_management_controller.cc:225] No machine level policy manager exists.
    [20288:20310:0529/013338.610148:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
    [20288:20310:0529/013339.960471:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
    [20288:20288:0529/013340.697032:ERROR:dbus/object_proxy.cc:572] Failed to call method: org.freedesktop.DBus.NameHasOwner: object_path= /org/freedesktop/DBus: unknown error type:
    [20288:20310:0529/013340.697201:ERROR:dbus/bus.cc:405] Failed to connect to the bus: Address does not contain a colon
    ```
