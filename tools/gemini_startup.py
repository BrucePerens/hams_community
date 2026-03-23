#!/usr/bin/env python3
"""
gemini_startup.py
Generates a highly-focused initialization payload for Gemini sessions.
Combines uncommitted/modified Git files with critical architectural docs,
relying on Gemini's GitHub integration to fetch the rest of the repository dynamically.
"""

import os
import subprocess
import argparse

IGNORE_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", "env"}
IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".zip",
    ".tar",
    ".gz",
    ".pdf",
    ".sqlite3",
}


def get_git_root():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return os.path.abspath(".")


def get_github_info(root_dir):
    """
    Determines the GitHub username and repository name.
    Prompts the user for their username if it's not cached locally.
    """
    user_file = os.path.join(root_dir, ".github_user")
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            github_user = f.read().strip()
    else:
        github_user = input(
            "Enter your GitHub username (for open source context): "
        ).strip()
        if github_user:
            with open(user_file, "w", encoding="utf-8") as f:
                f.write(github_user + "\n")

    repo_name = os.path.basename(root_dir)
    return github_user, repo_name


def get_uncommitted_files():
    """Returns a list of modified, added, or untracked files."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        files = []
        for line in result.stdout.splitlines():
            if len(line) > 3:
                # Extract filepath starting from the 4th character
                filepath = line[3:]
                if filepath.startswith('"') and filepath.endswith('"'):
                    filepath = filepath[1:-1]
                files.append(filepath)
        return files
    except subprocess.CalledProcessError:
        print("[!] Warning: Not a git repository or git error.")
        return []


def get_docs_files(root_dir):
    """Recursively fetches all files within the docs/ directory."""
    docs_dir = os.path.join(root_dir, "docs")
    docs_files = []
    if os.path.exists(docs_dir):
        for dirpath, _, filenames in os.walk(docs_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in IGNORE_EXTENSIONS:
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, root_dir)
                    # Normalize path separators for consistency
                    docs_files.append(rel_path.replace("\\", "/"))
    return docs_files


def is_text_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return ext not in IGNORE_EXTENSIONS


def generate_payload(modules=None):
    if modules is None:
        modules = []

    root_dir = get_git_root()
    os.chdir(root_dir)

    github_user, repo_name = get_github_info(root_dir)

    uncommitted = get_uncommitted_files()
    docs_files = get_docs_files(root_dir)

    # Amalgamate target files, ensuring uniqueness
    target_files = set()
    if os.path.exists("AGENTS.md"):
        target_files.add("AGENTS.md")

    for f in docs_files:
        target_files.add(f)

    for f in uncommitted:
        if os.path.exists(f) and os.path.isfile(f):
            # Exclude files inside ignored directories
            if not any(ignored in f.split("/") for ignored in IGNORE_DIRS):
                target_files.add(f)

    # Final safety check: ensure file still exists on disk
    target_files = {f for f in target_files if os.path.exists(f) and os.path.isfile(f)}

    output_dir = os.path.expanduser("~/tmp")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, "gemini_startup_payload.txt")

    with open(output_filename, "w", encoding="utf-8") as out:
        out.write("SYSTEM DIRECTIVE: INITIALIZATION PAYLOAD\n")
        out.write(f"Repository Target: {github_user}/{repo_name}\n\n")

        out.write("--- CONTEXT INSTRUCTIONS ---\n")
        out.write(
            "1. You have read-only access to my GitHub repository via your extensions.\n"
        )
        out.write(
            "2. The files below represent my CURRENT UNPUSHED WORK-IN-PROGRESS, alongside our strict architectural mandates (AGENTS.md and docs/).\n"
        )
        out.write(
            "3. You MUST prioritize the contents of this file over the historical state on GitHub. For any other files, use your GitHub integration to fetch them dynamically.\n"
        )
        out.write(
            "4. Code Generation: You MUST continue using the MIME-like Parcel transport schema defined in AGENTS.md to modify my local files.\n"
        )
        if modules:
            out.write(
                "6. MODULE LOADING MANDATE: Use your @GitHub integration to explicitly fetch and load the following modules/paths before proceeding:\n"
            )
            for mod in modules:
                out.write(f"   - {mod}\n")

        out.write("----------------------------\n\n")

        for filepath in sorted(target_files):
            if not is_text_file(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as infile:
                    content = infile.read()

                out.write(f"File: {filepath}\n")
                out.write("=" * 80 + "\n")
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")
                out.write("=" * 80 + "\n\n")
            except UnicodeDecodeError:
                # Gracefully skip binaries disguised without extensions
                pass
            except Exception as e:
                print(f"[!] Error reading {filepath}: {e}")

    print(f"\n[+] Successfully generated {output_filename}")
    print(
        f"    Included: {len(target_files)} files (AGENTS.md, docs/, and uncommitted changes)."
    )
    if modules:
        print(f"    Requested GitHub Modules: {', '.join(modules)}")
    print("[*] Upload this file to Gemini to begin the session.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a highly-focused initialization payload for Gemini sessions."
    )
    parser.add_argument(
        "modules",
        nargs="*",
        help="List of modules/directories to instruct Gemini to load via @GitHub.",
    )
    args = parser.parse_args()

    generate_payload(args.modules)
