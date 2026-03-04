#!/usr/bin/env python3
import re
import os
import sys
import json
import argparse
import urllib.parse
import shutil
import ast
import difflib
import warnings

MAX_LINE_LENGTH = 3000

def validate_line_length(data, file_name, block_name):
    if isinstance(data, list):
        for i, line in enumerate(data):
            if len(line) > MAX_LINE_LENGTH:
                print(f"❌ Error: Line {i+1} in {block_name} of {file_name} exceeds {MAX_LINE_LENGTH} characters. Use shorter lines.")
                return False
    elif isinstance(data, str):
        if len(data) > MAX_LINE_LENGTH:
            print(f"❌ Error: {block_name} of {file_name} exceeds {MAX_LINE_LENGTH} characters. Split into an array of shorter lines.")
            return False
    return True

def extract_json_payloads(input_text):
    input_text = input_text.replace('\xa0', ' ')
    input_text = input_text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    
    pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)
    matches = pattern.findall(input_text)
    if matches:
        return matches
        
    start_idx = input_text.find('{')
    if start_idx != -1:
        end_idx = input_text.rfind('}')
        if end_idx != -1 and end_idx > start_idx:
            return [input_text[start_idx:end_idx+1]]
        else:
            return [input_text[start_idx:]]
    return [input_text.strip()]

def _recover_json(payload_text):
    try:
        return json.loads(payload_text, strict=False)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode failed ({e}). Attempting RegEx/AST recovery...")
        
    payload_text_clean = re.sub(r',\s*([\]\}])', r'\1', payload_text)
    try:
        payload = json.loads(payload_text_clean, strict=False)
        print("✅ RegEx recovery successful.")
        return payload
    except json.JSONDecodeError:
        print("⚠️ RegEx recovery failed. Falling back to AST literal_eval...")
        
    try:
        ast_text = re.sub(r'\btrue\b', 'True', payload_text_clean)
        ast_text = re.sub(r'\bfalse\b', 'False', ast_text)
        ast_text = re.sub(r'\bnull\b', 'None', ast_text)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            payload = ast.literal_eval(ast_text)
        print("✅ AST literal_eval recovery successful.")
        return payload
    except Exception as ast_e:
        print(f"❌ AST recovery failed: {ast_e}")
        print("🚨 The payload is too severely mangled to recover. If using a Web UI, check if the LLM output was truncated!")
        return None

def _decode_blocks(blocks, encoding):
    decoded_blocks = []
    for block in blocks:
        search_raw = block.get("search", [])
        replace_raw = block.get("replace", [])
        search_str = "".join(search_raw) if isinstance(search_raw, list) else search_raw
        replace_str = "".join(replace_raw) if isinstance(replace_raw, list) else replace_raw

        if encoding in ["url-encoded", "url", "percent-encoded"]:
            # if "%20" in search_str or "%20" in replace_str:
            #     raise ValueError("CRITICAL: Payload contains '%20'. Spaces must NOT be percent-encoded. Use raw spaces.")
            # Enforcement on hold until LLMs have a broader cognitive horizon or better token generation constraints.
            search_text = urllib.parse.unquote(search_str)
            replace_text = urllib.parse.unquote(replace_str)
        else:
            search_text = search_str
            replace_text = replace_str

        replace_text = re.sub(r'^```[a-zA-Z0-9]*\n', '', replace_text)
        replace_text = re.sub(r'\n```\s*$', '\n', replace_text)
        search_text = re.sub(r'^```[a-zA-Z0-9]*\n', '', search_text)
        search_text = re.sub(r'\n```\s*$', '\n', search_text)
        
        decoded_blocks.append((search_text, replace_text, search_str))
    return decoded_blocks

def _check_for_laziness(filepath, replace_text):
    lazy_patterns = [
        r'\/\/ \.\.\.', r'# \.\.\.', r'<\!\-\- \.\.\. \-\->',
        r'\.\.\. rest of', r'\[\s*Code unchanged\s*\]',
        r'\(\s*rest of method\s*\)', r'\(\s*Code unchanged\s*\)'
    ]
    is_meta_file = filepath.endswith('AGENTS.md') or 'LLM_' in filepath or filepath.endswith('simple_create.py') or filepath.endswith('parcel_extract.py')
    
    if not filepath.endswith(".md") and not is_meta_file:
        for pat in lazy_patterns:
            if re.search(pat, replace_text, re.IGNORECASE):
                return True
    return False

