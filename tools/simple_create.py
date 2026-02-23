#!/usr/bin/env python3
import os
import sys

# Standard ignore lists to keep the prompt clean and token-efficient
IGNORE_DIRS = {'__pycache__', 'venv', 'env', '.git', '.idea', '.vscode', 'node_modules'}
IGNORE_EXTENSIONS = {
    '.pyc', '.pyo', '.pyd', '.so', '.dll', '.class', '.exe', 
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.tar', '.gz', '.pdf'
}
IGNORE_FILES = {'id_rsa', 'id_rsa.pub', 'known_hosts', 'authorized_keys', 'package-lock.json', 'yarn.lock'}

def generate_plain_text_prompt(root_dir="."):
    root_path = os.path.abspath(root_dir)
    
    # Optional: You can prepend a default system prompt here if you want
    print("Please review the following project files:\n")

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Prune hidden and ignored directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in IGNORE_DIRS]

        for filename in filenames:
            # Skip hidden and ignored files
            if filename.startswith('.') or filename in IGNORE_FILES:
                continue
            
            _, ext = os.path.splitext(filename)
            if ext.lower() in IGNORE_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_path).replace('\\', '/')

            try:
                # Attempt to read as standard UTF-8 text
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Output the formatted delimiter block
                print(f"File: {rel_path}")
                print("=" * 80)
                print(content)
                # Ensure a trailing newline before closing the block
                if content and not content.endswith('\n'):
                    print()
                print("=" * 80)
                print()
                
            except UnicodeDecodeError:
                # Gracefully skip files that aren't valid UTF-8 (likely binaries we missed in the extension filter)
                sys.stderr.write(f"Skipping binary or non-UTF-8 file: {rel_path}\n")
            except Exception as e:
                sys.stderr.write(f"Error reading {rel_path}: {e}\n")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_plain_text_prompt(target_dir)
