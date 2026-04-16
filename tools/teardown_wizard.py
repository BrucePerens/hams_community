#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil


def run_cmd(cmd, ignore_error=False):
    print(f" $ {' '.join(cmd)}")
    try:
        subprocess.run(cmd, shell=False, check=not ignore_error)
    except subprocess.CalledProcessError as e:
        if not ignore_error:
            print(f" [!] Command failed: {e}")


def _as_postgres(cmd_list):
    if os.geteuid() == 0:
        return ["runuser", "-u", "postgres", "--"] + cmd_list
    return ["sudo", "-u", "postgres"] + cmd_list


def prompt_yes_no(question):
    while True:
        resp = input(f"{question} [y/N]: ").strip().lower()
        if resp in ["y", "yes"]:
            return True
        if resp in ["", "n", "no"]:
            return False


def main():
    if os.geteuid() != 0:
        print(
            "[!] This script requires root privileges to remove systemd units and configurations."
        )
        os.execvp("sudo", ["sudo", "-E", sys.executable] + sys.argv)

    print("====================================================")
    print(" 🧹 Hams.com Unified Teardown & Cleanup Wizard")
    print("====================================================\n")

    print("[*] Phase 1: Stopping Primary Gateway Services...")
    run_cmd(["systemctl", "stop", "nginx"], ignore_error=True)
    run_cmd(["systemctl", "stop", "odoo"], ignore_error=True)
    run_cmd(["systemctl", "stop", "pdns"], ignore_error=True)
    run_cmd(["systemctl", "stop", "cloudflared"], ignore_error=True)

    print("\n[*] Phase 2: Hunting and Purging Systemd Daemons & Overrides...")
    systemd_dir = "/etc/systemd/system"
    purged_count = 0

    # Because everything is strictly contained, we only look for symlinks pointing to /opt/hams
    if os.path.exists(systemd_dir):
        # Sort in reverse to ensure .timer units are processed before .service units
        for item in sorted(os.listdir(systemd_dir), reverse=True):
            item_path = os.path.join(systemd_dir, item)

            if os.path.islink(item_path):
                target = os.readlink(item_path)
                if target.startswith("/opt/hams"):
                    print(f"   [-] Found managed symlink: {item} -> {target}")

                    # Stop and disable if it's a service or timer
                    if item.endswith(".service") or item.endswith(".timer"):
                        run_cmd(["systemctl", "stop", item], ignore_error=True)
                        run_cmd(["systemctl", "disable", item], ignore_error=True)

                    # Remove the symlink (lexists safely handles broken links)
                    if os.path.lexists(item_path):
                        os.remove(item_path)
                    purged_count += 1

    if purged_count > 0:
        print("\n[*] Reloading systemd daemon to clear deleted units...")
        run_cmd(["systemctl", "daemon-reload"])

    print("\n[*] Phase 3: Purging Application Config Symlinks...")
    symlinks_to_remove = [
        "/etc/nginx/sites-enabled/hams.com.conf",
        "/etc/powerdns/pdns.d/gsqlite3.conf",
        "/etc/odoo/odoo.conf",
    ]
    for f in symlinks_to_remove:
        if os.path.lexists(f):
            print(f"   [-] Deleting symlink {f}")
            os.remove(f)

    print("\n[*] Phase 4: Wiping FHS Codebase (/opt/hams)...")
    if os.path.exists("/opt/hams"):
        for item in os.listdir("/opt/hams"):
            if item in ["downloads", "test"]:
                continue
            item_path = os.path.join("/opt/hams", item)
            if os.path.isdir(item_path) and not os.path.islink(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        print("   [-] /opt/hams cleaned (preserved /opt/hams/downloads and /opt/hams/test).")
    else:
        print("   [-] /opt/hams already missing.")

    print("\n[*] Phase 5: Data & State Destruction (Interactive)")
    print(
        "WARNING: The following actions will permanently delete user data, domains, and sessions."
    )

    if prompt_yes_no("Drop PostgreSQL 'hams_prod' database?"):
        run_cmd(_as_postgres(["dropdb", "--if-exists", "hams_prod"]), ignore_error=True)
        print("   [-] Database dropped.")

    if prompt_yes_no("Delete Odoo filestore and sessions (/var/lib/odoo)?"):
        if os.path.exists("/var/lib/odoo"):
            # Clean contents but leave directory for the package manager
            run_cmd(
                ["find", "/var/lib/odoo", "-mindepth", "1", "-delete"],
                ignore_error=True,
            )
            print("   [-] Odoo local share wiped.")

    if prompt_yes_no("Delete PowerDNS SQLite database (/var/lib/powerdns)?"):
        if os.path.exists("/var/lib/powerdns/pdns.sqlite3"):
            os.remove("/var/lib/powerdns/pdns.sqlite3")
            print("   [-] PowerDNS zone data wiped.")

    print("\n[*] Phase 6: Purging System Packages (Interactive)")
    if prompt_yes_no(
        "Purge all base packages (odoo, nginx, postgresql, redis, rabbitmq, pdns, etc.)?"
    ):
        pkgs = [
            "postgresql",
            "postgresql-client",
            "postgresql-17-pgvector",
            "nginx",
            "redis-server",
            "rabbitmq-server",
            "python3-redis",
            "python3-pika",
            "sqlite3",
            "pdns-server",
            "pdns-backend-sqlite3",
            "kopia",
            "pgbackrest",
            "certbot",
            "python3-certbot-nginx",
            "python3-venv",
            "build-essential",
            "libpq-dev",
            "python3-dev",
            "bind9-dnsutils",
            "odoo",
        ]
        run_cmd(["apt-get", "purge", "-y"] + pkgs, ignore_error=True)
        run_cmd(["apt-get", "autoremove", "-y"], ignore_error=True)
        print("   [-] Base packages purged.")
    else:
        print("   [-] Package purge skipped.")

    print("\n====================================================")
    print(" ✅ Teardown Complete! The system has been sanitized.")
    print("====================================================\n")


if __name__ == "__main__":
    main()