def _strip_whitespace(text):
    return re.sub(r'\s+', '', text)

def _apply_fuzzy_match(search_text, file_text, idx):
    print(f"⚠️  Note: Search block {idx+1} regex fallback failed. Attempting fuzzy match...")
    search_lines = search_text.splitlines(keepends=True)
    file_lines = file_text.splitlines(keepends=True)
    
    base_window = len(search_lines)
    if base_window == 0:
        return search_text, 0
        
    search_stripped = _strip_whitespace(search_text)
    search_len = len(search_stripped)
    
    # Dynamic threshold scaling based on character length
    if search_len < 50:
        threshold = 0.95
    elif search_len > 500:
        threshold = 0.75
    else:
        threshold = 0.95 - (0.20 * ((search_len - 50) / 450))

    best_ratio = 0
    best_idx = -1
    best_window = 0
    
    for w_offset in [-2, -1, 0, 1, 2]:
        window_size = base_window + w_offset
        if window_size <= 0 or len(file_lines) < window_size:
            continue
            
        for i in range(len(file_lines) - window_size + 1):
            window_text = "".join(file_lines[i:i+window_size])
            window_stripped = _strip_whitespace(window_text)
            
            sm = difflib.SequenceMatcher(None, search_stripped, window_stripped)
            if sm.real_quick_ratio() < threshold - 0.10:
                continue
                
            ratio = sm.ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = i
                best_window = window_size
                
    if best_ratio >= threshold:
        print(f"✅ Fuzzy match found with {best_ratio*100:.1f}% similarity (Threshold: {threshold*100:.1f}%).")
        return "".join(file_lines[best_idx:best_idx+best_window]), 1
        
    print(f"❌ Fuzzy match failed. Best ratio was {best_ratio*100:.1f}% (Needed {threshold*100:.1f}%).")
    return search_text, 0

def _apply_whitespace_match(search_text, file_text, replace_text, idx):
    parts = [re.escape(p) for p in re.split(r'\s+', search_text) if p]
    if not parts:
        return search_text, replace_text, None, 0
        
    pattern = r'\s+'.join(parts)
    search_regex = re.compile(pattern)
    matches = list(search_regex.finditer(file_text))
    match_count = len(matches)
    
    if match_count == 1:
        print(f"⚠️  Note: Search block {idx+1} matched using flexible whitespace fallback.")
        search_leading_ws_match = re.match(r'^\s*', search_text)
        search_trailing_ws_match = re.search(r'\s*$', search_text)
        search_leading_ws = search_leading_ws_match.group() if search_leading_ws_match else ""
        search_trailing_ws = search_trailing_ws_match.group() if search_trailing_ws_match else ""
        
        if replace_text.startswith(search_leading_ws):
            replace_text = replace_text[len(search_leading_ws):]
        if replace_text.endswith(search_trailing_ws) and len(search_trailing_ws) > 0:
            replace_text = replace_text[:-len(search_trailing_ws)]
            
    return search_text, replace_text, search_regex, match_count

