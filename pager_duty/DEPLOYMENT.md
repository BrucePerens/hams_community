# Pager-Duty Deployment Guide

This document outlines the steps required to deploy the `pager_duty` module and its accompanying standalone monitoring daemons in a strict DevSecOps environment.

## 1. Prerequisites & Dependencies

The OS monitoring daemon requires specific system packages to perform full-chain DNS resolution (`dig`) and Application-Layer PostgreSQL checks.

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y dnsutils libpq-dev python3-dev smartmontools
```

### CentOS/RHEL/AlmaLinux:
```bash
sudo dnf install -y bind-utils postgresql-devel python3-devel smartmontools
```

### Python Dependencies (PEP-668 Virtual Environment):
Switch to your Odoo user and activate your virtual environment before installing:
```bash
pip install psutil psycopg2
```
*Note: If `psycopg2` fails to install, the daemon will gracefully fall back to a Layer-4 TCP socket check for PostgreSQL.*

## 2. Log Monitor Permissions
The `log_monitor.py` daemon runs under the `odoo` user but needs read access to system logs. On Debian/Ubuntu systems, you must add the `odoo` user to the `adm` group:
```bash
sudo usermod -aG adm odoo
```

## 3. Odoo Module Deployment
1. Copy the `pager_duty` directory into your Odoo `addons` path.
2. Update the Odoo app list and install the `Pager Duty` module.
3. Assign the "Pager Duty Admin" group to the relevant administrative users.
4. Configure the shifts in the Calendar module by checking the "Is Pager Duty Shift" box.

## 4. Daemon Deployment (systemd)

We use systemd to manage the standalone monitoring daemons, ensuring they restart on failure and log output to the system journal.

1. Copy the unit files to systemd:
```bash
sudo cp daemons/pager_duty/pager-os-monitor.service /etc/systemd/system/
sudo cp daemons/pager_duty/pager-log-monitor.service /etc/systemd/system/
```
2. Adjust the `User`, `Group`, `WorkingDirectory`, and `ExecStart` paths in the unit files to match your exact environment if they differ from standard `/opt/odoo` paths.
3. Reload systemd and enable the services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pager-os-monitor.service
sudo systemctl enable pager-log-monitor.service
sudo systemctl enable pager-smart-spooler.timer
sudo systemctl start pager-os-monitor.service
sudo systemctl start pager-log-monitor.service
sudo systemctl start pager-smart-spooler.timer
```
4. Verify they are running smoothly:
```bash
sudo systemctl status pager-*.service
sudo journalctl -u pager-os-monitor.service -f
```

## 5. Cloudflare Configuration
To ensure the external HTTP checks do not trigger WAF blocks or rate limits:
1. Log into your Cloudflare dashboard.
2. Navigate to **Security** -> **WAF** -> **Custom Rules**.
3. Create a rule to `Skip` rate limiting and WAF checks if the incoming request matches both the Origin Server IP of the monitoring node AND the HTTP User-Agent equals `HamMonitor/1.0`.
