# Proposal 14: Intelligent Hardware Relay & Diagnostic Wizard

## 1. Architectural Context
The current local hardware relay (`hams_local_relay.py`) hardcodes the `rigctld` startup command to use a dummy rig (`-m 1`). Non-technical users struggle to manually edit hidden `.vbs` or `.sh` scripts to specify their unique COM ports and baud rates. Furthermore, if the Hamlib installation fails or is missing, the web UI simply throws a generic timeout error.

## 2. Integration Design

### A. Local Diagnostic & Setup UI
**Targets:** `daemons/hams_local_relay/hams_local_relay.py`
* **Diagnostic Engine:** Add logic to the Flask app to search for the `rigctld` binary upon startup (e.g., checking relative paths for `.exe` on Windows, or utilizing `shutil.which` on macOS/Linux).
* **Missing Software Route:** If the binary is missing, requests to the new `http://127.0.0.1:8089/setup` route will render a clean, local HTML page stating that the prerequisite software is missing, providing a direct hyperlink back to the animated installation instructions hosted on the Odoo server.
* **Configuration Wizard:** If the software is present, the `/setup` route uses `serial.tools.list_ports` to auto-discover connected USB radios. It allows the user to select their radio model from a dropdown, saves the configuration to a local JSON file (`hams_relay_config.json`), and automatically restarts the background `rigctld` process with the correct arguments.

### B. Web Shack Gateway
**Targets:** `ham_shack/static/src/js/web_shack.js`
* **The Fix:** When the Web Shack mounts, it pings the local relay's `/status` endpoint. If the relay reports it is still running the dummy rig (`-m 1`), the Web Shack UI will display a prominent "Configure Radio" button that redirects the user's browser to the local `http://127.0.0.1:8089/setup` wizard.

## 3. BDD Acceptance Criteria
* **Story:** As a non-technical operator, I want a visual interface to select my radio's USB port so I don't have to edit code.
    * *Given* the `hams_local_relay.py` is running
    * *When* the user navigates to `/setup`
    * *Then* it MUST display available COM ports and save the selection to a local config file.
* **Story:** As a user who botched the installation, I want to know exactly what went wrong.
    * *Given* the `rigctld` binary is missing from the directory
    * *When* the user visits the setup page
    * *Then* the relay MUST render an error page guiding them to the official installation documentation.
