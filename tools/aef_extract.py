#!/usr/bin/env python3
import re
import os
import sys
import json
import argparse
import base64
import urllib.parse
import subprocess
import shutil

def extract_json_payload(input_text):
    pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)
    match = pattern.search(input_text)
    if match:
        return match.group(1)
    start_idx = input_text.find('{')
    if start_idx != -1:
        end_idx = input_text.rfind('}')
        if end_idx != -1 and end_idx > start_idx:
            return input_text[start_idx:end_idx+1]
        else:
            return input_text[start_idx:]
    return input_text.strip()

def parse_json_and_write_files(input_text, base_dir="."):
    payload_text = extract_json_payload(input_text)
    try:
        payload = json.loads(payload_text, strict=False)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding failed: {e}")
        sys.exit(1)

    version = payload.get("aef_version", "legacy")
    files = payload.get("files", [])
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
                
            elif operation == "diff":
                patch_path = full_path + ".patch"
                backup_path = full_path + ".bak"
                
                with open(patch_path, 'wb') as f:
                    f.write(file_bytes)
                    
                if os.path.exists(full_path):
                    shutil.copy2(full_path, backup_path)
                    
                try:
                    subprocess.run(["patch", "-p1", "--ignore-whitespace", "--no-backup-if-mismatch", "-i", os.path.abspath(patch_path)], cwd=abs_base_dir, check=True)
                    print(f"✅ Patched (diff): {filepath}")
                except Exception as e:
                    print(f"❌ Error applying diff to {filepath}: {e}. Rolling back to prevent corruption.")
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, full_path)
                finally:
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    if os.path.exists(patch_path):
                        os.remove(patch_path)
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
