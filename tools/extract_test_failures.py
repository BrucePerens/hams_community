#! /usr/bin/env python3
import re
import sys


def extract_failures(input_path, output_path):
    # Regex to match a standard timestamped log prefix, ignoring optional tags like
    # Matches things like "2026-03-02 08:05:14,228" or "2026-03-02 08:05:14,228"
    log_prefix_pattern = re.compile(
        r"^(?:\\s*)?\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}"
    )

    # Regex to identify standard, successful log levels that signal an error block has ended
    safe_log_levels = re.compile(r"\s(INFO|WARNING|DEBUG)\s")

    # Regex to track the current context (which test is running)
    test_start_pattern = re.compile(r"Starting Test|test_.*?\s\.\.\.")

    current_context = "Global / Module Loading"
    capturing = False
    captured_blocks = []
    current_block = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            # 1. Update Context
            if test_start_pattern.search(line):
                current_context = line.strip()

            # 2. Check if this line is a standard timestamped log entry
            is_log_line = log_prefix_pattern.match(line)

            if is_log_line:
                if safe_log_levels.search(line):
                    # It's a standard INFO/WARNING/DEBUG line. Stop capturing.
                    if capturing:
                        captured_blocks.append((current_context, current_block))
                        current_block = []
                        capturing = False
                else:
                    # It's a log line, but it's ERROR, CRITICAL, or a summary result.
                    # We want to start/continue capturing.
                    if not capturing:
                        capturing = True
                    current_block.append(line)
            else:
                # 3. This is NOT a standard log line (e.g. Tracebacks, stdout, SQL dumps, diffs)
                # Check for explicit unit test failure markers
                if (
                    "======================================================================"
                    in line
                    or "Traceback (most recent call last):" in line
                    or line.startswith("FAIL: ")
                    or line.startswith("ERROR: ")
                    or line.startswith("AssertionError")
                ):
                    if not capturing:
                        capturing = True

                # If the capture state is on, record the line
                if capturing:
                    current_block.append(line)

    # Catch anything left open at EOF
    if capturing and current_block:
        captured_blocks.append((current_context, current_block))

    # 4. Write out the isolated failures
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("=== EXTRACTED TEST FAILURES & ERRORS ===\n")

        if not captured_blocks:
            out.write("\nNo errors or failures detected in the log.\n")
            return

        for context, block in captured_blocks:
            # Skip empty blocks just in case
            if not block:
                continue

            out.write("\n" + "=" * 80 + "\n")
            out.write(f"CONTEXT: {context}\n")
            out.write("-" * 80 + "\n")
            for b_line in block:
                out.write(b_line)
            out.write("\n")

    print(
        f"Extraction complete. Found {len(captured_blocks)} error blocks. Saved to {output_path}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_test_failures.py <input_log.txt> <output_log.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    extract_failures(input_file, output_file)