def _process_search_and_replace(full_path, filepath, blocks, encoding):
    if not os.path.exists(full_path):
        print(f"❌ Error: File not found for patching: {filepath}")
        return False
        
    with open(full_path, 'r', encoding='utf-8') as f:
        file_text = f.read()
        
    decoded_blocks = _decode_blocks(blocks, encoding)
    valid_blocks = []
    
    for idx, (search_text, replace_text, search_raw_str) in enumerate(decoded_blocks):
        if _check_for_laziness(filepath, replace_text):
            print(f"❌ Error: LLM hallucinated a truncation placeholder in the replacement block for {filepath}. Aborting file patch to prevent deleting code.")
            return False
            
        match_count = file_text.count(search_text)
        search_regex = None
        
        if match_count == 0 and search_text != search_raw_str:
            if file_text.count(search_raw_str) > 0:
                print(f"⚠️  Note: Search block {idx+1} matched using raw (unquoted) string fallback due to missing double-encoding.")
                search_text = search_raw_str
                match_count = file_text.count(search_text)
        
        if match_count == 0:
            search_text, replace_text, search_regex, match_count = _apply_whitespace_match(search_text, file_text, replace_text, idx)
            
        if match_count == 0:
            search_text, match_count = _apply_fuzzy_match(search_text, file_text, idx)
            search_regex = None
            
        if match_count == 0:
            print(f"❌ Error: Search block {idx+1} not found in {filepath}. Aborting file patch to prevent corruption.")
            return False
        elif match_count > 1:
            print(f"❌ Error: Search block {idx+1} matches {match_count} times in {filepath}. Aborting due to ambiguity.")
            return False
            
        valid_blocks.append((search_text, replace_text, search_regex))
        
    for search_text, replace_text, search_regex in valid_blocks:
        if search_regex:
            match = search_regex.search(file_text)
            if match:
                start, end = match.span()
                matched_str = match.group()
                actual_leading_ws = re.match(r'^\s*', matched_str).group()
                actual_trailing_ws = re.search(r'\s*$', matched_str).group()
                final_replace = actual_leading_ws + replace_text + actual_trailing_ws
                file_text = file_text[:start] + final_replace + file_text[end:]
        else:
            file_text = file_text.replace(search_text, replace_text, 1)
            
    tmp_path = full_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(file_text)
    if os.path.exists(full_path):
        shutil.copymode(full_path, tmp_path)
    os.replace(tmp_path, full_path)
    print(f"✅ Patched (search-and-replace): {filepath}")
    return True

def _process_ast_replace(full_path, filepath, file_data, encoding):
    if not os.path.exists(full_path):
        print(f"❌ Error: File not found for AST patching: {filepath}")
        return False
        
    target_name = file_data.get("target_name")
    target_type = file_data.get("target_type", "function")
    parent_class = file_data.get("parent_class")
    content_raw = file_data.get("content", "")
    
    if not target_name:
        print("❌ Error: AST replace requires 'target_name'.")
        return False

    content_str = "".join(content_raw) if isinstance(content_raw, list) else content_raw
    if encoding in ["url-encoded", "url", "percent-encoded"]:
        replace_text = urllib.parse.unquote(content_str)
    else:
        replace_text = content_str

    replace_text = re.sub(r'^```[a-zA-Z0-9]*\n', '', replace_text)
    replace_text = re.sub(r'\n```\s*$', '\n', replace_text)

    with open(full_path, 'r', encoding='utf-8') as f:
        file_text = f.read()
        
    try:
        tree = ast.parse(file_text, filename=filepath)
    except SyntaxError as e:
        print(f"❌ Error: Cannot perform AST replace. Target file {filepath} has invalid syntax: {e}")
        return False

    target_node = None
    nodes_to_search = []

    if parent_class:
        class_node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == parent_class), None)
        if not class_node:
            print(f"❌ Error: Parent class '{parent_class}' not found in {filepath}.")
            return False
        nodes_to_search = ast.walk(class_node)
    else:
        nodes_to_search = ast.walk(tree)
        
    for node in nodes_to_search:
        if target_type == "function" and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == target_name:
                target_node = node
                break
        elif target_type == "class" and isinstance(node, ast.ClassDef):
            if node.name == target_name:
                target_node = node
                break

    if not target_node:
        print(f"❌ Error: Target {target_type} '{target_name}' not found in {filepath}.")
        return False
        
    end_line = getattr(target_node, 'end_lineno', None)
    if end_line is None:
        print("❌ Error: Python version does not support end_lineno in AST. Cannot perform AST replace.")
        return False

    real_start_line = target_node.lineno
    if hasattr(target_node, 'decorator_list') and target_node.decorator_list:
        real_start_line = min(d.lineno for d in target_node.decorator_list)
        
    file_lines = file_text.splitlines(keepends=True)
    new_lines = file_lines[:real_start_line - 1] + [replace_text] + (['\n'] if not replace_text.endswith('\n') else []) + file_lines[end_line:]
    
    tmp_path = full_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write("".join(new_lines))
    if os.path.exists(full_path):
        shutil.copymode(full_path, tmp_path)
    os.replace(tmp_path, full_path)
    print(f"✅ Patched (ast-replace): {filepath} ({target_type} '{target_name}')")
    return True

