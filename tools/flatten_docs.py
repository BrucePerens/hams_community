#!/usr/bin/env python3
import os
import shutil


def flatten_docs():
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    subdirs = ["adrs", "runbooks", "stories", "journeys", "security_models", "modules"]

    for subdir in subdirs:
        base_path = os.path.join(docs_dir, subdir)
        if not os.path.exists(base_path):
            continue

        for category in ["core", "domain"]:
            cat_path = os.path.join(base_path, category)
            if os.path.exists(cat_path):
                for filename in os.listdir(cat_path):
                    src = os.path.join(cat_path, filename)
                    dst = os.path.join(base_path, filename)

                    # Only move if it's a file
                    if os.path.isfile(src):
                        shutil.move(src, dst)
                        print(f"Moved {src} to {dst}")

                # Remove the empty directory
                try:
                    os.rmdir(cat_path)
                    print(f"Removed empty directory {cat_path}")
                except OSError:
                    print(f"Could not remove directory {cat_path} (not empty)")


if __name__ == "__main__":
    flatten_docs()
