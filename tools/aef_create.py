#!/usr/bin/env python3
import os
import sys
import json
import base64

IGNORE_DIRS = {'__pycache__', 'venv', 'env', '.git', '.idea', '.vscode', 'node_modules'}
IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.class', '.exe', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.zip', '.tar', '.gz'}
IGNORE_FILES = {'id_rsa', 'id_rsa.pub', 'known_hosts', 'authorized_keys'}

SYSTEM_PROMPT = """You are an expert AI developer assistant operating in a strict, zero-guessing environment.
Below is the current project state formatted as an AEF 4.0 JSON object.

**CRITICAL INSTRUCTIONS:**
1. Before answering my request, you MUST read and adopt all operational mandates found in the LLM_GENERAL_REQUIREMENTS.md and LLM_ODOO_REQUIREMENTS.md files included in this JSON.
2. When generating or modifying code, you MUST output your response using this exact same AEF 4.0 JSON schema inside a single ```json code block.
3. AEF 4.0 ASYMMETRIC TRANSPORT MANDATE: The project state provided to you here is Base64 encoded. Your generated `content` (or `search`/`replace`) field MUST be an array of plain text strings (one string per line, ending with `\n`). You MUST specify `"encoding": "utf-8"`.
4. JSON SAFETY & SELECTIVE URL-ENCODING: To prevent JSON syntax errors from unescaped quotes or backslashes, you MUST use `"encoding": "url-encoded"` and selectively percent-encode ONLY `\"` (to `%22`), `\\` (to `%5C`), `<` (to `%3C`), `>` (to `%3E`), and `&` (to `%26`). Do NOT globally encode spaces or newlines.
5. PRESENTATION MANDATE: You MUST explain your code changes and provide human-readable snippets outside the JSON block so the user can review them. (Ensure you intentionally break UI-crashing tags in your explanation, like writing `< !--` instead of the actual HTML comment tag).
6. THE PERFECT PATCH MANDATE (search-and-replace): To guarantee accurate patching, your `search` block MUST: 1) Be an exact, character-for-character copy of the target file's lines, preserving all original indentation. 2) Include exactly 2-3 lines of unmodified surrounding context to ensure a unique match. 3) Target a maximum of 10-15 lines; if changing distant areas, output multiple small `search-and-replace` blocks.
7. ABSOLUTE COMPLETENESS: Your `replace` blocks MUST be syntactically whole and executable as-is. You MUST explicitly type every single character, variable, and line of the code you are modifying from start to finish.

**MY REQUEST:** [Insert your question/instruction here]
"""

def generate_json_from_project(root_dir="."):
    root_path = os.path.abspath(root_dir)
    payload = {"aef_version": "4.0", "files": []}

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in IGNORE_DIRS]

        for filename in filenames:
            if filename.startswith('.') or filename in IGNORE_FILES:
                continue
            
            _, ext = os.path.splitext(filename)
            if ext.lower() in IGNORE_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_path).replace('\\', '/')

            try:
                # Read as binary to handle all files cleanly
                with open(filepath, 'rb') as f:
                    file_bytes = f.read()
                    
                # Encode to Base64 string
                b64_string = base64.b64encode(file_bytes).decode('utf-8')
                
                # Chunk into 80-character segments for terminal safety
                chunk_size = 80
                b64_chunks = [b64_string[i:i+chunk_size] + "\n" for i in range(0, len(b64_string), chunk_size)]
                
                payload["files"].append({
                    "path": rel_path,
                    "encoding": "base64",
                    "content": b64_chunks
                })
            except Exception as e:
                sys.stderr.write(f"Error reading {rel_path}: {e}\n")

    print(SYSTEM_PROMPT)
    print("```json")
    print(json.dumps(payload, indent=2))
    print("```\n")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_json_from_project(target_dir)
