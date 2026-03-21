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
        self.test_start_pattern = re.compile(r"Starting Test|test_.*?\s\.\.\.")

        self.current_context = "Global / Module Loading"
        self.capturing = False
        self.captured_blocks = []
        self.current_block = []

    def process_line(self, line):
        if self.test_start_pattern.search(line):
            self.current_context = line.strip()

        is_log_line = self.log_prefix_pattern.match(line)

        if is_log_line:
            if self.safe_log_levels.search(line):
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
        Scans the captured tracebacks to determine which Odoo modules are implicated.
        """
        modules = set()
        # Match standard Odoo namespaces e.g., odoo.addons.ham_base.tests
        addon_pattern = re.compile(r"odoo\.addons\.([a-zA-Z0-9_]+)")
        # Match standard file paths in tracebacks e.g., File ".../ham_logbook/models/..."
        filepath_pattern = re.compile(r"\/([a-zA-Z0-9_]+)\/(?:models|controllers|tests|wizard|daemons|tools)\/.*?\.py")

        for context, block in self.captured_blocks:
            # Search context
            for match in addon_pattern.findall(context):
                modules.add(match)
            for match in filepath_pattern.findall(context):
                modules.add(match)

            # Search the actual traceback lines
            for line in block:
                for match in addon_pattern.findall(line):
                    modules.add(match)
                for match in filepath_pattern.findall(line):
                    modules.add(match)

        # Exclude core Odoo modules to keep the AI focused on the custom codebase
        ignore_list = {'base', 'web', 'mail', 'website', 'bus'}
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


def run_cmd(cmd, extractor=None):
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
    )

    force_killed = False
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

    process.wait()

    # If we force killed the process, the OS will return a non-zero exit code.
    # We must evaluate our Extractor state to determine true test success/failure.
    if force_killed:
        final_errors = len(extractor.captured_blocks) if extractor else 0
        return 1 if final_errors > initial_errors else 0

    return process.returncode


def get_local_modules(base_dir):
    """Scans the repository root for Odoo modules by locating __manifest__.py"""
    mods = []
    for item in os.listdir(base_dir):
        mod_path = os.path.join(base_dir, item)
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


def check_anchors(venv_python, base_dir):
    """Executes the Semantic Anchor DevSecOps linter"""
    print("[*] Scanning documentation and codebase for Semantic Anchors...")
    anchor_script = os.path.join(base_dir, "tools", "verify_anchors.py")
    res = subprocess.run([venv_python, anchor_script, base_dir])
    if res.returncode != 0:
        print(
            "🛑 Halting due to linter/anchor violations. Please review the output above."
        )
        sys.exit(1)


def rebuild_db(db_name):
    """Drops and creates a fresh PostgreSQL database"""
    print("[*] Dropping and Rebuilding Database Schema ({})...".format(db_name))
    subprocess.run(
        ["dropdb", "--if-exists", db_name], check=False, stderr=subprocess.DEVNULL
    )
    subprocess.run(["createdb", db_name], check=True)


def main():
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
        "-u", "--module", help="Specific module to test (defaults to all local modules)"
    )
    parser.add_argument(
        "-e",
        "--error-log",
        default="~/tmp/filtered_test.txt",
        help="Path to save filtered test failures (default: ~/tmp/filtered_test.txt)",
    )

    args = parser.parse_args()

    # Path Resolution
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    venv_python = os.path.join(base_dir, ".venv", "bin", "python")
    odoo_bin = "/usr/bin/odoo"

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
        target_modules = get_local_modules(base_dir)

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
        check_anchors(venv_python, base_dir)
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
        final_rc = run_cmd(cmd, extractor)

    elif args.mode == "integration":
        check_anchors(venv_python, base_dir)
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
            final_rc = run_cmd(test_cmd, extractor)

    elif args.mode == "individual":
        check_anchors(venv_python, base_dir)
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


if __name__ == "__main__":
    main()
