#!/usr/bin/env bash
"":"
# --- Bash Execution Environment ---
if [ ! -d ".venv" ]; then
    echo "[*] Setting up Python virtual environment in .venv..."
    python3 -m venv .venv
fi

# Ensure required packages are installed
.venv/bin/pip install -q google-genai rich

if [ -z "$GEMINI_API_KEY" ]; then
    echo "[!] Error: GEMINI_API_KEY environment variable is not set."
    exit 1
fi

exec .venv/bin/python "$0" "$@"
"""

# --- Python Execution Environment ---
import os
import re
import sys
import json
import tempfile
import signal
from google import genai
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

# Global state
REQUIRE_APPROVAL = True
MARKDOWN_CODE_THEME = "tango" # Accessible for red-green color blindness
IS_STREAMING = False          # Tracks if we are currently rendering Markdown
CURRENT_MODEL = "gemini-3-pro-preview"

# --- Terminal Signal Handling for Clean Suspension ---
def handle_sigtstp(signum, frame):
    """Fired when user hits Ctrl+Z. Restores cursor, then suspends."""
    # Force the cursor to become visible
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    # Temporarily restore the default stop behavior
    signal.signal(signal.SIGTSTP, signal.SIG_DFL)
    # Send the stop signal to ourselves to actually pause the process
    os.kill(os.getpid(), signal.SIGTSTP)

def handle_sigcont(signum, frame):
    """Fired when user types 'fg'. Hides cursor again if we were rendering."""
    # Re-arm the custom Ctrl+Z interceptor
    signal.signal(signal.SIGTSTP, handle_sigtstp)
    # If we paused mid-stream, hide the cursor so rich can resume rendering cleanly
    if IS_STREAMING:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

# Register the signals (if the OS supports them, i.e., Unix/Linux/macOS)
if hasattr(signal, 'SIGTSTP') and hasattr(signal, 'SIGCONT'):
    signal.signal(signal.SIGTSTP, handle_sigtstp)
    signal.signal(signal.SIGCONT, handle_sigcont)


def flush_input():
    """Flushes the terminal input buffer to discard unread keystrokes."""
    try:
        # Windows
        import msvcrt
        count = 0
        # Limit to 1000 keystrokes to completely prevent any risk of infinite loop hangs
        while msvcrt.kbhit() and count < 1000:
            msvcrt.getch()
            count += 1
    except ImportError:
        # Unix/Linux/macOS
        try:
            import termios
            # Crucial fix: tcflush requires the integer file descriptor, not the IO object
            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except Exception:
            pass # Failsafe fallback

def is_hidden(filename):
    """Checks if a file or directory name starts with a dot."""
    return filename.startswith('.')

def is_binary(filepath):
    """Simple heuristic to detect binary files."""
    try:
        with open(filepath, 'tr') as check_file:
            check_file.read(1024)
            return False
    except UnicodeDecodeError:
        return True

def get_directory_contents():
    """Reads files, skipping hidden files, heavy directories, and massive files."""
    contents = []
    exclude_dirs = {'__pycache__', 'node_modules', 'build', 'dist', 'target', 'venv', 'env'}
    max_file_size = 100 * 1024 
    
    for root, dirs, files in os.walk('.'):
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

def upload_directory_context(client):
    """Bundles the directory into a single text file and uploads it via the Files API."""
    context_str = get_directory_contents()
    if not context_str:
        return None

    # Create a temporary file to hold the concatenated codebase
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
        temp_file.write(context_str)
        temp_path = temp_file.name
        
    try:
        print("[*] Uploading bundled directory context to Google servers...")
        uploaded_file = client.files.upload(file=temp_path, config={'display_name': 'Directory Context'})
        return uploaded_file
    finally:
        # Always clean up the local temp file
        os.remove(temp_path)

def print_help():
    print("\n" + "="*40)
    print("       Gemini Interactive Runner")
    print("="*40)
    print("/?             : Print these instructions")
    print("/model         : List available models")
    print("/model <name>  : Switch the Gemini model")
    print("/send <file>   : Upload a specific file to Gemini via the Files API")
    print("/auto          : Toggle automatic file writing (skip approval)")
    print("/quit or /exit : Exit the program")
    print("Anything else  : Sent directly to Gemini as a prompt")
    print("="*40 + "\n")

def process_response(text):
    """Extracts AEF 4.0 JSON blocks from the full response and prompts to write."""
    global REQUIRE_APPROVAL
    pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.finditer(pattern, text, flags=re.DOTALL)
    
    for match in matches:
        json_str = match.group(1)
        try:
            payload = json.loads(json_str)
            if payload.get("aef_version") in ("3.0", "4.0") and "files" in payload:
                for file_data in payload["files"]:
                    filename = file_data.get("path", "").strip()
                    encoding = file_data.get("encoding", "utf-8")
                    content_raw = file_data.get("content", [])
                    
                    if not filename:
                        continue
                    
                    if encoding == "base64":
                        print(f"\n[!] ERROR: LLM attempted to generate Base64 for {filename}. This violates the mandate.")
                        continue
                    
                    if isinstance(content_raw, list):
                        content = "".join(content_raw)
                    else:
                        content = content_raw

                    print(f"\n[!] Gemini wants to write: {filename}")
                    
                    if REQUIRE_APPROVAL:
                        flush_input()
                        ans = input(f"    Save this file? (y/n): ").strip().lower()
                    else:
                        print(f"    Auto-saving enabled. Writing automatically...")
                        ans = 'y'

                    if ans == 'y':
                        try:
                            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"[*] Wrote {filename}")
                        except Exception as e:
                            print(f"[!] Error writing {filename}: {e}")
                    else:
                        print(f"[*] Skipped writing {filename}")
        except json.JSONDecodeError:
            continue # Skip invalid JSON blocks

def stream_and_parse(chat, prompt):
    """Streams thoughts and renders markdown in real-time."""
    global IS_STREAMING
    
    full_response = ""
    visible_response = ""
    in_thought_block = False
    response_started = False
    
    console = Console()
    live = None
    IS_STREAMING = True
    
    def update_display(new_text):
        nonlocal visible_response
        visible_response += new_text
        if live:
            live.update(Markdown(visible_response, code_theme=MARKDOWN_CODE_THEME), refresh=True)

    try:
        for chunk in chat.send_message_stream(prompt):
            parts = []
            if getattr(chunk, 'candidates', None) and chunk.candidates and chunk.candidates[0].content and getattr(chunk.candidates[0].content, 'parts', None):
                parts = chunk.candidates[0].content.parts
            else:
                if chunk.text:
                    class MockPart:
                        def __init__(self, t):
                            self.text = t
                            self.thought = False
                    parts = [MockPart(chunk.text)]

            for part in parts:
                is_thought = getattr(part, 'thought', False)
                if is_thought:
                    if not in_thought_block:
                        print("\n\033[90m[Gemini is thinking...]\n", end="")
                        in_thought_block = True
                    if part.text:
                        print(part.text, end="", flush=True)
                else:
                    if not response_started:
                        if in_thought_block:
                            print("\033[0m", end="", flush=True)
                            in_thought_block = False
                        print("\nGemini>\n", flush=True)
                        response_started = True
                        
                    if not live:
                        live = Live(Markdown(visible_response, code_theme=MARKDOWN_CODE_THEME), console=console, refresh_per_second=15, transient=False)
                        live.start()

                    text_to_process = part.text if part.text else ""
                    update_display(text_to_process)
                    full_response += text_to_process

        if in_thought_block:
            print("\033[0m", end="", flush=True)
            
    finally:
        # Stop tracking the stream for signal handlers
        IS_STREAMING = False
        # Ensures the display thread dies even if an API interruption occurs mid-stream
        if live:
            live.stop()
            
    print() 
    return full_response

def main():
    global REQUIRE_APPROVAL, CURRENT_MODEL
    print("[*] Initializing Gemini API...")
    client = genai.Client() 
    
    system_instruction = (
        "You are an expert developer. When generating or modifying code, you MUST output your response using the AEF 4.0 JSON schema inside a single ```json code block.\n"
        "CRITICAL AEF 4.0 ASYMMETRIC TRANSPORT MANDATE: You MUST NEVER output Base64. Your generated `content` field MUST be an array of plain text strings (one string per line, ending with '\n'). You MUST specify `\"encoding\": \"utf-8\"`.\n"
        "JSON SAFETY & SELECTIVE URL-ENCODING: To prevent JSON syntax errors from unescaped quotes or backslashes, you MUST use `\"encoding\": \"url-encoded\"` and selectively percent-encode ONLY `\"` (to `%22`), `\\` (to `%5C`), `<` (to `%3C`), `>` (to `%3E`), and `&` (to `%26`). Do NOT globally encode spaces or newlines.\n"
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
        "```"
    )
    
    print("[*] Bundling directory (skipping hidden/heavy files)...")
    uploaded_context = upload_directory_context(client)
    
    chat = client.chats.create(
        model=CURRENT_MODEL, 
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            thinking_config=types.ThinkingConfig(include_thoughts=True)
        )
    )
    
    try:
        if uploaded_context:
            print("[*] Processing directory context with Gemini...")
            # We pass a list containing the text prompt and the uploaded File object
            chat.send_message(["Here is the context of the current directory. It contains multiple files concatenated with delimiters.", uploaded_context])
        else:
            chat.send_message("Directory is empty.")
            
        print("[*] Context established. Ready for prompts.")
        print_help()
    except Exception as e:
        print(f"[!] Initialization failed: {e}")
        return

    while True:
        try:
            flush_input()
            user_input = input("\nYou> ").strip()
            if not user_input: continue
            
            if user_input.startswith('/'):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                
                if cmd == '/?':
                    print_help()
                elif cmd in ('/quit', '/exit'):
                    break
                elif cmd == '/auto':
                    REQUIRE_APPROVAL = not REQUIRE_APPROVAL
                    status = "OFF" if REQUIRE_APPROVAL else "ON"
                    print(f"[*] Auto-write is now {status} (Approval required: {REQUIRE_APPROVAL})")
                elif cmd == '/model':
                    if len(parts) < 2:
                        print(f"[*] Current model: {CURRENT_MODEL}")
                        print("[*] Fetching available models...")
                        try:
                            for m in client.models.list():
                                # Strip 'models/' prefix for a cleaner display
                                clean_name = m.name.replace('models/', '')
                                print(f"  - {clean_name}")
                            print("\nUsage to switch: /model <model_name>")
                        except Exception as e:
                            print(f"[!] Error fetching models: {e}")
                        continue
                        
                    CURRENT_MODEL = parts[1]
                    print(f"[*] Switching model to {CURRENT_MODEL}...")
                    
                    try:
                        chat = client.chats.create(
                            model=CURRENT_MODEL, 
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.2,
                                thinking_config=types.ThinkingConfig(include_thoughts=True)
                            ),
                            history=chat.get_history()
                        )
                        print(f"[*] Successfully switched to {CURRENT_MODEL}. History preserved.")
                    except Exception as e:
                        print(f"[!] Failed to switch model: {e}")
                elif cmd == '/send':
                    if len(parts) < 2:
                        print("Usage: /send <filename>")
                        continue
                        
                    target_file = parts[1]
                    target_basename = os.path.basename(target_file)
                    
                    if is_hidden(target_basename):
                        print(f"[!] Blocked: Cannot send hidden file '{target_file}'.")
                        continue
                        
                    if not os.path.isfile(target_file):
                        print(f"[!] Error: '{target_file}' is not a valid file.")
                        continue
                        
                    try:
                        print(f"[*] Uploading {target_file} to Google servers...")
                        uploaded_file = client.files.upload(file=target_file)
                        print(f"[*] File uploaded successfully. Asking Gemini...")
                        
                        # Pass the uploaded File object alongside the prompt
                        full_response = stream_and_parse(chat, [f"User sent a new version of or a new file: {target_file}", uploaded_file])
                        process_response(full_response)
                        
                    except Exception as e:
                        print(f"\n[!] Error uploading or sending file: {e}")
                else:
                    print(f"Unknown command: {cmd}")
            else:
                try:
                    full_response = stream_and_parse(chat, user_input)
                    process_response(full_response)
                except Exception as e:
                    print(f"\n[!] Communication error: {e}")
                
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == '__main__':
    main()
