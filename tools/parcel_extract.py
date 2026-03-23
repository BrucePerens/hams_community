#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import xml.etree.ElementTree as ET
import json
import ast
import tokenize
import io
import difflib


def verify_python(filepath):
    """Runs flake8 to verify Python syntax and style."""
    try:
        # Select only E9 (Syntax) and F (Logic/Name) errors to prevent cosmetic spacing
        # issues from aborting the extraction process.
        result = subprocess.run(
            ["flake8", "--select=E9,F", filepath],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"[ERROR] flake8 found issues:\n{result.stdout.strip()}"
    except FileNotFoundError:
        return "[WARN] flake8 is not installed. Skipping verification."
    return None


def verify_xml(filepath):
    """Verifies that the XML is well-formed."""
    try:
        ET.parse(filepath)
    except ET.ParseError as e:
        return f"[ERROR] XML Parsing Error: {e}"
    return None


def verify_markdown(filepath):
    """Checks for unclosed inline and fenced code blocks using robust state parsing."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        mask_markdown_and_check_balance(content)
    except ValueError as e:
        return f"[ERROR] {e}"
    except Exception as e:
        return f"[WARN] Could not verify Markdown: {e}"
    return None


def verify_json(filepath):
    """Verifies JSON payload validity."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
    except Exception as e:
        return f"[ERROR] Invalid JSON: {e}"
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
                return f"[ERROR] check_burn_list.py rejected:\n{out}"
        except Exception as e:
            return f"[WARN] Failed to execute custom linter: {e}"
    return None


def mask_markdown_and_check_balance(payload):
    """
    Accurate line-by-line parser to check Markdown code block balance.
    Respects CommonMark rules for fenced blocks, inline spans, and backslash escapes.
    """
    in_fenced = False
    fence_char = ""
    fence_len = 0

    in_inline = False
    inline_len = 0

    lines = payload.split("\n")

    for line in lines:
        stripped = line.lstrip(" \t")

        # 1. Handle Fenced Code Blocks (which ignore all internal markdown)
        if not in_fenced and not in_inline:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                char = stripped[0]
                count = 0
                for c in stripped:
                    if c == char:
                        count += 1
                    else:
                        break
                if count >= 3:
                    in_fenced = True
                    fence_char = char
                    fence_len = count
                    continue

        if in_fenced:
            if stripped.startswith(fence_char):
                count = 0
                for c in stripped:
                    if c == fence_char:
                        count += 1
                    else:
                        break
                if count >= fence_len:
                    in_fenced = False
            continue

        # 2. Handle Inline Code Spans (and escapes)
        i = 0
        n = len(line)
        while i < n:
            # Backslash escapes are valid outside inline blocks
            if not in_inline and line[i] == "\\":
                i += 2
                continue

            if line[i] == "`":
                start_idx = i
                while i < n and line[i] == "`":
                    i += 1
                count = i - start_idx

                if not in_inline:
                    in_inline = True
                    inline_len = count
                elif count == inline_len:
                    in_inline = False
            else:
                i += 1

    if in_fenced:
        raise ValueError("Markdown Error: Unclosed fenced code block.")
    if in_inline:
        raise ValueError("Markdown Error: Unclosed inline code snippet.")

    return payload


def check_ai_foibles(payload, filepath=""):
    """Strips rogue markdown wrappers and rejects laziness placeholders."""
    if payload.lstrip().startswith("```"):
        lines = payload.strip("\r\n").split("\n")
        if (
            len(lines) >= 2
            and lines[0].strip().startswith("```")
            and lines[-1].strip().startswith("```")
        ):
            payload = "\n".join(lines[1:-1]) + "\n"

    text_to_check = payload
    if filepath.endswith(".md"):
        try:
            mask_markdown_and_check_balance(payload)
        except ValueError:
            pass  # We pass it through here, but the verifier will warn the user

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

    # UI Data Loss Guardrail: Detect stripped HTML comments leaving behind empty backticks
    if filepath.endswith(".md") and re.search(r"(?<!`)``(?!`)", text_to_check):
        raise ValueError(
            "UI Data Loss Detected: Found empty inline code block (``). "
            "The conversational UI likely stripped an HTML/XML comment before reaching the extractor. "
            "You MUST percent-encode the tags (%3C, %3E) to bypass the UI."
        )

    return payload


def validate_syntax_in_memory(filepath, content):
    """Validates the syntax of the fully patched file in memory before writing to disk."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".py":
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Python Syntax/Indentation Error: {e}")
    elif ext == ".json":
        try:
            json.loads(content)
        except Exception as e:
            raise ValueError(f"JSON Syntax Error: {e}")
    elif ext == ".xml":
        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            raise ValueError(f"XML Syntax Error: {e}")
    elif ext == ".md":
        mask_markdown_and_check_balance(content)


def get_semantic_tokens(source_text):
    """
    Converts source code into a list of meaningful tokens, stripping
    formatting and line breaks (but retaining comments for anchor accuracy).
    """
    lines = source_text.splitlines(keepends=True)
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line))

    tokens = []
    reader = io.BytesIO(source_text.encode("utf-8")).readline

    try:
        for tok in tokenize.tokenize(reader):
            if tok.type in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.ENCODING,
                tokenize.ENDMARKER,
            ):
                continue

            val = tok.string
            start_char = line_offsets[tok.start[0] - 1] + tok.start[1]
            end_char = line_offsets[tok.end[0] - 1] + tok.end[1]

            tokens.append(
                {"type": tok.type, "val": val, "start": start_char, "end": end_char}
            )
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None

    return tokens


def process_indented_replacement(replace_text, indentation):
    """Preserves relative nesting when injecting multiline code blocks."""
    replace_lines = replace_text.strip("\n").split("\n")

    base_replace_indent = None
    for line in replace_lines:
        if line.strip():
            indent = len(line) - len(line.lstrip(" \t"))
            if base_replace_indent is None or indent < base_replace_indent:
                base_replace_indent = indent
    if base_replace_indent is None:
        base_replace_indent = 0

    indented_replace = replace_lines[0].lstrip(" \t")
    if len(replace_lines) > 1:
        for line in replace_lines[1:]:
            if line.strip():
                relative_line = (
                    line[base_replace_indent:]
                    if len(line) >= base_replace_indent
                    and line[:base_replace_indent].isspace()
                    else line.lstrip(" \t")
                )
                indented_replace += "\n" + indentation + relative_line
            else:
                indented_replace += "\n"
    return indented_replace


def fuzzy_line_replace(original_text, search_text, replace_text):
    """
    Fallback algorithm that evaluates lines using difflib to absorb LLM
    formatting drift or syntactically incomplete AST fragments.
    """
    orig_lines = original_text.split("\n")
    search_lines = search_text.strip("\n").split("\n")

    if not orig_lines or not search_lines:
        return None

    search_len = len(search_lines)
    target_len = len(orig_lines)

    if search_len == 0 or search_len > target_len:
        return None

    # Normalize search lines to ignore trailing whitespace drift
    norm_search = [line_item.strip() for line_item in search_lines]

    best_ratio = 0
    best_indices = []

    # Sliding window comparison
    for i in range(target_len - search_len + 1):
        window = [line_item.strip() for line_item in orig_lines[i : i + search_len]]
        ratio = difflib.SequenceMatcher(None, window, norm_search).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_indices = [i]
        elif ratio == best_ratio and ratio > 0:
            best_indices.append(i)

    if best_ratio >= 0.85:  # High confidence threshold
        if len(best_indices) > 1:
            raise ValueError(
                "Fuzzy line match is not unique (found multiple blocks with similar logic). Please provide more context lines."
            )

        best_idx = best_indices[0]
        first_line = orig_lines[best_idx]
        indentation = first_line[: len(first_line) - len(first_line.lstrip(" \t"))]

        indented_replace = process_indented_replacement(replace_text, indentation)

        # Reconstruct the file with the replaced lines
        new_lines = (
            orig_lines[:best_idx]
            + indented_replace.split("\n")
            + orig_lines[best_idx + search_len :]
        )
        return "\n".join(new_lines)

    return None


def semantic_token_replace(original_text, search_text, replace_text):
    target_tokens = get_semantic_tokens(original_text)
    search_tokens = get_semantic_tokens(search_text)

    if not target_tokens or not search_tokens:
        return None

    search_len = len(search_tokens)
    target_len = len(target_tokens)

    if search_len == 0 or search_len > target_len:
        return None

    matches = []
    for i in range(target_len - search_len + 1):
        match = True
        for j in range(search_len):
            if target_tokens[i + j]["val"] != search_tokens[j]["val"]:
                match = False
                break

        if match:
            matches.append(i)

    if len(matches) > 1:
        raise ValueError(
            "Semantic token match is not unique. Please provide more context lines in the SEARCH block."
        )
    elif len(matches) == 1:
        start_idx = target_tokens[matches[0]]["start"]
        end_idx = target_tokens[matches[0] + search_len - 1]["end"]

        line_start = original_text.rfind("\n", 0, start_idx) + 1
        indentation = original_text[line_start:start_idx]

        indented_replace = process_indented_replacement(replace_text, indentation)
        return original_text[:start_idx] + indented_replace + original_text[end_idx:]

    return None


def get_markdown_tokens(text):
    tokens = []
    # Aggressive Alphanumeric Normalization:
    # Completely strips formatting symbols, punctuation, and bullets.
    for match in re.finditer(r"[a-zA-Z0-9]+", text):
        tokens.append(
            {
                "raw": match.group(),
                "norm": match.group().lower(),
                "start": match.start(),
                "end": match.end(),
            }
        )
    return tokens


def semantic_markdown_replace(original_text, search_text, replace_text):
    target_tokens = get_markdown_tokens(original_text)
    search_tokens = get_markdown_tokens(search_text)

    if not target_tokens or not search_tokens:
        return None

    search_len = len(search_tokens)
    target_len = len(target_tokens)

    if search_len == 0 or search_len > target_len:
        return None

    matches = []
    for i in range(target_len - search_len + 1):
        match = True
        for j in range(search_len):
            if target_tokens[i + j]["norm"] != search_tokens[j]["norm"]:
                match = False
                break

        if match:
            matches.append(i)

    if len(matches) > 1:
        raise ValueError(
            "Semantic Markdown match is not unique. Please provide more context lines."
        )
    elif len(matches) == 1:
        start_idx = target_tokens[matches[0]]["start"]
        end_idx = target_tokens[matches[0] + search_len - 1]["end"]

        line_start = original_text.rfind("\n", 0, start_idx) + 1
        indentation = original_text[line_start:start_idx]

        indented_replace = process_indented_replacement(replace_text, indentation)
        return original_text[:start_idx] + indented_replace + original_text[end_idx:]

    return None


def boundary_markdown_replace(original_text, search_text, replace_text):
    target_tokens = get_markdown_tokens(original_text)
    search_tokens = get_markdown_tokens(search_text)

    if not target_tokens or len(search_tokens) < 10:
        return None

    # Take first 5 and last 5 alphanumeric words
    prefix = [t["norm"] for t in search_tokens[:5]]
    suffix = [t["norm"] for t in search_tokens[-5:]]

    target_words = [t["norm"] for t in target_tokens]

    start_matches = []
    for i in range(len(target_words) - 4):
        if target_words[i : i + 5] == prefix:
            start_matches.append(i)

    if len(start_matches) > 1:
        raise ValueError("Boundary Markdown Prefix is not unique.")
    if not start_matches:
        return None

    best_start_token_idx = start_matches[0]

    end_matches = []
    for i in range(best_start_token_idx, len(target_words) - 4):
        if target_words[i : i + 5] == suffix:
            end_matches.append(i + 4)

    if len(end_matches) > 1:
        raise ValueError("Boundary Markdown Suffix is not unique.")
    if not end_matches:
        return None

    best_end_token_idx = end_matches[0]

    start_idx = target_tokens[best_start_token_idx]["start"]
    end_idx = target_tokens[best_end_token_idx]["end"]

    line_start = original_text.rfind("\n", 0, start_idx) + 1
    indentation = original_text[line_start:start_idx]

    indented_replace = process_indented_replacement(replace_text, indentation)
    return original_text[:start_idx] + indented_replace + original_text[end_idx:]


def fuzzy_markdown_replace(original_text, search_text, replace_text):
    target_tokens = get_markdown_tokens(original_text)
    search_tokens = get_markdown_tokens(search_text)

    if not target_tokens or not search_tokens:
        return None

    search_len = len(search_tokens)
    target_len = len(target_tokens)

    if search_len == 0 or search_len > target_len:
        return None

    search_words = [t["norm"] for t in search_tokens]
    target_words = [t["norm"] for t in target_tokens]

    best_ratio = 0
    best_indices = []

    for i in range(target_len - search_len + 1):
        window = target_words[i : i + search_len]
        ratio = difflib.SequenceMatcher(None, window, search_words).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_indices = [i]
        elif ratio == best_ratio and ratio > 0:
            best_indices.append(i)

    if best_ratio > 0.90:  # 90% word similarity
        if len(best_indices) > 1:
            raise ValueError(
                "Fuzzy Markdown match is not unique. Please provide more context lines."
            )

        best_idx = best_indices[0]
        start_idx = target_tokens[best_idx]["start"]
        end_idx = target_tokens[best_idx + search_len - 1]["end"]

        line_start = original_text.rfind("\n", 0, start_idx) + 1
        indentation = original_text[line_start:start_idx]

        indented_replace = process_indented_replacement(replace_text, indentation)
        return original_text[:start_idx] + indented_replace + original_text[end_idx:]

    return None


def get_xml_tokens(text):
    tokens = []
    pattern = re.compile(r"(<!\[CDATA\[.*?\]\]>||<[^>]+>|[^<]+)", re.DOTALL)

    def normalize_tag(tag_str):
        if (
            tag_str.startswith("</")
            or tag_str.startswith("<!")
            or tag_str.startswith("<?")
        ):
            return " ".join(tag_str.split())

        inner = tag_str[1:-1]
        is_self_closing = False
        if inner.endswith("/"):
            is_self_closing = True
            inner = inner[:-1]

        parts = inner.split(None, 1)
        if not parts:
            return tag_str

        tag_name = parts[0]
        attrs_str = parts[1] if len(parts) > 1 else ""

        attr_pattern = re.compile(r'([\w\-\:]+)\s*=\s*(["\'])(.*?)\2', re.DOTALL)
        attrs = attr_pattern.findall(attrs_str)
        sorted_attrs = sorted(attrs, key=lambda x: x[0])
        norm_attr_str = " ".join([f'{k}="{v}"' for k, q, v in sorted_attrs])

        res = f"<{tag_name}"
        if norm_attr_str:
            res += f" {norm_attr_str}"
        res += "/>" if is_self_closing else ">"
        return res

    for match in pattern.finditer(text):
        raw = match.group(1)
        norm = ""
        if raw.startswith("<"):
            norm = normalize_tag(raw)
        else:
            norm = raw.strip()
            if not norm:
                continue

        tokens.append(
            {"raw": raw, "norm": norm, "start": match.start(), "end": match.end()}
        )
    return tokens


def semantic_xml_replace(original_text, search_text, replace_text):
    target_tokens = get_xml_tokens(original_text)
    search_tokens = get_xml_tokens(search_text)

    if not target_tokens or not search_tokens:
        return None

    search_len = len(search_tokens)
    target_len = len(target_tokens)

    if search_len == 0 or search_len > target_len:
        return None

    matches = []
    for i in range(target_len - search_len + 1):
        match = True
        for j in range(search_len):
            if target_tokens[i + j]["norm"] != search_tokens[j]["norm"]:
                match = False
                break

        if match:
            matches.append(i)

    if len(matches) > 1:
        raise ValueError(
            "Semantic XML match is not unique. Please provide more context lines."
        )
    elif len(matches) == 1:
        start_idx = target_tokens[matches[0]]["start"]
        end_idx = target_tokens[matches[0] + search_len - 1]["end"]

        line_start = original_text.rfind("\n", 0, start_idx) + 1
        indentation = original_text[line_start:start_idx]

        indented_replace = process_indented_replacement(replace_text, indentation)
        return original_text[:start_idx] + indented_replace + original_text[end_idx:]

    return None


def whitespace_agnostic_replace(original_text, search_text, replace_text):
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

    matches = []
    idx = orig_stripped.find(search_stripped)
    while idx != -1:
        matches.append(idx)
        idx = orig_stripped.find(search_stripped, idx + 1)

    if len(matches) > 1:
        raise ValueError(
            "Whitespace-agnostic match is not unique. Please provide more context lines."
        )
    elif len(matches) == 1:
        idx = matches[0]
        start_idx = indices[idx]
        end_idx = indices[idx + len(search_stripped) - 1]

        line_start = original_text.rfind("\n", 0, start_idx) + 1
        indentation = original_text[line_start:start_idx]

        indented_replace = process_indented_replacement(replace_text, indentation)
        return (
            original_text[:start_idx] + indented_replace + original_text[end_idx + 1 :]
        )

    return None


def parse_search_replace_blocks(payload):
    """
    Safely parses SEARCH and REPLACE blocks line-by-line, enforcing
    closure to prevent greedy regex swallowing.
    """
    blocks = []
    lines = payload.split("\n")
    state = "TEXT"  # 'TEXT', 'SEARCH', 'REPLACE'
    current_search = []
    current_replace = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(":::: SEARCH"):
            if state != "TEXT":
                raise ValueError(
                    "Malformed search block: ':::: SEARCH' found inside another block."
                )
            state = "SEARCH"
            current_search = []
            current_replace = []
        elif stripped.startswith("===="):
            if state != "SEARCH":
                raise ValueError(
                    "Malformed search block: '====' found without preceding ':::: SEARCH'."
                )
            state = "REPLACE"
        elif stripped.startswith(":::: REPLACE"):
            if state != "REPLACE":
                raise ValueError(
                    "Malformed search block: ':::: REPLACE' found without preceding '===='."
                )
            blocks.append(
                {
                    "search": "\n".join(current_search) + "\n",
                    "replace": "\n".join(current_replace) + "\n",
                }
            )
            state = "TEXT"
        else:
            if state == "SEARCH":
                current_search.append(line)
            elif state == "REPLACE":
                current_replace.append(line)

    if state != "TEXT":
        raise ValueError(
            "Malformed search block: Unclosed ':::: SEARCH' or '====' block."
        )

    return blocks


def extract_parcel(raw_text):
    lines = raw_text.splitlines()
    boundaries_found = set()

    # 1. Enforce rigorous boundary checking and matching
    for line_item in lines:
        stripped = line_item.strip()
        if stripped.startswith("@@BOUNDARY_"):
            if stripped.endswith("@@"):
                boundaries_found.add(stripped)
            elif stripped.endswith("@@--"):
                boundaries_found.add(stripped[:-2])

    if not boundaries_found:
        print("❌ Error: Invalid Parcel format. Missing boundary string.\n")
        return

    if len(boundaries_found) > 1:
        print(
            f"❌ Error: Mismatched boundaries detected in Parcel: {', '.join(boundaries_found)}. All boundaries must be identical.\n"
        )
        return

    boundary = list(boundaries_found)[0]
    terminator = boundary + "--"

    # 2. Enforce explicit terminator to prevent partial payloads
    terminator_found = any(line_item.strip() == terminator for line_item in lines)
    if not terminator_found:
        print(
            f"❌ Error: Parcel terminator ({terminator}) missing. Rejecting payload to prevent partial/corrupt extraction.\n"
        )
        return

    pattern = rf"^{re.escape(boundary)}$"
    parts = re.split(pattern, raw_text, flags=re.MULTILINE)

    tasks_by_file = {}

    for part in parts:
        if not part.strip() or part.strip().startswith("--"):
            continue

        part = part.lstrip()
        lines = part.splitlines()
        header_lines = []
        payload_lines = []
        in_header = True
        for line in lines:
            if in_header:
                if not line.strip():
                    in_header = False
                    continue
                if line.startswith(
                    ("Path: ", "Operation: ", "New-Path: ", "Mode: ", "Encoding: ")
                ):
                    header_lines.append(line)
                else:
                    in_header = False
                    payload_lines.append(line)
            else:
                payload_lines.append(line)

        if not header_lines:
            continue

        header = "\n".join(header_lines)
        payload = "\n".join(payload_lines)

        path_lines = [
            line_item
            for line_item in header.splitlines()
            if line_item.startswith("Path: ")
        ]
        if not path_lines:
            continue

        filepath = path_lines[0].replace("Path: ", "").strip()

        operation_lines = [
            line_item
            for line_item in header.splitlines()
            if line_item.startswith("Operation: ")
        ]
        operation = (
            operation_lines[0].replace("Operation: ", "").strip().lower()
            if operation_lines
            else "overwrite"
        )

        new_path_lines = [
            line_item
            for line_item in header.splitlines()
            if line_item.startswith("New-Path: ")
        ]
        new_filepath = (
            new_path_lines[0].replace("New-Path: ", "").strip()
            if new_path_lines
            else None
        )

        mode_lines = [
            line_item
            for line_item in header.splitlines()
            if line_item.startswith("Mode: ")
        ]
        mode_str = mode_lines[0].replace("Mode: ", "").strip() if mode_lines else None
        if terminator in payload:
            payload = payload.split(terminator)[0]

        # REJECTION GUARD: Fail instantly if the payload contains raw unencoded angle brackets or non-hex percent signs.
        if re.search(r"<|>|%(?![0-9a-fA-F]{2})", payload):
            tasks_by_file.setdefault(filepath, []).append(
                {
                    "error": "CRITICAL ENCODING ERROR: Payload contains unencoded '<', '>', or '%' characters. You MUST URL-encode these characters (%3C, %3E, %25)."
                }
            )
            continue

        # ALWAYS unquote, regardless of encoding header, because the new architecture enforces URL-encoding on all payloads
        import urllib.parse

        payload = urllib.parse.unquote(payload)

        try:
            payload = check_ai_foibles(payload, filepath)
        except ValueError as e:
            tasks_by_file.setdefault(filepath, []).append({"error": str(e)})
            continue

        payload = payload.rstrip() + "\n"

        task = {
            "operation": operation,
            "filepath": filepath,
            "new_filepath": new_filepath,
            "mode_str": mode_str,
            "payload": payload,
            "error": None,
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

    failed_files = []
    shortened_files = []

    for filepath, tasks in tasks_by_file.items():
        errors = []
        warnings = []

        for t in tasks:
            if t.get("error"):
                errors.append(t["error"])

        if errors:
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
            failed_files.append(filepath)
            continue

        target_dir = os.path.dirname(filepath)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)

        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    original_text = f.read()
                    current_text = original_text
            except Exception as e:
                errors.append(f"Failed to read existing file {filepath}: {e}")
                _print_summary(
                    filepath, errors, warnings, aborted=True, count=len(tasks)
                )
                failed_files.append(filepath)
                continue
        else:
            original_text = None
            current_text = ""

        file_mutated = False
        mode_int = None
        file_deleted = False
        renamed_to = None
        copied_to = None

        try:
            for task in tasks:
                op = task["operation"]

                # Normalize line endings to prevent drift when exact matching strings
                payload = task["payload"].replace("\r\n", "\n")
                if current_text:
                    current_text = current_text.replace("\r\n", "\n")

                mode_str = task["mode_str"]

                if mode_str:
                    try:
                        mode_int = int(mode_str, 8)
                    except ValueError:
                        raise ValueError(
                            f"Invalid mode format: {mode_str}. Must be octal."
                        )

                if op in ("delete", "remove"):
                    file_deleted = True
                    break

                elif op == "rename":
                    if not task["new_filepath"]:
                        raise ValueError("Rename requires 'New-Path: <target>'")
                    if not os.path.exists(filepath):
                        raise FileNotFoundError(
                            f"Cannot rename missing file: {filepath}"
                        )
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
                        raise FileNotFoundError(
                            f"Cannot chmod missing file: {filepath}"
                        )

                elif op == "overwrite":
                    current_text = payload
                    if not payload.strip():
                        warnings.append("[WARN] Extracted payload is empty.")
                    file_mutated = True

                elif op == "append":
                    if current_text and not current_text.endswith("\n"):
                        current_text += "\n"
                    current_text += payload
                    if not payload.strip():
                        warnings.append("[WARN] Appended payload is empty.")
                    file_mutated = True

                elif op == "search-and-replace":
                    if not os.path.exists(filepath) and not file_mutated:
                        raise FileNotFoundError(
                            f"Cannot search-and-replace missing file: {filepath}"
                        )

                    search_blocks = parse_search_replace_blocks(payload)

                    if not search_blocks:
                        raise ValueError(
                            "Malformed search-and-replace block. Missing markers."
                        )

                    for block in search_blocks:
                        search_text = block["search"]
                        replace_text = block["replace"]

                        new_text = None
                        if filepath.endswith(".py"):
                            new_text = semantic_token_replace(
                                current_text, search_text, replace_text
                            )
                            if new_text is None:
                                new_text = fuzzy_line_replace(
                                    current_text, search_text, replace_text
                                )
                            if new_text is None:
                                new_text = whitespace_agnostic_replace(
                                    current_text, search_text, replace_text
                                )
                        elif filepath.endswith(".md"):
                            new_text = semantic_markdown_replace(
                                current_text, search_text, replace_text
                            )
                            if new_text is None:
                                new_text = boundary_markdown_replace(
                                    current_text, search_text, replace_text
                                )
                            if new_text is None:
                                new_text = fuzzy_markdown_replace(
                                    current_text, search_text, replace_text
                                )
                            if new_text is None:
                                new_text = whitespace_agnostic_replace(
                                    current_text, search_text, replace_text
                                )
                        elif filepath.endswith(".xml"):
                            new_text = semantic_xml_replace(
                                current_text, search_text, replace_text
                            )
                            if new_text is None:
                                new_text = whitespace_agnostic_replace(
                                    current_text, search_text, replace_text
                                )
                        else:
                            new_text = whitespace_agnostic_replace(
                                current_text, search_text, replace_text
                            )

                        if new_text is None:
                            raise ValueError(
                                "Semantic token, fuzzy line, and whitespace fallback all failed for search block."
                            )
                        current_text = new_text
                    file_mutated = True

            if file_mutated:
                validate_syntax_in_memory(filepath, current_text)

        except Exception as e:
            errors.append(str(e))

        if errors:
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
            failed_files.append(filepath)
            continue

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
                if filepath.endswith((".py", ".xml", ".md", ".js", ".html")):
                    current_text = re.sub(
                        r"[ \t]+$", "", current_text, flags=re.MULTILINE
                    )

                if original_text is not None:
                    orig_lines = len(original_text.splitlines())
                    new_lines = len(current_text.splitlines())
                    if new_lines < orig_lines:
                        shortened_files.append(
                            f"{filepath} ({orig_lines} -> {new_lines} lines)"
                        )

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(current_text)

                if filepath.endswith(".py"):
                    try:
                        subprocess.run(
                            [sys.executable, "-m", "black", "-q", filepath], check=True
                        )
                    except Exception as e:
                        warnings.append(f"[WARN] Black formatting failed: {e}")

            if mode_int is not None:
                os.chmod(filepath, mode_int)

            ext = os.path.splitext(filepath)[1].lower()
            post_errors = []

            if ext == ".py":
                err = verify_python(filepath)
                if err:
                    if err.startswith("[WARN]"):
                        warnings.append(err)
                    else:
                        post_errors.append(err)
            elif ext == ".xml":
                err = verify_xml(filepath)
                if err:
                    if err.startswith("[WARN]"):
                        warnings.append(err)
                    else:
                        post_errors.append(err)
            elif ext == ".md":
                err = verify_markdown(filepath)
                if err:
                    if err.startswith("[WARN]"):
                        warnings.append(err)
                    else:
                        post_errors.append(err)
            elif ext == ".json":
                err = verify_json(filepath)
                if err:
                    if err.startswith("[WARN]"):
                        warnings.append(err)
                    else:
                        post_errors.append(err)

            if ext in (".py", ".xml", ".js"):
                err = run_burn_list_linter(filepath)
                if err:
                    if err.startswith("[WARN]"):
                        warnings.append(err)
                    else:
                        post_errors.append(err)

            if post_errors:
                if file_mutated:
                    if original_text is not None:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(original_text)
                    else:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                errors.extend(post_errors)
                _print_summary(
                    filepath, errors, warnings, aborted=True, count=len(tasks)
                )
                failed_files.append(filepath)
                continue

            _print_summary(filepath, errors, warnings, aborted=False, count=len(tasks))

        except Exception as e:
            errors.append(f"Commit failed: {e}")
            _print_summary(filepath, errors, warnings, aborted=True, count=len(tasks))
            failed_files.append(filepath)

    if failed_files:
        print(f"\n❌ Failed to extract: {', '.join(failed_files)}")

    if shortened_files:
        print("\n" + "!" * 80)
        print("WARNING: THE FOLLOWING FILES BECAME SHORTER!")
        print("VERIFY THAT NO ACCIDENTAL TRUNCATION OR LAZINESS OCCURRED.")
        for sf in shortened_files:
            print(f"  - {sf}")
        print("!" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                input_data = f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{sys.argv[1]}' not found.\n")
            sys.exit(1)
    else:
        input_data = sys.stdin.read()

    extract_parcel(input_data)