def _process_file(file_data, abs_base_dir):
    filepath = file_data.get("path", "").strip()
    operation = file_data.get("operation", "overwrite")
    content_raw = file_data.get("content", "")
    encoding = file_data.get("encoding", "url-encoded")

    if not filepath:
        return

    if not validate_line_length(content_raw, filepath, "content"):
        return

    if encoding not in ["url-encoded", "url", "percent-encoded"]:
        print(f"❌ Error: File {filepath} rejected. You MUST use 'url-encoded'. Legacy encodings and backslash escapes are strictly forbidden.")
        return

    full_path = os.path.abspath(os.path.join(abs_base_dir, filepath))
    if not full_path.startswith(abs_base_dir):
        print(f"🚨 SECURITY ALERT: Path traversal blocked for '{filepath}'.")
        return

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    try:
        if operation == "ast-replace":
            _process_ast_replace(full_path, filepath, file_data, encoding)
            return

        if operation == "search-and-replace":
            blocks = file_data.get("blocks", [])
            valid_length = True
            for idx, block in enumerate(blocks):
                if not validate_line_length(block.get("search", ""), filepath, f"search block {idx+1}"):
                    valid_length = False
                if not validate_line_length(block.get("replace", ""), filepath, f"replace block {idx+1}"):
                    valid_length = False
            if not valid_length:
                return
            _process_search_and_replace(full_path, filepath, blocks, encoding)
            return

        content_str = "".join(content_raw) if isinstance(content_raw, list) else content_raw
        
        # if encoding in ["url-encoded", "url", "percent-encoded"] and "%20" in content_str:
        #     print(f"❌ Error: File {filepath} rejected. Payload contains '%20'. Spaces must NOT be percent-encoded.")
        #     return
        # %20 prohibition enforcement on hold until LLMs have a broader cognitive horizon.

        content = urllib.parse.unquote(content_str)
        file_bytes = content.encode('utf-8')

        if operation == "overwrite":
            tmp_path = full_path + ".tmp"
            with open(tmp_path, 'wb') as f:
                f.write(file_bytes)
            if os.path.exists(full_path):
                shutil.copymode(full_path, tmp_path)
            os.replace(tmp_path, full_path)
            print(f"✅ Wrote: {filepath}")
        elif operation == "delete":
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"🗑️ Deleted: {filepath}")
            else:
                print(f"⚠️  Note: File already missing or deleted: {filepath}")
        else:
            print(f"❌ Unknown operation '{operation}' for {filepath}")

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

def parse_json_and_write_files(input_text, base_dir="."):
    payload_texts = extract_json_payloads(input_text)
    all_files = []
    version = "legacy"
    
    for payload_text in payload_texts:
        payload = _recover_json(payload_text)
        if payload and isinstance(payload, dict):
            version = payload.get("parcel_version", payload.get("aef_version", version))
            all_files.extend(payload.get("files", []))
            
    if not all_files:
        print("❌ No valid files found in the payload.")
        sys.exit(1)
        
    print(f"🔍 Found {len(all_files)} files to process (Parcel {version})...")
    abs_base_dir = os.path.abspath(base_dir)

    for file_data in all_files:
        _process_file(file_data, abs_base_dir)

def main():
    parser = argparse.ArgumentParser(description="Extract files from Parcel output.")
    parser.add_argument("input_file", nargs='?', help="Path to the file containing LLM output.")
    
    args = parser.parse_args()
    input_text = ""

    if args.input_file:
        if os.path.exists(args.input_file):
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        else:
            print(f"❌ File not found: {args.input_file}")
            sys.exit(1)
    else:
        print("📥 Reading from Standard Input (Press Ctrl+D to finish)...")
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            sys.exit(0)

    if not input_text.strip():
        print("❌ No content received.")
        sys.exit(1)

    parse_json_and_write_files(input_text)
    print("\n🏁 Processing complete.")

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        main()
