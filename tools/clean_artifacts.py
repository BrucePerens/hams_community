#!/usr/bin/env python3
import csv
import os
import re
import shutil
import glob

# --- Configuration ---
DATA_DIR = "ham_auxcomm_training/data"


def clean_cell(text):
    """Scrub LLM hallucination artifacts from a single string."""
    if not isinstance(text, str) or not text:
        return text

    original = text

    # 1. Strip raw unprintable control characters (Leaves \n, \r, \t intact)
    # \x08 = Backspace, \x0b = Vertical Tab, \x0c = Form Feed
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # 2. Strip literal escaped sequences if the LLM output them as raw text
    text = text.replace("\\b", "")
    text = text.replace("\\v", "")
    text = text.replace("\\f", "")

    # 3. Collapse extreme repetition of whitespace (LLM stuck in a loop)
    text = re.sub(r"\t{3,}", " ", text)  # 3 or more consecutive tabs becomes 1 space
    text = re.sub(r" {10,}", " ", text)  # 10 or more consecutive spaces becomes 1 space

    # 4. Collapse repeating non-breaking spaces
    text = re.sub(r"(?:&nbsp;){5,}", " ", text)

    return text


def process_csv(filepath):
    temp_path = filepath + ".tmp"
    changes_made = 0

    try:
        # Use standard reader/writer to gracefully handle any dirty CSV rows
        with open(filepath, mode="r", encoding="utf-8") as infile, open(
            temp_path, mode="w", encoding="utf-8", newline=""
        ) as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                new_row = []
                row_changed = False

                for cell in row:
                    cleaned_cell = clean_cell(cell)
                    if cleaned_cell != cell:
                        row_changed = True
                    new_row.append(cleaned_cell)

                if row_changed:
                    changes_made += 1

                writer.writerow(new_row)

        # Atomically replace if we actually fixed something
        if changes_made > 0:
            shutil.move(temp_path, filepath)
            print(
                f"  [+] Cleaned {changes_made} artifact rows in {os.path.basename(filepath)}"
            )
        else:
            os.remove(temp_path)
            print(f"  [=] No artifacts found in {os.path.basename(filepath)}")

    except Exception as e:
        print(f"  [!] Error processing {filepath}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)


def main():
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not csv_files:
        print(f"Error: No CSV files found in {DATA_DIR}. Are you in the project root?")
        return

    print(f"Scanning {len(csv_files)} CSV files for LLM hallucination artifacts...")
    for filepath in csv_files:
        process_csv(filepath)

    print("Cleanup complete!")


if __name__ == "__main__":
    main()
