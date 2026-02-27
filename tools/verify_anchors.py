#!/usr/bin/env python3
import os
import re
import sys

def find_anchors_in_docs(docs_dir):
    doc_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file == 'LLM_LINTER_GUIDE.md':
                continue
            if file.endswith('.md') or file.endswith('.html'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    for match in pattern.finditer(f.read()):
                        doc_anchors.add(match.group(1))
    return doc_anchors

def find_anchors_in_code_and_manifests(root_dir, is_partial_workspace):
    code_anchors = set()
    anchor_locations = {}
    tests_links = {}
    tests_links_set = set()
    verified_by_links = set()
    
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    exclude_dirs = {'docs', '.git', 'venv', '__pycache__'}
    
    if is_partial_workspace:
        exclude_dirs.discard('docs')
        
    for root, dirs, files in os.walk(root_dir):
        # Allow scanning docs/modules strictly in partial workspaces to ingest manifests
        if is_partial_workspace and root == os.path.join(root_dir, 'docs'):
            dirs[:] = ['modules'] if 'modules' in dirs else []
            continue
            
        if not (is_partial_workspace and 'modules' in root.split(os.sep)):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
        for file in files:
            if file == 'LLM_LINTER_GUIDE.md':
                continue
                
            is_code = file.endswith(('.py', '.js', '.xml', '.html'))
            is_readme = file.lower() == 'readme.md'
            is_module_doc = is_partial_workspace and 'modules' in root.split(os.sep) and file.endswith('.md')
            
            if is_code or is_readme or is_module_doc:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for line_num, line in enumerate(content.splitlines(), 1):
                            for match in pattern.finditer(line):
                                anchor = match.group(1)
                                
                                if 'Tests [%ANCHOR:' in line:
                                    tests_links.setdefault(full_path, []).append(anchor)
                                    tests_links_set.add(anchor)
                                elif 'Verified by [%ANCHOR:' in line or 'Tested by [%ANCHOR:' in line:
                                    verified_by_links.add(anchor)
                                else:
                                    if anchor in anchor_locations and not anchor.startswith('example_') and anchor not in ('unique_name', 'name'):
                                        prev_loc = anchor_locations[anchor].replace('\\', '/')
                                        curr_loc = full_path.replace('\\', '/')
                                        
                                        # ADR-0016: Manifests in docs/modules stand in for missing code in partial workspaces.
                                        # If the real code is also present, it naturally duplicates the manifest. 
                                        # We allow the real code to silently override the manifest.
                                        if 'docs/modules' in prev_loc and 'docs/modules' not in curr_loc:
                                            anchor_locations[anchor] = full_path
                                        elif 'docs/modules' in curr_loc and 'docs/modules' not in prev_loc:
                                            pass
                                        else:
                                            print(f"[!] CI/CD FAILURE: Duplicate Semantic Anchor detected: '{anchor}' in {full_path} and {anchor_locations[anchor]}")
                                            sys.exit(1)
                                    else:
                                        anchor_locations[anchor] = full_path
                                        code_anchors.add(anchor)
                except UnicodeDecodeError:
                    pass
    return code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links

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
    code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links = find_anchors_in_code_and_manifests('.', is_partial_workspace)
    
    missing_tested_anchors = set()
    for file_path, links in tests_links.items():
        for link in links:
            if link not in code_anchors and not link.startswith('example_') and link not in ('unique_name', 'name'):
                missing_tested_anchors.add(link)
                
    if missing_tested_anchors and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Violation. The following anchors are referenced as 'Tests' but do not exist in the codebase:")
        for anchor in missing_tested_anchors:
            print(f"    - `{anchor}`")
        sys.exit(1)

    test_anchors = {a for a in code_anchors if a.startswith('test_')}
    source_anchors = {a for a in code_anchors if not a.startswith('test_') and not a.startswith('example_') and a not in ('unique_name', 'name')}
    
    orphaned_source = source_anchors - tests_links_set
    orphaned_tests = test_anchors - verified_by_links

    if orphaned_source and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. The following source anchors have no corresponding '# Tests [%ANCHOR: ...]' link in the test suite:")
        for a in orphaned_source:
            print(f"    - `{a}`")
        sys.exit(1)

    if orphaned_tests and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. The following test anchors are not cited by any '# Verified by [%ANCHOR: ...]' comment in the source code:")
        for a in orphaned_tests:
            print(f"    - `{a}`")
        sys.exit(1)

    undocumented_source = source_anchors - docs_anchors
    if undocumented_source and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0055 Bidirectional Documentation Violation. The following source anchors are missing from formal documentation (docs/):")
        for a in undocumented_source:
            print(f"    - `{a}`")
        sys.exit(1)

    missing_in_code = docs_anchors - code_anchors
    
    # Exclude placeholder anchors by enforcing an 'example_' prefix convention and legacy exclusions
    missing_in_code = {a for a in missing_in_code if not a.startswith('example_') and a not in ('unique_name', 'name')}

    if missing_in_code:
        print("\n[!] CI/CD FAILURE: The following Semantic Anchors are referenced in the documentation but are missing from the codebase or module READMEs:")
        for anchor in missing_in_code:
            print(f"    - `{anchor}`")
            
        print("\n[!] ADR-0004 Violation: You must locate the relocated logic and restore the anchor, or remove the documentation reference.")
        sys.exit(1)
    else:
        print("\n[+] SUCCESS: All documented Semantic Anchors are physically present in the codebase or accounted for in module manifests.")
        sys.exit(0)

if __name__ == '__main__':
    main()
