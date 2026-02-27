#!/usr/bin/env python3
import re
import os
import sys
import json
import argparse
import base64
import urllib.parse
import shutil  # noqa: F401

def extract_json_payloads(input_text):
    # Sanitize common Web UI copy-paste artifacts
    input_text = input_text.replace('\xa0', ' ')  # Non-breaking spaces to regular spaces
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

def parse_json_and_write_files(input_text, base_dir="."):
    payload_texts = extract_json_payloads(input_text)
    all_files = []
    version = "legacy"
    
    for payload_text in payload_texts:
        try:
            payload = json.loads(payload_text, strict=False)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode failed ({e}). Attempting RegEx/AST recovery...")
            # 1. Strip illegal trailing commas before closing braces/brackets
            payload_text_clean = re.sub(r',\s*([\]}])', r'\1', payload_text)
            try:
                payload = json.loads(payload_text_clean, strict=False)
                print("✅ RegEx recovery successful.")
            except json.JSONDecodeError:
                print("⚠️ RegEx recovery failed. Falling back to AST literal_eval...")
                import ast
                try:
                    # 2. Map JSON primitives to Python primitives for AST parsing
                    ast_text = re.sub(r'\btrue\b', 'True', payload_text_clean)
                    ast_text = re.sub(r'\bfalse\b', 'False', ast_text)
                    ast_text = re.sub(r'\bnull\b', 'None', ast_text)
                    payload = ast.literal_eval(ast_text)
                    print("✅ AST literal_eval recovery successful.")
                except Exception as ast_e:
                    print(f"❌ AST recovery failed: {ast_e}")
                    print("🚨 The payload is too severely mangled to recover. If using a Web UI, check if the LLM output was truncated!")
                    continue

        if isinstance(payload, dict):
            version = payload.get("aef_version", version)
            all_files.extend(payload.get("files", []))
            
    files = all_files
    if not files:
        print("❌ No valid files found in the payload.")
        sys.exit(1)
        
    print(f"🔍 Found {len(files)} files to process (AEF {version})...")

    abs_base_dir = os.path.abspath(base_dir)

    for file_data in files:
        filepath = file_data.get("path", "").strip()
        operation = file_data.get("operation", "overwrite")
        content_raw = file_data.get("content", "")
        encoding = file_data.get("encoding", "utf-8")

        if not filepath:
            continue

        # SECURITY: Path Traversal Protection
        full_path = os.path.abspath(os.path.join(abs_base_dir, filepath))
        if not full_path.startswith(abs_base_dir):
            print(f"🚨 SECURITY ALERT: Path traversal blocked for '{filepath}'.")
            continue

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        try:
            if operation == "search-and-replace":
                blocks = file_data.get("blocks", [])
                if not os.path.exists(full_path):
                    print(f"❌ Error: File not found for patching: {filepath}")
                    continue
                    
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_text = f.read()
                    
                # Phase 1: Pre-flight validation
                valid_blocks = []
                abort_file = False
                for idx, block in enumerate(blocks):
                    search_raw = block.get("search", [])
                    replace_raw = block.get("replace", [])
                    
                    if encoding in ["url-encoded", "url", "percent-encoded"]:
                        search_text = "".join([urllib.parse.unquote(line) for line in search_raw]) if isinstance(search_raw, list) else urllib.parse.unquote(search_raw)
                        replace_text = "".join([urllib.parse.unquote(line) for line in replace_raw]) if isinstance(replace_raw, list) else urllib.parse.unquote(replace_raw)
                    else:
                        search_text = "".join(search_raw) if isinstance(search_raw, list) else search_raw
                        replace_text = "".join(replace_raw) if isinstance(replace_raw, list) else replace_raw

                    # Anti-Corruption Guard: Check for LLM laziness placeholders in the replacement text
                    lazy_patterns = [
                        r'\/\/ \.\.\.', r'# \.\.\.', r'<\!\-\- \.\.\. \-\->',
                        r'\.\.\. rest of', r'\[\s*Code unchanged\s*\]',
                        r'\(\s*rest of method\s*\)', r'\(\s*Code unchanged\s*\)'
                    ]
                    
                    # Linter avoidance strategy: Meta-files that define these rules are exempt from the guard
                    is_meta_file = filepath.endswith('AGENTS.md') or 'LLM_' in filepath or filepath.endswith('aef_create.py') or filepath.endswith('aef_extract.py')

                    if not filepath.endswith(".md") and not is_meta_file and any(re.search(pat, replace_text, re.IGNORECASE) for pat in lazy_patterns):
                        print(f"❌ Error: LLM hallucinated a truncation placeholder in the replacement block for {filepath}. Aborting file patch to prevent deleting code.")
                        abort_file = True
                        break
                        
                    match_count = file_text.count(search_text)
                    search_regex = None
                    
                    if match_count == 0:
                        # Fallback: Ignore whitespace differences
                        parts = [re.escape(p) for p in re.split(r'\s+', search_text) if p]
                        if parts:
                            pattern = r'\s+'.join(parts)
                            search_regex = re.compile(pattern)
                            matches = list(search_regex.finditer(file_text))
                            match_count = len(matches)
                            
                            if match_count == 1:
                                print(f"⚠️  Note: Search block {idx+1} matched using flexible whitespace fallback.")
                                # Determine leading/trailing spaces to correctly trim replace_text
                                search_leading_ws_match = re.match(r'^\s*', search_text)
                                search_trailing_ws_match = re.search(r'\s*$', search_text)
                                search_leading_ws = search_leading_ws_match.group() if search_leading_ws_match else ""
                                search_trailing_ws = search_trailing_ws_match.group() if search_trailing_ws_match else ""
                                
                                if replace_text.startswith(search_leading_ws):
                                    replace_text = replace_text[len(search_leading_ws):]
                                if replace_text.endswith(search_trailing_ws) and len(search_trailing_ws) > 0:
                                    replace_text = replace_text[:-len(search_trailing_ws)]

                    if match_count == 0:
                        import difflib
                        print(f"⚠️  Note: Search block {idx+1} regex fallback failed. Attempting fuzzy match...")
                        search_lines = search_text.splitlines(keepends=True)
                        file_lines = file_text.splitlines(keepends=True)
                        best_ratio = 0
                        best_idx = -1
                        best_window = 0
                        base_window = len(search_lines)
                        
                        if base_window > 0:
                            # Try windows of sizes -1, 0, +1 relative to the search block length
                            for w_offset in [-1, 0, 1]:
                                window_size = base_window + w_offset
                                if window_size > 0 and len(file_lines) >= window_size:
                                    for i in range(len(file_lines) - window_size + 1):
                                        window_text = "".join(file_lines[i:i+window_size])
                                        ratio = difflib.SequenceMatcher(None, search_text, window_text).ratio()
                                        if ratio > best_ratio:
                                            best_ratio = ratio
                                            best_idx = i
                                            best_window = window_size
                                            
                            if best_ratio >= 0.85:
                                print(f"✅ Fuzzy match found with {best_ratio*100:.1f}% similarity.")
                                search_text = "".join(file_lines[best_idx:best_idx+best_window])
                                search_regex = None
                                match_count = 1

                    if match_count == 0:
                        print(f"❌ Error: Search block {idx+1} not found in {filepath}. Aborting file patch to prevent corruption.")
                        abort_file = True
                        break
                    elif match_count > 1:
                        print(f"❌ Error: Search block {idx+1} matches {match_count} times in {filepath}. Aborting due to ambiguity.")
                        abort_file = True
                        break
                    
                    valid_blocks.append((search_text, replace_text, search_regex))
                    
                if abort_file:
                    continue
                    
                # Phase 2: Execution in memory
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
                    
                # Phase 3: Atomic write
                tmp_path = full_path + ".tmp"
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    f.write(file_text)
                if os.path.exists(full_path):
                    shutil.copymode(full_path, tmp_path)
                os.replace(tmp_path, full_path)
                
                print(f"✅ Patched (search-and-replace): {filepath}")
                continue

            if encoding == "base64":
                if isinstance(content_raw, list):
                    b64_string = "".join(content_raw)
                else:
                    b64_string = content_raw
                b64_string = b64_string.replace('\n', '').strip()
                file_bytes = base64.b64decode(b64_string)
                
            elif encoding in ["url-encoded", "url", "percent-encoded"]:
                if isinstance(content_raw, list):
                    content = "".join([urllib.parse.unquote(line) for line in content_raw])
                else:
                    content = urllib.parse.unquote(content_raw)
                file_bytes = content.encode('utf-8')
            else:
                if isinstance(content_raw, list):
                    content = "".join(content_raw)
                else:
                    content = content_raw
                file_bytes = content.encode('utf-8')

            if operation == "overwrite":
                tmp_path = full_path + ".tmp"
                with open(tmp_path, 'wb') as f:
                    f.write(file_bytes)
                if os.path.exists(full_path):
                    shutil.copymode(full_path, tmp_path)
                os.replace(tmp_path, full_path)
                print(f"✅ Wrote: {filepath}")
            else:
                print(f"❌ Unknown operation '{operation}' for {filepath}")

        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Extract files from AEF output.")
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
    main()
