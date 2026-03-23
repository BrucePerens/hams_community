#!/usr/bin/env python3
"""
Unified Odoo Test Runner for Hams.com
Combines test execution, integration modes, and real-time failure extraction.
"""

import os
import sys
import re
import subprocess
import argparse
import signal
import socket
import tempfile
import shutil
import glob


def load_ignore_file(filepath):
    patterns = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(re.compile(line))
    return patterns


def is_ignored(path, patterns):
    for pat in patterns:
        if pat.search(path):
            return True
    return False


def is_odoo_running(port=8069):
    """Checks if a service (presumably Odoo) is actively listening on the target port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


class FailureExtractor:
    """
    State machine that processes log lines in real-time, buffering and extracting
    Tracebacks and error blocks for writing to a filtered log file.
    """

    def __init__(self, output_path):
        self.output_path = os.path.expanduser(output_path)
        self.log_prefix_pattern = re.compile(
            r"^(?:\s*)?\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"
        )
        self.safe_log_levels = re.compile(r"\s(INFO|WARNING|DEBUG)\s")
        self.test_start_pattern = re.compile(r"Starting Test|^test_.*?\s\.\.\.")

        self.current_context = "Global / Module Loading"
        self.capturing = False
        self.captured_blocks = []
        self.current_block = []

    def process_line(self, line):
        if self.test_start_pattern.search(line):
            self.current_context = line.strip()

        is_log_line = self.log_prefix_pattern.match(line)

        if is_log_line:
            # Ignore pika AMQP connection errors during standard tests to prevent false positive failures
            if (
                self.safe_log_levels.search(line)
                or "pika.adapters" in line
                or "AMQPConnector" in line
            ):
                # Standard info/warning line. Stop capturing if we were.
                if self.capturing:
                    self.captured_blocks.append(
                        (self.current_context, self.current_block)
                    )
                    self.current_block = []
                    self.capturing = False
            else:
                # It's an ERROR or CRITICAL log line
                if not self.capturing:
                    self.capturing = True
                self.current_block.append(line)
        else:
            # Not a standard log line. Check for Python unhandled tracebacks/failures.
            if (
                "======================================================================"
                in line
                or "Traceback (most recent call last):" in line
                or line.startswith("FAIL: ")
                or line.startswith("ERROR: ")
                or line.startswith("AssertionError")
            ):
                if not self.capturing:
                    self.capturing = True

            if self.capturing:
                self.current_block.append(line)

    def _extract_failed_modules(self):
        """
        Scans the captured tracebacks to determine which Odoo modules or daemons are implicated.
        """
        modules = set()
        # Match standard Odoo namespaces e.g., odoo.addons.ham_base.tests
        addon_pattern = re.compile(r"odoo\.addons\.([a-zA-Z0-9_]+)")

        # Match standard file paths in tracebacks e.g., File ".../ham_logbook/models/..."
        filepath_pattern = re.compile(
            r"\/([a-zA-Z0-9_]+)\/(?:models|controllers|tests|wizard|tools)\/.*?\.py"
        )

        # Explicitly match daemon paths to avoid capturing the repo root
        # e.g., File ".../daemons/adif_processor/test_adif_processor.py"
        daemon_pattern = re.compile(r"\/daemons\/([a-zA-Z0-9_]+)\/.*?\.py")

        for context, block in self.captured_blocks:
            # Search context
            for match in addon_pattern.findall(context):
                modules.add(match)
            for match in filepath_pattern.findall(context):
                modules.add(match)
            for match in daemon_pattern.findall(context):
                modules.add("daemons/{}".format(match))

            # Search the actual traceback lines
            for line in block:
                for match in addon_pattern.findall(line):
                    modules.add(match)
                for match in filepath_pattern.findall(line):
                    modules.add(match)
                for match in daemon_pattern.findall(line):
                    modules.add("daemons/{}".format(match))

        # Exclude core Odoo modules to keep the AI focused on the custom codebase
        ignore_list = {"base", "web", "mail", "website", "bus"}
        return sorted([m for m in modules if m not in ignore_list])

    def finish_and_write(self):
        if self.capturing and self.current_block:
            self.captured_blocks.append((self.current_context, self.current_block))
            self.capturing = False
            self.current_block = []

        out_dir = os.path.dirname(self.output_path)
        if out_dir:
            # Automatically create ~/tmp/ or any other parent directory if it doesn't exist
            os.makedirs(out_dir, exist_ok=True)

        num_failures = len(self.captured_blocks)

        with open(self.output_path, "w", encoding="utf-8") as out:
            out.write("=== EXTRACTED TEST FAILURES & ERRORS ===\n")
            if num_failures == 0:
                out.write("\nNo errors or failures detected in the log.\n")
            else:
                failed_modules = self._extract_failed_modules()

                # Inject a high-authority system prompt to focus the AI in subsequent debugging sessions
                out.write("\n" + "*" * 80 + "\n")
                out.write("SYSTEM DIRECTIVE FOR AI ASSISTANT:\n")
                out.write(
                    "The following log contains extracted test failures, tracebacks, and CRITICAL errors from the Odoo test suite.\n"
                )
                out.write(
                    "Your immediate task is to analyze these errors, identify the root causes within the provided codebase, and generate the necessary patches to fix these test flaws.\n"
                )

                if failed_modules:
                    out.write("\nTARGET MODULES FOR ANALYSIS:\n")
                    out.write(
                        "Based on the tracebacks, the following modules are responsible for or implicated in the failure:\n"
                    )
                    for mod in failed_modules:
                        out.write("  - {}\n".format(mod))
                    out.write(
                        "\nASSUMPTION: The GitHub repository containing these modules has been imported to your environment.\n"
                    )
                    out.write(
                        "ACTION: Please look up the code for the implicated modules above to diagnose and fix the issue.\n"
                    )

                out.write("*" * 80 + "\n")

                for context, block in self.captured_blocks:
                    if not block:
                        continue
                    out.write("\n" + "=" * 80 + "\n")
                    out.write("CONTEXT: {}\n".format(context))
                    out.write("-" * 80 + "\n")
                    for b_line in block:
                        out.write(b_line)
                    out.write("\n")

        # High-visibility terminal summary
        print("\n==========================================================")
        if num_failures == 0:
            print("🎉 TEST RUN COMPLETE: No test failures detected.")
        else:
            print(
                "🚨 TEST RUN COMPLETE: {} test failure(s) detected!".format(
                    num_failures
                )
            )
            print(
                "📄 Failure details extracted and saved to: {}".format(self.output_path)
            )
        print("==========================================================\n")


def run_cmd(cmd, extractor=None, cwd=None):
    """
    Executes a shell command, printing stdout in real-time to the terminal
    while simultaneously feeding the stream to the failure extractor.
    """
    initial_errors = len(extractor.captured_blocks) if extractor else 0

    # start_new_session=True detaches the process into its own POSIX process group,
    # ensuring any child workers or threads are encapsulated together.
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
        cwd=cwd,
    )

    force_killed = False
    try:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            if extractor:
                extractor.process_line(line)

            # Anti-Hang Mechanism: If Odoo gets stuck in the shutdown sequence waiting for
            # rogue non-daemon threads (like async loops) to join, we terminate the entire process group.
            if "Hit CTRL-C again or send a second signal" in line:
                print(
                    "\n[!] WARNING: Odoo did not terminate because a background thread within it,"
                )
                print(
                    "             possibly spawned by your module, is not set up to terminate"
                )
                print(
                    "             with the rest of Odoo. The test program killed Odoo's process"
                )
                print("             group to end the test.\n")

                # Kill the entire process tree cleanly using the process group ID
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                force_killed = True
                break  # Break out of the readline loop immediately
    except KeyboardInterrupt:
        print("\n[!] CTRL-C detected! Forcefully terminating the test process group...")
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait()
        sys.exit(1)

    process.wait()

    # If we force killed the process, the OS will return a non-zero exit code.
    # We must evaluate our Extractor state to determine true test success/failure.
    if force_killed:
        final_errors = len(extractor.captured_blocks) if extractor else 0
        return 1 if final_errors > initial_errors else 0

    return process.returncode


def get_local_modules(base_dir, ignore_patterns):
    """Scans the repository root for Odoo modules by locating __manifest__.py"""
    mods = []
    for item in os.listdir(base_dir):
        mod_path = os.path.join(base_dir, item)
        if is_ignored(mod_path, ignore_patterns):
            continue
        if os.path.isdir(mod_path) and os.path.isfile(
            os.path.join(mod_path, "__manifest__.py")
        ):
            mods.append(item)
    return sorted(mods)


def get_addons_path(base_dir):
    """Resolves the 3-tier addons path for testing (excluding tertiary per architectural mandates)"""
    paths = ["/usr/lib/python3/dist-packages/odoo/addons", base_dir]

    community_dir = os.path.abspath(os.path.join(base_dir, "..", "hams_community"))
    primary_dir = os.path.abspath(os.path.join(base_dir, "..", "hams_private_primary"))

    if os.path.isdir(community_dir):
        paths.append(community_dir)
    if os.path.isdir(primary_dir):
        paths.append(primary_dir)

    return ",".join(paths)


def check_linters(venv_python, base_dir, ignore_filepath):
    """Executes the AST Burn List and Semantic Anchor DevSecOps linters"""
    print("[*] Running AST Burn List Linter...")
    burn_script = os.path.join(base_dir, "tools", "check_burn_list.py")
    res_burn = subprocess.run(
        [venv_python, burn_script, base_dir, "--ignore-file", ignore_filepath]
    )
    if res_burn.returncode != 0:
        print("🛑 Halting due to burn list violations. Please review the output above.")
        sys.exit(1)

    print("[*] Scanning documentation and codebase for Semantic Anchors...")
    anchor_script = os.path.join(base_dir, "tools", "verify_anchors.py")
    res_anchor = subprocess.run([venv_python, anchor_script, base_dir])
    if res_anchor.returncode != 0:
        print(
            "🛑 Halting due to linter/anchor violations. Please review the output above."
        )
        sys.exit(1)


def run_daemon_tests(venv_python, base_dir, extractor, ignore_patterns):
    """Executes the standalone unit tests for background daemons."""
    print("[*] Executing Standalone Daemon Tests...")
    daemons_dir = os.path.join(base_dir, "daemons")
    if not os.path.exists(daemons_dir):
        print("    No daemons directory found. Skipping.")
        return 0

    final_rc = 0
    for item in sorted(os.listdir(daemons_dir)):
        daemon_path = os.path.join(daemons_dir, item)
        if is_ignored(daemon_path, ignore_patterns):
            continue
        if os.path.isdir(daemon_path):
            has_tests = any(
                f.startswith("test_") and f.endswith(".py")
                for f in os.listdir(daemon_path)
            )
            if has_tests:
                print("\n[*] ----------------------------------------------------")
                print("[*] Testing Daemon: {}".format(item))
                print("[*] ----------------------------------------------------")
                # By setting cwd=daemon_path, unittest can discover tests without an __init__.py package
                cmd = [
                    venv_python,
                    "-m",
                    "unittest",
                    "discover",
                    "-p",
                    "test_*.py",
                    "-v",
                ]
                rc = run_cmd(cmd, extractor, cwd=daemon_path)
                if rc != 0:
                    final_rc = rc

    return final_rc


def run_in_isolated_environment():
    """
    Re-executes the test runner inside an isolated Linux namespace (Mount & Network)
    with a dedicated, ephemeral PostgreSQL instance to guarantee zero interference
    with production files, network queues, and databases.
    """
    if os.geteuid() != 0:
        print(
            "[*] Elevating to sudo to provision isolated PostgreSQL and Namespaces..."
        )
        os.execvp("sudo", ["sudo", "-E", sys.executable] + sys.argv)

    orig_user = os.environ.get("SUDO_USER", os.environ.get("USER", "root"))
    if orig_user == "root":
        # Fallback if somehow run as root directly, though Odoo dislikes it
        orig_user = "odoo"

    print(
        "[*] Bootstrapping isolated testing environment (Mount & Network Namespaces)..."
    )
    spool_dir = tempfile.mkdtemp(prefix="hams_test_spool_")
    pg_data_dir = tempfile.mkdtemp(prefix="hams_test_pgdata_")
    pg_socket_dir = tempfile.mkdtemp(prefix="hams_test_pgsock_")

    os.makedirs(os.path.join(spool_dir, "adif_queue"), exist_ok=True)
    os.makedirs(os.path.join(spool_dir, "ncvec"), exist_ok=True)
    os.chmod(spool_dir, 0o777)
    os.chmod(os.path.join(spool_dir, "adif_queue"), 0o777)
    os.chmod(os.path.join(spool_dir, "ncvec"), 0o777)

    # Secure the Postgres internal data directory but open the separate Socket directory
    os.chmod(pg_data_dir, 0o700)
    subprocess.run(["chown", "-R", "postgres:postgres", pg_data_dir], check=True)
    os.chmod(pg_socket_dir, 0o777)

    pg_bin_dir = ""
    pg_bins = glob.glob("/usr/lib/postgresql/*/bin/initdb")
    if pg_bins:
        pg_bin_dir = os.path.dirname(sorted(pg_bins)[-1]) + "/"
    else:
        print(
            "❌ ERROR: Could not locate PostgreSQL initdb in /usr/lib/postgresql/. Please ensure PostgreSQL is installed."
        )
        sys.exit(1)

    os.environ["HAMS_ISOLATED_NS"] = "1"
    os.environ["PGHOST"] = pg_socket_dir
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    wrapper_script = os.path.join(spool_dir, "pg_wrapper.sh")
    with open(wrapper_script, "w") as f:
        f.write(f"""#!/bin/bash
