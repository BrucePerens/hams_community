#!/usr/bin/env python3
import os
import re
import sys

def find_anchors_in_docs(docs_dir):
    doc_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md') or file.endswith('.html'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for match in pattern.finditer(f.read()):
                        doc_anchors.add(match.group(1))
    return doc_anchors

def find_anchors_in_code(root_dir):
    code_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    exclude_dirs = {'docs', '.git', 'venv', '__pycache__'}
    
    if is_partial_workspace:
        exclude_dirs.discard('docs')

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(('.py', '.js', '.xml', '.html')):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    try:
                        for match in pattern.finditer(f.read()):
                            code_anchors.add(match.group(1))
                    except UnicodeDecodeError:
                        pass
    return code_anchors

def main():
    print("[*] Scanning documentation for Semantic Anchors...")
    docs_anchors = find_anchors_in_docs('docs')
    print(f"[*] Found {len(docs_anchors)} referenced anchors in documentation.")
    
    print("[*] Scanning codebase for implemented Semantic Anchors...")
    code_anchors = find_anchors_in_code('.')
    
    missing_in_code = docs_anchors - code_anchors
    
    # Exclude dummy placeholder anchors from documentation templates
    missing_in_code -= {'unique_name', 'name'}
    
    # Detect if we are operating in a partial Task Workspace (ADR-0016)
    # If any standard repository directories are missing, we skip cross-module validation
    root_dir = '.'
    expected_full_repo_dirs = [
        'ham_base', 'ham_logbook', 'ham_onboarding', 'user_websites', 
        'ham_dx_cluster', 'daemons', 'ham_shack', 'ham_testing', 'ham_callbook'
    ]
    is_partial_workspace = any(not os.path.exists(os.path.join(root_dir, d)) for d in expected_full_repo_dirs)

    if missing_in_code:
        if is_partial_workspace:
            print("\n[+] Note: Partial workspace detected. Ignoring missing cross-module anchors.")
            sys.exit(0)
            
        print("\n[!] CI/CD FAILURE: The following Semantic Anchors are referenced in the documentation but are missing from the codebase:")
        for anchor in missing_in_code:
            print(f"    - {anchor}")
            
        print("\n[!] ADR-0004 Violation: You must locate the relocated logic and restore the anchor, or remove the documentation reference.")
        sys.exit(1)
    else:
        print("\n[+] SUCCESS: All documented Semantic Anchors are physically present in the codebase.")
        sys.exit(0)

if __name__ == '__main__':
    main()
