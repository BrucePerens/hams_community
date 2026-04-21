#!/usr/bin/env python3
import os
import re
import sys

def clean_init_files(root_dir):
    # Matches optional leading tabs/spaces, '#', optional spaces, 'noqa',
    # optional spaces, ':', optional spaces, 'F401', and optional trailing spaces.
    # Case-insensitive to catch variations like 'NOQA' or 'f401'.
    pattern = re.compile(r'[ \t]*#[\t ]*noqa[\t ]*:[\t ]*f401[\t ]*', re.IGNORECASE)

    count = 0
    for dirpath, dirs, filenames in os.walk(root_dir):
        # Exclude hidden directories and standard virtual environments
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'venv', 'env', 'node_modules')]

        for filename in filenames:
            if filename == '__init__.py':
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    modified = False
                    new_content = []

                    for line in content.splitlines(keepends=True):
                        new_line = pattern.sub('', line)
                        if new_line != line:
                            modified = True
                        new_content.append(new_line)

                    if modified:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.writelines(new_content)
                        print(f"Cleaned: {filepath}")
                        count += 1

                except Exception as e:
                    print(f"Error processing {filepath}: {e}", file=sys.stderr)

    print(f"\nTotal __init__.py files cleaned: {count}")

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    clean_init_files(target_dir)