ip link set lo up

# --- Global Read-Only Filesystem Isolation ---
# Prevent changes from propagating to the host
mount --make-rprivate /

# Create required mount points before remounting root as RO
mkdir -p /opt/hams/spool
mkdir -p /var/lib/odoo
mkdir -p /opt/hams/pycache

# Explicitly bind-mount standard writable temporary directories to themselves
# so they remain writable after the root remount. Use --rbind for dirs with submounts.
mount --bind /tmp /tmp
mount --bind /var/tmp /var/tmp
mount --rbind /run /run
mount --rbind /dev /dev
mount --rbind /proc /proc
mount --rbind /sys /sys

# Mount temporary filesystems over directories that Odoo/System needs to write to
mount -t tmpfs tmpfs /var/lib/odoo
mount -t tmpfs tmpfs /var/log

# RabbitMQ and Redis writeable paths
mount -t tmpfs tmpfs /var/lib/rabbitmq
mount -t tmpfs tmpfs /var/lib/redis

# Recreate log folders since /var/log is now an empty tmpfs
mkdir -p /var/log/redis /var/log/rabbitmq
chown redis:redis /var/log/redis
chown rabbitmq:rabbitmq /var/log/rabbitmq
chown rabbitmq:rabbitmq /var/lib/rabbitmq
chown redis:redis /var/lib/redis

