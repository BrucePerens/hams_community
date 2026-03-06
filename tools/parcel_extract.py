#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import xml.etree.ElementTree as ET
import json
import ast


def verify_python(filepath):
    """Runs flake8 to verify Python syntax and style."""
    try:
        result = subprocess.run(
            ["flake8", "--extend-ignore=E203,E302,E501", filepath], capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"[WARN] flake8 found issues:\n{result.stdout.strip()}"
    except FileNotFoundError:
        return "[WARN] flake8 is not installed. Skipping verification."
    return None


def verify_xml(filepath):
    """Verifies that the XML is well-formed."""
    try:
        ET.parse(filepath)
    except ET.ParseError as e:
        return f"[WARN] XML Parsing Error: {e}"
    return None


def verify_markdown(filepath):
    """Checks for unclosed code blocks."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        code_block_markers = re.findall(r"^\s*`{3,}", content, flags=re.MULTILINE)
        if len(code_block_markers) % 2 != 0:
            return "[WARN] Markdown issue: Odd number of code block markers."
    except Exception as e:
        return f"[WARN] Could not verify Markdown: {e}"
    return None


def verify_json(filepath):
    """Verifies JSON payload validity."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        return f"[WARN] Invalid JSON: {e}"
    return None


def run_burn_list_linter(filepath):
    """Runs custom project linter to catch architectural issues."""
    linter_path = os.path.join(os.path.dirname(__file__), "check_burn_list.py")
    if os.path.exists(linter_path):
        try:
            result = subprocess.run(
                [sys.executable, linter_path, filepath], capture_output=True, text=True
            )
            if result.returncode != 0:
                out = result.stdout.strip()
                return f"[❌ LINTER FAILED] check_burn_list.py rejected:\n{out}"
        except Exception as e:
            return f"[WARN] Failed to execute custom linter: {e}"
    return None


def mask_markdown_and_check_balance(payload):
    """
    Masks out content inside inline and fenced code blocks in Markdown.
    Raises ValueError if blocks do not balance.
    """
    masked = []
    i = 0
    n = len(payload)
    in_fenced = False
    fence_str = ""
    in_inline = False
    inline_str = ""

    while i < n:
        if not in_fenced and not in_inline:
            # Match fenced block: up to 3 spaces, then 3+ backticks/tildes
            fence_match = re.match(r"^( {0,3})(`{3,}|~{3,})", payload[i:])
            if fence_match and (i == 0 or payload[i - 1] == "\n"):
                in_fenced = True
                fence_str = fence_match.group(2)
                advance = len(fence_match.group(0))
                masked.append(payload[i : i + advance])
                i += advance
                continue

            # Match inline code
            inline_match = re.match(r"^`+", payload[i:])
            if inline_match:
                in_inline = True
                inline_str = inline_match.group(0)
                advance = len(inline_match.group(0))
                masked.append(payload[i : i + advance])
                i += advance
                continue

            masked.append(payload[i])
            i += 1

        elif in_fenced:
            # Look for closing fence
            fence_match = re.match(r"^( {0,3})(`{3,}|~{3,})[ \t]*(\n|$)", payload[i:])
            if (
                fence_match
                and (i == 0 or payload[i - 1] == "\n")
                and fence_match.group(2)[0] == fence_str[0]
                and len(fence_match.group(2)) >= len(fence_str)
            ):
                in_fenced = False
                advance = len(fence_match.group(0))
                if payload[i : i + advance].endswith("\n"):
                    advance -= 1
                masked.append(payload[i : i + advance])
                i += advance
                continue

            # Mask character
            masked.append(" ")
            i += 1

        elif in_inline:
            # Look for closing inline code
            inline_match = re.match(r"^`+", payload[i:])
            if inline_match:
                if inline_match.group(0) == inline_str:
                    in_inline = False
                    advance = len(inline_str)
                    masked.append(payload[i : i + advance])
                    i += advance
                else:
                    # Consume the entire non-matching backtick sequence
                    advance = len(inline_match.group(0))
                    for _ in range(advance):
                        masked.append(" ")
                    i += advance
                continue

            masked.append(" ")
            i += 1

    if in_fenced:
        raise ValueError("Markdown Error: Unclosed fenced code block.")
    if in_inline:
        raise ValueError("Markdown Error: Unclosed inline code snippet.")

    return "".join(masked)


def check_ai_foibles(payload, filepath=""):
    """Strips rogue markdown wrappers and rejects laziness placeholders."""
    # LLMs occasionally wrap their payload in standard markdown blocks
    payload = re.sub(r"^\s*```[a-zA-Z]*\n", "", payload)
    payload = re.sub(r"\n\s*```\s*$", "\n", payload)

    text_to_check = payload
    if filepath.endswith(".md"):
        text_to_check = mask_markdown_and_check_balance(payload)

    # Strings split mathematically to avoid triggering the extractor on itself
    foibles = [
        r"#" + r"\s*\.\.\.\s*rest of",
        r"//" + r"\s*\.\.\.\s*rest of",
        r"<!" + r"--\s*\.\.\.\s*rest of",
        r"#" + r"\s*Code unchanged",
        r"//" + r"\s*Code unchanged",
        r"#" + r"\s*\.\.\.\s*existing code\s*\.\.\.",
    ]
    for f in foibles:
        if re.search(f, text_to_check, re.IGNORECASE):
            raise ValueError(
                f"AI Laziness Foible: Found placeholder matching {f}. "
                "Payload rejected to prevent file corruption."
            )

    return payload


def whitespace_agnostic_replace(original_text, search_text, replace_text):
    """Finds search block ignoring spaces/newlines ensuring drift safety."""
    search_stripped = "".join(search_text.split())
    if not search_stripped:
        return original_text

    chars = []
    indices = []
    for i, c in enumerate(original_text):
        if not c.isspace():
            chars.append(c)
            indices.append(i)

    orig_stripped = "".join(chars)
    idx = orig_stripped.find(search_stripped)
    if idx == -1:
        return None

    start_idx = indices[idx]
    end_idx = indices[idx + len(search_stripped) - 1]

    # Prevent double-indentation. original_text[:start_idx] includes the
    # original leading whitespace. Strip leading spaces/tabs from the
    # replacement so it docks perfectly onto the original indentation.
    replace_text = replace_text.lstrip(" \t")

    return original_text[:start_idx] + replace_text + original_text[end_idx + 1 :]


def ast_fallback_replace(original_text, search_text, replace_text):
    """If exact string matching fails in Python, replace the AST node."""
    try:
        search_tree = ast.parse(search_text)
        target_name = None
        valid_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        for node in search_tree.body:
            if isinstance(node, valid_types):
                target_name = node.name
                break

        if not target_name:
            return None

        orig_tree = ast.parse(original_text)
        target_node = None
        for node in ast.walk(orig_tree):
            if getattr(node, "name", None) == target_name:
                target_node = node
                break

        if not target_node:
            return None

        lines = original_text.splitlines()
        start_line = target_node.lineno - 1
        end_line = target_node.end_lineno

        new_lines = lines[:start_line] + replace_text.splitlines() + lines[end_line:]
        return "\n".join(new_lines) + "\n"
    except SyntaxError:
        return None


def extract_parcel(raw_text):
    lines = raw_text.splitlines()

    # Find the absolute first boundary string and ignore everything else
    boundary = None
    for line_item in lines:
        stripped = line_item.strip()
        if stripped.startswith("@@BOUNDARY_") and stripped.endswith("@@"):
            boundary = stripped
            break

    if not boundary:
        print("❌ Error: Invalid Parcel format. Missing boundary string.\n")
        return

    terminator = boundary + "--"

    if terminator not in raw_text:
        print("❌ [WARN] Parcel terminator missing. Attempting extract...\n")

    # Split strictly on the detected boundary
    pattern = rf"^{re.escape(boundary)}$"
    parts = re.split(pattern, raw_text, flags=re.MULTILINE)

    tasks_by_file = {}

    for part in parts:
        if not part.strip() or part.strip().startswith("--"):
            continue

        # Strip leading whitespace for header parsing, keep trailing
        part = part.lstrip()
        if "\n\n" not in part:
            continue

        header, payload = part.split("\n\n", 1)

        path_lines = [line_item for line_item in header.splitlines() if line_item.startswith("Path: ")]
        if not path_lines:
            continue

        filepath = path_lines[0].replace("Path: ", "").strip()

        operation_lines = [line_item for line_item in header.splitlines() if line_item.startswith("Operation: ")]
        operation = operation_lines[0].replace("Operation: ", "").strip().lower() if operation_lines else "overwrite"

        new_path_lines = [line_item for line_item in header.splitlines() if line_item.startswith("New-Path: ")]
        new_filepath = new_path_lines[0].replace("New-Path: ", "").strip() if new_path_lines else None

        encoding_lines = [line_item for line_item in header.splitlines() if line_item.startswith("Encoding: ")]
        encoding = encoding_lines[0].replace("Encoding: ", "").strip().lower() if encoding_lines else "utf-8"

        mode_lines = [line_item for line_item in header.splitlines() if line_item.startswith("Mode: ")]
        mode_str = mode_lines[0].replace("Mode: ", "").strip() if mode_lines else None

        # Clean terminator from the payload if it's attached
        if terminator in payload:
            payload = payload.split(terminator)[0]

        if encoding == "url-encoded":
            import urllib.parse
            payload = urllib.parse.unquote(payload)

        try:
            payload = check_ai_foibles(payload, filepath)
        except ValueError as e:
            tasks_by_file.setdefault(filepath, []).append({"error": str(e)})
            continue

        # Ensure payload ends with exactly one newline
        payload = payload.rstrip() + "\n"

        task = {
            "operation": operation,
            "filepath": filepath,
            "new_filepath": new_filepath,
            "mode_str": mode_str,
            "payload": payload,
            "error": None
        }
        tasks_by_file.setdefault(filepath, []).append(task)

    def _print_summary(fp, errs, warns, aborted, count):
        if aborted:
            print(f"❌ Extracted with errors: {fp} ({count} operations)")
            for err in errs:
                print(f"  {err}")
            print(f"  [!] Aborted all modifications for {fp} due to errors.\n")
        elif warns:
            print(f"⚠️  Extracted with warnings: {fp} ({count} operations)")
            for w in warns:
                print(f"  {w}")
            print()
        else:
            op_text = "operation" if count == 1 else "operations"
            print(f"✅ Extracted: {fp} ({count} {op_text})")

    import shutil

    for filepath, tasks in tasks_by_file.items():
        errors = []
        warnings = []

        for t in tasks:
            if t.get("error"):
                errors.append(t["error"])

        if errors:
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
            continue

        target_dir = os.path.dirname(filepath)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    current_text = f.read()
            except Exception as e:
                errors.append(f"Failed to read existing file {filepath}: {e}")
                _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
                continue
        else:
            current_text = ""

        file_mutated = False
        mode_int = None
        file_deleted = False
        renamed_to = None
        copied_to = None

        try:
            for task in tasks:
                op = task["operation"]
                payload = task["payload"]
                mode_str = task["mode_str"]

                if mode_str:
                    try:
                        mode_int = int(mode_str, 8)
                    except ValueError:
                        raise ValueError(f"Invalid mode format: {mode_str}. Must be octal.")

                if op in ("delete", "remove"):
                    file_deleted = True
                    break

                elif op == "rename":
                    if not task["new_filepath"]:
                        raise ValueError("Rename requires 'New-Path: <target>'")
                    if not os.path.exists(filepath):
                        raise FileNotFoundError(f"Cannot rename missing file: {filepath}")
                    renamed_to = task["new_filepath"]

                elif op == "copy":
                    if not task["new_filepath"]:
                        raise ValueError("Copy requires 'New-Path: <target>'")
                    if not os.path.exists(filepath):
                        raise FileNotFoundError(f"Cannot copy missing file: {filepath}")
                    copied_to = task["new_filepath"]

                elif op == "chmod":
                    if not mode_str:
                        raise ValueError("Chmod requires 'Mode: <octal_string>'")
                    if not os.path.exists(filepath) and not file_mutated:
                        raise FileNotFoundError(f"Cannot chmod missing file: {filepath}")

                elif op == "overwrite":
                    current_text = payload
                    if not payload.strip():
                        warnings.append("[WARN] Extracted payload is empty.")
                    file_mutated = True

                elif op == "search-and-replace":
                    if not os.path.exists(filepath) and not file_mutated:
                        raise FileNotFoundError(f"Cannot search-and-replace missing file: {filepath}")

                    pattern = r"^<<<< SEARCH\n(.*?)\n^====\n(.*?)\n^>>>> REPLACE"
                    search_blocks = list(re.finditer(pattern, payload, re.DOTALL | re.MULTILINE))

                    if not search_blocks:
                        raise ValueError("Malformed search-and-replace block. Missing markers.")

                    for match in search_blocks:
                        search_text = match.group(1)
                        replace_text = match.group(2)

                        new_text = whitespace_agnostic_replace(current_text, search_text, replace_text)
                        if new_text is None:
                            if filepath.endswith(".py"):
                                new_text = ast_fallback_replace(current_text, search_text, replace_text)
                                if new_text is None:
                                    raise ValueError("AST fallback failed for search block.")
                            else:
                                raise ValueError("Search block not found.")
                        current_text = new_text
                    file_mutated = True

        except Exception as e:
            errors.append(str(e))

        if errors:
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
            continue

        # Commit Phase
        try:
            if file_deleted:
                if os.path.exists(filepath):
                    os.remove(filepath)
                print(f"✅ Deleted: {filepath}")
                continue

            if renamed_to:
                os.makedirs(os.path.dirname(renamed_to), exist_ok=True)
                os.rename(filepath, renamed_to)
                print(f"✅ Renamed: {filepath} -> {renamed_to}")
                continue

            if copied_to:
                os.makedirs(os.path.dirname(copied_to), exist_ok=True)
                shutil.copy2(filepath, copied_to)
                print(f"✅ Copied: {filepath} -> {copied_to}")
                continue

            if file_mutated:
                if filepath.endswith(".py"):
                    current_text = re.sub(r"[ \t]+$", "", current_text, flags=re.MULTILINE)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(current_text)

            if mode_int is not None:
                os.chmod(filepath, mode_int)

            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".py":
                err = verify_python(filepath)
                if err: warnings.append(err)
            elif ext == ".xml":
                err = verify_xml(filepath)
                if err: warnings.append(err)
            elif ext == ".md":
                err = verify_markdown(filepath)
                if err: warnings.append(err)
            elif ext == ".json":
                err = verify_json(filepath)
                if err: warnings.append(err)

            if ext in (".py", ".xml", ".js"):
                err = run_burn_list_linter(filepath)
                if err: warnings.append(err)

            _print_summary(filepath, errors, warnings, aborted=False, count=len(tasks))

        except Exception as e:
            errors.append(f"Commit failed: {e}")
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                input_data = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{sys.argv[1]}' not found.\n")
            sys.exit(1)
    else:
        # Running entirely silent on stdin prevents terminal noise
        input_data = sys.stdin.read()

    extract_parcel(input_data)
