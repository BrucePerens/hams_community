#!/usr/bin/env python3
import os
import re
import sys

def find_anchors_in_docs(docs_dir):
    doc_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    for root, _, files in os.walk(docs_dir):
        # Exclude docs/modules from being treated as requirements references; they are manifests
        if 'modules' in root.split(os.sep):
            continue
        for file in files:
            if file.endswith('.md') or file.endswith('.html'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for match in pattern.finditer(f.read()):
                        doc_anchors.add(match.group(1))
    return doc_anchors

def find_anchors_in_code_and_manifests(root_dir, is_partial_workspace):
    code_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    exclude_dirs = {'docs', '.git', 'venv', '__pycache__'}
    
    for root, dirs, files in os.walk(root_dir):
        # Allow scanning docs/modules strictly in partial workspaces to ingest manifests
        if is_partial_workspace and root == os.path.join(root_dir, 'docs'):
            # Traverse ONLY into modules inside docs, skip stories/runbooks/adrs
            dirs[:] = ['modules'] if 'modules' in dirs else []
            continue
            
        if not (is_partial_workspace and 'modules' in root.split(os.sep)):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
        for file in files:
            is_code = file.endswith(('.py', '.js', '.xml', '.html'))
            is_readme = file.lower() == 'readme.md'
            is_module_doc = is_partial_workspace and 'modules' in root.split(os.sep) and file.endswith('.md')
            
            if is_code or is_readme or is_module_doc:
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        for match in pattern.finditer(f.read()):
                            code_anchors.add(match.group(1))
                except UnicodeDecodeError:
                    pass
    return code_anchors

def main():
    print("[*] Scanning documentation for Semantic Anchors...")
    docs_anchors = find_anchors_in_docs('docs')
    print(f"[*] Found {len(docs_anchors)} referenced anchors in documentation.")
    
    root_dir = '.'
    expected_full_repo_dirs = [
        'ham_base', 'ham_logbook', 'ham_onboarding', 'user_websites', 
        'ham_dx_cluster', 'daemons', 'ham_shack', 'ham_testing', 'ham_callbook'
    ]
    is_partial_workspace = any(not os.path.exists(os.path.join(root_dir, d)) for d in expected_full_repo_dirs)

    print(f"[*] Scanning codebase (Partial Workspace: {is_partial_workspace}) for implemented Semantic Anchors...")
    code_anchors = find_anchors_in_code_and_manifests('.', is_partial_workspace)
    
    missing_in_code = docs_anchors - code_anchors
    
    # Exclude placeholder anchors by enforcing an 'example_' prefix convention
    missing_in_code = {a for a in missing_in_code if not a.startswith('example_')}

    if missing_in_code:
        print("\n[!] CI/CD FAILURE: The following Semantic Anchors are referenced in the documentation but are missing from the codebase or module READMEs:")
        for anchor in missing_in_code:
            print(f"    - {anchor}")
            
        print("\n[!] ADR-0004 Violation: You must locate the relocated logic and restore the anchor, or remove the documentation reference.")
        sys.exit(1)
    else:
        print("\n[+] SUCCESS: All documented Semantic Anchors are physically present in the codebase or accounted for in module manifests.")
        sys.exit(0)

if __name__ == '__main__':
    main()