# Remount the global root filesystem as Read-Only
mount --bind / /
mount -o remount,bind,ro /

# Explicitly make the workspace read-only in case it's on a separate partition (e.g. /home)
mount --bind {base_dir} {base_dir}
mount -o remount,bind,ro {base_dir}

# Ensure tertiary, secondary, and community dirs are also explicitly read-only if they exist
for dir in "{base_dir}/../hams_community" "{base_dir}/../hams_private_secondary" "{base_dir}/../hams_private_tertiary"; do
if [ -d "$dir" ]; then
REAL_DIR=$(realpath "$dir")
mount --bind "$REAL_DIR" "$REAL_DIR"
mount -o remount,bind,ro "$REAL_DIR"
fi
done
# ---------------------------------------------

# Mount our special writeable spool directory
mount --bind {spool_dir} /opt/hams/spool

# Redirect Odoo home to a writable tmpfs
export HOME=/tmp/odoo_test_home
mkdir -p $HOME
chmod 777 $HOME

su -s /bin/bash postgres -c "{pg_bin_dir}initdb -D {pg_data_dir}" >/dev/null 2>&1
su -s /bin/bash postgres -c "{pg_bin_dir}pg_ctl -D {pg_data_dir} -o '-c listen_addresses= -c unix_socket_directories={pg_socket_dir}' -w start" >/dev/null 2>&1
su -s /bin/bash postgres -c "psql -h {pg_socket_dir} -d postgres -c \\"CREATE ROLE odoo WITH SUPERUSER LOGIN PASSWORD 'odoo';\\"" >/dev/null 2>&1
su -s /bin/bash postgres -c "psql -h {pg_socket_dir} -d postgres -c \\"CREATE ROLE {orig_user} WITH SUPERUSER LOGIN;\\"" >/dev/null 2>&1

