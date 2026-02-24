# ADR 0029: Hardware-to-Web Airgap Bridge (Native Installers)

## Status
Accepted

## Context
Modern web browsers prevent HTTPS websites from making direct local network calls to physical hardware. Bridging this gap requires a local proxy daemon (`hams_local_relay.py`). Previously, requiring users to manage Python virtual environments and Hamlib binaries manually created unacceptable onboarding friction.

## Decision
The platform MUST provide native, 1-click OS installation packages (e.g., Windows MSI, macOS PKG, Linux DEB) for the local relay. 

1. These native packages will encapsulate the Python runtime, the Flask CORS server, and the Hamlib (`rigctld`) binaries.
2. The installers MUST automatically register the relay as a background service (Windows Startup/Service, macOS launchd, Linux systemd).
3. Users download the native package from the Web Shack, run it once, and go straight to operating without touching a command line.

## Consequences
* **Positive:** Eliminates technical friction. Operators can integrate their physical transceivers with the Web Shack instantly.
* **Negative:** Shifts the maintenance burden to the platform developers, who must now compile and sign native OS packages externally before uploading them to the Odoo instance.
