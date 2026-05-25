#!/usr/bin/env python3
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_tours(root_dir):
    modified_count = 0
    manual_review_needed = 0

    # Regex to capture TourUtils.clickElement('selector', 'description')
    click_pattern = re.compile(r'TourUtils\.clickElement\(\s*([\'"`])(.*?)\1\s*,\s*([\'"`])(.*?)\3\s*\)')

    # Regex to capture TourUtils.waitForElement('selector', 'description')
    wait_pattern = re.compile(r'TourUtils\.waitForElement\(\s*([\'"`])(.*?)\1\s*,\s*([\'"`])(.*?)\3\s*\)')

    # Regex to capture TourUtils.waitForRPC()
    rpc_pattern = re.compile(r'TourUtils\.waitForRPC\(\s*\),?')

    for dirpath, _, filenames in os.walk(root_dir):
        if any(ignored in dirpath for ignored in [".venv", "__pycache__", ".git", "node_modules"]):
            continue

        for filename in filenames:
            if filename.endswith(".js") and ("tours" in dirpath or "tour" in filename):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content

                    # 1. Strip redundant waitForRPC
                    content = rpc_pattern.sub('', content)

                    # 2. Convert clickElement to native step objects
                    # Replacement structure: { trigger: 'selector', content: 'description', run: 'click' }
                    def click_repl(match):
                        quote = match.group(1)
                        selector = match.group(2)
                        desc_quote = match.group(3)
                        desc = match.group(4)
                        return f"{{ trigger: {quote}{selector}{quote}, content: {desc_quote}{desc}{desc_quote}, run: 'click' }}"

                    content = click_pattern.sub(click_repl, content)

                    # 3. Convert waitForElement to native step objects (empty run)
                    def wait_repl(match):
                        quote = match.group(1)
                        selector = match.group(2)
                        desc_quote = match.group(3)
                        desc = match.group(4)
                        return f"{{ trigger: {quote}{selector}{quote}, content: {desc_quote}Wait for: {desc}{desc_quote}, run: function() {{}} }}"

                    content = wait_pattern.sub(wait_repl, content)

                    if content != original_content:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
                        print(f"[+] Migrated to native steps: {os.path.relpath(filepath, root_dir)}")
                        modified_count += 1

                    # Flag files that still have :contains for manual review
                    if ":contains" in content:
                        print(f"   [!] MANUAL REVIEW REQUIRED: {os.path.relpath(filepath, root_dir)} still uses ':contains'. Convert to data-menu-xmlid.")
                        manual_review_needed += 1

                except Exception as e: # audit-ignore-catch-all
                    logger.warning("Could not process %s: %s", filepath, e)
                    print(f"[!] Could not process {filepath}: {e}")

    print(f"\nDone! Automatically migrated {modified_count} files.")
    if manual_review_needed > 0:
        print(f"Warning: {manual_review_needed} files require manual translation of ':contains' selectors to native attributes.")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"[*] Migrating JS Tours to native architecture at: {repo_root}")
    migrate_tours(repo_root)