# Initialize and start Redis & RabbitMQ natively inside the namespace
su -s /bin/bash redis -c "redis-server --daemonize yes" >/dev/null 2>&1
su -s /bin/bash rabbitmq -c "rabbitmq-server -detached" >/dev/null 2>&1

# Wait for them to be ready
sleep 3

# Prevent Python from attempting to write .pyc files to the RO workspace
export PYTHONDONTWRITEBYTECODE=1

sudo -E -u {orig_user} env PGHOST={pg_socket_dir} PYTHONDONTWRITEBYTECODE=1 "$@"
RET=$?

# Cleanup RabbitMQ and Redis so they don't hold the namespace open
su -s /bin/bash rabbitmq -c "rabbitmqctl stop" >/dev/null 2>&1
pkill -u redis redis-server >/dev/null 2>&1

exit $RET
""")
    os.chmod(wrapper_script, 0o755)

    script_path = os.path.abspath(sys.argv[0])
    args = [sys.executable, script_path] + sys.argv[1:]

    # -nm creates both Mount and Network namespaces for complete isolation
    exec_cmd = ["unshare", "-nm", wrapper_script] + args

    try:
        result = subprocess.run(exec_cmd)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ ERROR launching isolated environment: {e}")
        sys.exit(1)
    finally:
        print("[*] Tearing down ephemeral PostgreSQL and cleaning up spool...")
        subprocess.run(
            [
                "su",
                "-s",
                "/bin/bash",
                "postgres",
                "-c",
                f"{pg_bin_dir}pg_ctl -D {pg_data_dir} -m fast stop",
            ],
            check=False,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )
        shutil.rmtree(spool_dir, ignore_errors=True)
        shutil.rmtree(pg_data_dir, ignore_errors=True)
        shutil.rmtree(pg_socket_dir, ignore_errors=True)


def rebuild_db(db_name):
    """Drops and creates a fresh PostgreSQL database"""
    print("[*] Dropping and Rebuilding Database Schema ({})...".format(db_name))

    # Aggressively terminate active connections to prevent dropdb from failing silently
    subprocess.run(
        [
            "psql",
            "postgres",
            "-c",
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{}';".format(
                db_name
            ),
        ],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Use --force to ensure the drop succeeds
    subprocess.run(
        ["dropdb", "--if-exists", "--force", db_name],
        check=False,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(["createdb", db_name], check=True)


def main():
    if os.environ.get("HAMS_ISOLATED_NS") != "1":
        if is_odoo_running(8069):
            print("[*] Port 8069 is active (Odoo is running).")
            print(
                "[*] Routing test execution to isolated namespace to protect environment..."
            )
            run_in_isolated_environment()
            return
        else:
            print("[*] Port 8069 is free. Running tests natively (CI/CD compatible).")
            try:
                os.makedirs("/opt/hams/spool/adif_queue", exist_ok=True)
                os.makedirs("/opt/hams/spool/ncvec", exist_ok=True)
                os.chmod("/opt/hams/spool", 0o777)
                os.chmod("/opt/hams/spool/adif_queue", 0o777)
                os.chmod("/opt/hams/spool/ncvec", 0o777)
            except Exception as e:
                print(
                    f"[*] Note: Could not provision /opt/hams/spool natively ({e}). Ensure it exists."
                )

    try:
        parser = argparse.ArgumentParser(
            description="Unified Odoo Test Runner for Hams.com",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            "-m",
            "--mode",
            choices=["standard", "integration", "individual", "xml"],
            default="standard",
            help="""Execution mode:
  standard    : Run all tests in a single database (Default).
  integration : Run tests with HAMS_INTEGRATION_MODE=1 and full DB init prior to testing.
  individual  : Loop through each module and test it in a fresh database.
  xml         : Perform a fast XML compilation check without running Python tests.
