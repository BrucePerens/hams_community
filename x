#!/usr/bin/env bash
''':'
# --- Bash Execution Environment ---
if [ ! -d ".venv" ]; then
    echo "[*] Setting up Python virtual environment in .venv..."
    python3 -m venv .venv
fi

# Ensure required packages are installed
.venv/bin/pip install -q rich

exec .venv/bin/python "$0" "$@"
'''

# --- Python Execution Environment ---
import os
import sys
import re
from rich.console import Console
from rich.markdown import Markdown

# Inject local tools directory into path so we can import aef_extract natively
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aef_extract
except ImportError:
    print("[!] Error: Could not import aef_extract.py. File writing will fail.")
    sys.exit(1)

console = Console()

def is_hidden(filename):
    return filename.startswith('.')

def is_binary(filepath):
    try:
        with open(filepath, 'tr') as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True

def get_directory_contents(target_paths):
    """Reads files from requested paths, skipping hidden/binary files."""
    contents = []
    exclude_dirs = {'__pycache__', 'node_modules', 'build', 'dist', 'target', 'venv', 'env', '.venv', '.git'}
    max_file_size = 100 * 1024 
    
    for target_path in target_paths:
        if not os.path.exists(target_path):
            print(f"[!] Warning: Path '{target_path}' does not exist.")
            continue
            
        if os.path.isfile(target_path):
            if not is_hidden(os.path.basename(target_path)) and not is_binary(target_path) and os.path.getsize(target_path) <= max_file_size:
                try:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        data = f.read()
                    contents.append(f"--- FILE: {target_path} ---\n{data}\n--- END FILE: {target_path} ---")
                except Exception:
                    pass
        else:
            for root, dirs, files in os.walk(target_path):
                dirs[:] = [d for d in dirs if not is_hidden(d) and d not in exclude_dirs]
                for file in files:
                    if is_hidden(file): continue
                    filepath = os.path.join(root, file)
                    if os.path.abspath(filepath) == os.path.abspath(__file__): continue
                    if os.path.getsize(filepath) > max_file_size: continue

                    if not is_binary(filepath):
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                data = f.read()
                            contents.append(f"--- FILE: {filepath} ---\n{data}\n--- END FILE: {filepath} ---")
                        except Exception:
                            pass
    return "\n\n".join(contents)

def generate_context_file(target_paths):
    """Bundles rules and local files into a single prompt for the Web UI."""
    print("[*] Gathering local files for context...")
    
    dynamic_rules = ""
    for rule_file in ['AGENTS.md', 'docs/LLM_GENERAL_REQUIREMENTS.md', 'docs/LLM_ODOO_REQUIREMENTS.md']:
        if os.path.exists(rule_file):
            with open(rule_file, 'r', encoding='utf-8') as f:
                dynamic_rules += f"\n\n--- CONTENTS OF {rule_file} ---\n" + f.read()

    system_instruction = (
        "You are an expert developer. When generating or modifying code, you MUST output your response using the AEF 4.0 JSON schema inside a single ```json code block.\n"
        "CRITICAL AEF 4.0 ASYMMETRIC TRANSPORT MANDATE: Your generated `content` (or `search`/`replace`) field MUST be an array of plain text strings (one string per line, ending with '\\n'). You MUST specify `\"encoding\": \"utf-8\"`.\n"
        "JSON SAFETY & SELECTIVE URL-ENCODING: To prevent JSON syntax errors from unescaped quotes or backslashes, you MUST use `\"encoding\": \"url-encoded\"` and selectively percent-encode ONLY `\"` (to `%22`), `\\` (to `%5C`), `<` (to `%3C`), `>` (to `%3E`), and `&` (to `%26`). Do NOT globally encode spaces or newlines.\n"
        "THE PERFECT PATCH MANDATE (search-and-replace): To guarantee accurate patching, your `search` block MUST: 1) Be an exact, character-for-character copy of the target file's lines, preserving all original indentation. 2) Include exactly 2-3 lines of unmodified surrounding context to ensure a unique match. 3) Target a maximum of 10-15 lines; if changing distant areas, output multiple small blocks.\n"
        "ABSOLUTE COMPLETENESS: Your `replace` blocks MUST be syntactically whole and executable as-is. You MUST explicitly type every single character, variable, and line of the code you are modifying from start to finish.\n"
        "Format:\n"
        "```json\n"
        "{\n"
        "  \"aef_version\": \"4.0\",\n"
        "  \"files\": [\n"
        "    {\n"
        "      \"path\": \"path/to/file.ext\",\n"
        "      \"encoding\": \"utf-8\",\n"
        "      \"content\": [\n"
        "        \"line 1\\n\",\n"
        "        \"line 2\\n\"\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n"
        + dynamic_rules
    )

    context_str = get_directory_contents(target_paths)
    if not context_str:
        print("[!] Warning: No readable files found in the specified paths.")
        context_str = "No files provided."

    full_payload = f"{system_instruction}\n\n=== USER CODEBASE CONTEXT ===\n\n{context_str}"
    
    out_file = "_gemini_web_prompt.txt"
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(full_payload)
        
    return out_file

def main():
    print("\n" + "="*50)
    print("      Gemini Web UI Companion (AEF Bridge)")
    print("="*50)
    
    target_paths = sys.argv[1:] if len(sys.argv) > 1 else ['.']
    prompt_file = generate_context_file(target_paths)
    
    print(f"\n✅ Context successfully bundled into: [bold cyan]{prompt_file}[/bold cyan]")
    print("\n[bold]Next Steps:[/bold]")
    print(f"  1. Drag and drop [cyan]{prompt_file}[/cyan] into the chat at gemini.google.com")
    print("  2. Ask me your coding questions or request changes.")
    print("  3. When I reply with code, paste my response below to apply the diffs.\n")
    print("="*50)

    # Infinite extraction loop
    while True:
        try:
            print("\n📋 [bold yellow]Paste Gemini's response here[/bold yellow].")
            print("   Type [bold green]APPLY[/bold green] on a new line and press Enter when done (or Ctrl+C to exit):")
            
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip().upper() == 'APPLY':
                        break
                    lines.append(line)
                except EOFError:
                    break
                    
            input_text = "\n".join(lines)
            
            if not input_text.strip():
                print("[*] No input provided. Waiting for next paste...")
                continue
                
            print("\n" + "-"*40)
            print("[*] Passing payload to aef_extract...")
            try:
                aef_extract.parse_json_and_write_files(input_text)
            except SystemExit:
                pass # aef_extract calls sys.exit(1) on failure; we catch it to keep the loop alive
            except Exception as e:
                print(f"❌ Exception during extraction: {e}")
            print("-" * 40)
            
        except KeyboardInterrupt:
            print("\n\n[*] Exiting Web UI Companion. Happy coding!")
            break

if __name__ == '__main__':
    main()
