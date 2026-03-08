# ADR 0070: OS-Level Daemon Restriction & Airgapped Hardware Spooling

## Status
Accepted

## Context
The platform utilizes a CQRS (Command Query Responsibility Segregation) architecture, relying heavily on standalone Python daemons running outside the Odoo WSGI workers to handle high-I/O polling, log tailing, and SRE checks.

Because these daemons execute external binaries, perform network requests, and parse complex regex patterns, they represent a potential Remote Code Execution (RCE) vector. Historically, daemons that needed to read system logs or query hardware were simply run as `root`. This violates the principle of least privilege; if a network-facing daemon running as `root` is compromised, the attacker gains total control of the host operating system.

We must mathematically restrict these daemons at the OS level without breaking their ability to execute necessary system binaries (like `ping`, `curl`, or `pg_dump`) or read hardware telemetry.

## Decision
We mandate a three-tiered defense-in-depth strategy for all standalone daemons deployed alongside the platform.

### 1. Chrooted Privilege De-escalation (For Internal Parsers)
Daemons that do not require external networking or access to global system binaries (e.g., the `pager_log_analyzer.py` Splunk engine) MUST execute a strict isolation sequence upon boot:
* They must start as `root` only to access restricted directories.
* They must immediately `chroot` into their target working directory (e.g., `/var/log`) to blind the process to the rest of the filesystem.
* They must mathematically drop all 40 Linux kernel bounding capabilities (`PR_CAPBSET_DROP`) via `libc.prctl`.
* They must permanently de-escalate their user identity to an unprivileged account (e.g., `nobody:adm`).

### 2. Systemd Sandboxing (For Network/Binary Orchestrators)
Network-facing daemons that must execute external binaries (e.g., the `generalized_monitor.py`) cannot be chrooted without severing their access to `/usr/bin` and critical system libraries. Instead, these daemons MUST be sandboxed directly by the Linux kernel via their systemd `.service` definitions:
* **Immutability:** The entire filesystem must be mounted as read-only (`ProtectSystem=strict`, `ProtectHome=read-only`).
* **Namespace Isolation:** The `/tmp` directory must be replaced with an ephemeral, private mount (`PrivateTmp=true`) to prevent payload staging.
* **Hardware & Privilege Denial:** Physical hardware access must be blocked (`PrivateDevices=true`) and the kernel must ignore any `setuid` bits to prevent privilege escalation via tools like `sudo` (`NoNewPrivileges=true`).
* **Network Constriction:** Sockets must be restricted to standard IP networking (`RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX`), and kernel capabilities must be dropped to the absolute minimum required (e.g., `CapabilityBoundingSet=CAP_NET_RAW` for ICMP pings).

### 3. The Airgapped Hardware Spooling Pattern
A fundamental conflict arises when a network-facing, sandboxed daemon requires telemetry from physical hardware (such as SMART disk health), which necessitates absolute `root` privileges (`CAP_SYS_ADMIN` or `CAP_SYS_RAWIO`).

To resolve this, the architecture MUST be physically split using the **Airgapped Hardware Spooling Pattern**:
* **The Sidecar:** A highly-privileged, network-isolated "sidecar" script executes periodically via a systemd `.timer`. It performs the hardware I/O and writes a serialized JSON state file into a read-only spool directory (e.g., `/var/log/pager_smart_spool.json`).
* **The Monitor:** The unprivileged, sandboxed network daemon simply reads this JSON file.
* **Staleness Protection:** The unprivileged daemon MUST evaluate the file's modification time (`mtime`). If the file is stale, the daemon must fail the check and assume the privileged sidecar has crashed.

## Consequences
* **Security:** The blast radius of a compromised daemon is radically compressed. An attacker gaining RCE inside the generalized monitor cannot manipulate block devices, install rootkits, execute privilege-escalation exploits, or stage payloads in temporary directories.
* **Operational Complexity:** Administrators must manage multiple systemd unit files (`.service` and `.timer`) per feature, and developers must carefully orchestrate file permissions and atomic writes between sidecar spoolers and primary daemons to prevent race conditions during reads.