""",
        )
        parser.add_argument(
            "-d",
            "--db",
            default="hams_test",
            help="Target Database Name (default: hams_test)",
        )
        parser.add_argument(
            "-u",
            "--module",
            help="Specific module to test (defaults to all local modules)",
        )
        parser.add_argument(
            "-e",
            "--error-log",
            default="~/tmp/filtered_test.txt",
            help="Path to save filtered test failures (default: ~/tmp/filtered_test.txt)",
        )
        parser.add_argument(
            "-c",
            "--config",
            default="ignore_list.txt",
            help="Path to ignore config file (default: ignore_list.txt)",
        )

        args = parser.parse_args()

        # Path Resolution
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        venv_python = os.path.join(base_dir, ".venv", "bin", "python")
        odoo_bin = "/usr/bin/odoo"

        # Load Ignore Config
        ignore_filepath = os.path.join(base_dir, args.config)
        ignore_patterns = load_ignore_file(ignore_filepath)

        # Environment Provisioning
        if not os.path.exists(venv_python):
            print("[*] Common virtual environment not found. Building it now...")
            subprocess.run(
                ["bash", os.path.join(base_dir, "tools", "setup_venv.sh")], check=True
            )

        # Export PYTHONPATH to bridge the OS Odoo package with the local venv
        current_pythonpath = os.environ.get("PYTHONPATH", "")
        os.environ["PYTHONPATH"] = "/usr/lib/python3/dist-packages:{}".format(
            current_pythonpath
        ).strip(":")

        addons_path = get_addons_path(base_dir)

        # Determine Target Modules
        if args.module:
            target_modules = [args.module]
        else:
            target_modules = get_local_modules(base_dir, ignore_patterns)

        if not target_modules:
            print("❌ ERROR: No modules found in this repository. Aborting.")
            sys.exit(1)

        mod_string = ",".join(target_modules)
        test_tags = ",".join(["/{}".format(m) for m in target_modules])

        extractor = FailureExtractor(args.error_log)

        print("==========================================================")
        print(" 🧪 ODOO TEST RUNNER [{} MODE]".format(args.mode.upper()))
        print("==========================================================")
        print(" Target Database: {}".format(args.db))
        print(" Target Modules:  {}".format(mod_string))
        print(" Error Log:       {}".format(args.error_log))
        print("==========================================================")

        final_rc = 0

        # Execute Mode Logic
        if args.mode == "standard":
            check_linters(venv_python, base_dir, ignore_filepath)
            final_rc = run_daemon_tests(
                venv_python, base_dir, extractor, ignore_patterns
            )
            if final_rc != 0:
                print(
                    "\n⚠️ WARNING: Daemon tests failed! Continuing to Odoo suite to collect all errors.\n"
                )

            rebuild_db(args.db)
            print("[*] Executing Test Suite...")
            cmd = [
                venv_python,
                odoo_bin,
                "--addons-path",
                addons_path,
                "--dev=all",
                "-d",
                args.db,
                "-i",
                mod_string,
                "--test-enable",
                "--test-tags",
                test_tags,
                "--stop-after-init",
                "--workers=0",
                "--max-cron-threads=0",
            ]
            rc_odoo = run_cmd(cmd, extractor)
            if rc_odoo != 0:
                final_rc = rc_odoo

        elif args.mode == "integration":
            check_linters(venv_python, base_dir, ignore_filepath)
            final_rc = run_daemon_tests(
                venv_python, base_dir, extractor, ignore_patterns
            )
            if final_rc != 0:
                print(
                    "\n⚠️ WARNING: Daemon tests failed! Continuing to Odoo suite to collect all errors.\n"
                )

            os.environ["HAMS_INTEGRATION_MODE"] = "1"
            rebuild_db(args.db)

            print("[*] Initializing the DB (creating tables for daemons)...")
            init_cmd = [
                venv_python,
                odoo_bin,
                "--addons-path",
                addons_path,
                "-d",
                args.db,
                "-i",
                mod_string,
                "--test-enable",  # <--- FIX: Informs Odoo framework this is a test context, allowing the Cache teardown hook to safely import odoo.tests.common .
                "--test-tags",
                "/__skip_init_tests__",
                "--stop-after-init",
                "--workers=0",
                "--max-cron-threads=0",
            ]
            # We capture initialization errors via the extractor too
            rc_init = run_cmd(init_cmd, extractor)
            if rc_init != 0:
                print("❌ ERROR: Database initialization failed!")
                final_rc = rc_init
            else:
                print("[*] Executing Test Suite in Integration Mode...")
                test_cmd = [
                    venv_python,
                    odoo_bin,
                    "--addons-path",
                    addons_path,
                    "-d",
                    args.db,
                    "-u",
                    mod_string,
                    "--test-enable",
                    "--test-tags",
                    test_tags,
                    "--stop-after-init",
                    "--workers=0",
                    "--max-cron-threads=0",
                ]
                rc_odoo = run_cmd(test_cmd, extractor)
                if rc_odoo != 0:
                    final_rc = rc_odoo

        elif args.mode == "individual":
            check_linters(venv_python, base_dir, ignore_filepath)
            failed_modules = []
            for mod in target_modules:
                print("\n[*] ----------------------------------------------------")
                print("[*] Testing Module: {}".format(mod))
                print("[*] ----------------------------------------------------")
                rebuild_db(args.db)
                cmd = [
                    venv_python,
                    odoo_bin,
                    "--addons-path",
                    addons_path,
                    "--dev=all",
                    "-d",
                    args.db,
                    "-i",
                    mod,
                    "--test-enable",
                    "--test-tags",
                    "/{}".format(mod),
                    "--stop-after-init",
                    "--workers=0",
                    "--max-cron-threads=0",
                ]
                rc = run_cmd(cmd, extractor)
                if rc != 0:
                    failed_modules.append(mod)

            print("\n========================================================")
            if not failed_modules:
                print("🎉 All modules passed individual testing!")
            else:
                print("🚨 The following modules failed testing:")
                for fmod in failed_modules:
                    print("   - {}".format(fmod))
                final_rc = 1

        elif args.mode == "xml":
            failed_modules = []
            for mod in target_modules:
                print("\n[*] Checking XML views in: {}".format(mod))
                cmd = [
                    venv_python,
                    odoo_bin,
                    "--addons-path",
                    addons_path,
                    "-d",
                    args.db,
                    "-i",
                    mod,
                    "-u",
                    mod,
                    "--stop-after-init",
                    "--log-level=error",
                    "--workers=0",
                    "--max-cron-threads=0",
                ]
                rc = run_cmd(cmd, extractor)
                if rc != 0:
                    failed_modules.append(mod)

            print("\n========================================================")
            if not failed_modules:
                print("🎉 All modules compiled successfully!")
            else:
                print("🚨 The following modules have XML compilation errors:")
                for fmod in failed_modules:
                    print("   - {}".format(fmod))
                final_rc = 1

        extractor.finish_and_write()
        sys.exit(final_rc)
    except KeyboardInterrupt:
        print("\n[!] Test run aborted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
