#!/usr/bin/env python3
import os
import re
import sys

def find_anchors_in_docs(docs_dir):
    doc_anchors = set()
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file == 'LLM_LINTER_GUIDE.md': continue
            if file.endswith('.md') or file.endswith('.html'):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    doc_anchors.update(match.group(1) for match in pattern.finditer(f.read()))
    return doc_anchors

def _process_file_for_anchors(full_path, content, pattern, code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links, cross_references, duplicates):
    for line in content.splitlines():
        for match in pattern.finditer(line):
            anchor = match.group(1)
            prefix = line[:match.start()].strip()
            if prefix.endswith('Tests'):
                tests_links.setdefault(full_path, []).append(anchor)
                tests_links_set.add(anchor)
            elif prefix.endswith('Verified by') or prefix.endswith('Tested by'):
                verified_by_links.add(anchor)
            elif prefix.endswith('Triggers') or prefix.endswith('Triggered by'):
                cross_references.add(anchor)
            else:
                if anchor in anchor_locations and not anchor.startswith('example_') and anchor not in ('unique_name', 'name'):
                    prev_loc = anchor_locations[anchor].replace('\\', '/')
                    curr_loc = full_path.replace('\\', '/')
                    if 'docs/modules' in prev_loc and 'docs/modules' not in curr_loc: anchor_locations[anchor] = full_path
                    elif 'docs/modules' in curr_loc and 'docs/modules' not in prev_loc: pass
                    else: duplicates.append(f"'{anchor}' in {full_path} and {anchor_locations[anchor]}")
                else:
                    anchor_locations[anchor] = full_path
                    code_anchors.add(anchor)

def find_anchors_in_code_and_manifests(root_dir, is_partial_workspace):
    code_anchors, anchor_locations = set(), {}
    tests_links, tests_links_set = {}, set()
    verified_by_links, cross_references = set(), set()
    duplicates = []
    pattern = re.compile(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]')
    exclude_dirs = {'docs', '.git', 'venv', '__pycache__'}
    if is_partial_workspace: exclude_dirs.discard('docs')
        
    for root, dirs, files in os.walk(root_dir):
        if is_partial_workspace and root == os.path.join(root_dir, 'docs'):
            dirs[:] = ['modules'] if 'modules' in dirs else []
            continue
        if not (is_partial_workspace and 'modules' in root.split(os.sep)):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
        for file in files:
            if file == 'LLM_LINTER_GUIDE.md': continue
            is_code = file.endswith(('.py', '.js', '.xml', '.html'))
            is_readme = file.lower() == 'readme.md'
            is_module_doc = is_partial_workspace and 'modules' in root.split(os.sep) and file.endswith('.md')
            if is_code or is_readme or is_module_doc:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        _process_file_for_anchors(full_path, f.read(), pattern, code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links, cross_references, duplicates)
                except UnicodeDecodeError:
                    pass
    return code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links, cross_references, duplicates

def _report_duplicates(duplicates):
    if duplicates:
        print("\n[!] CI/CD FAILURE: Duplicate Semantic Anchors detected:")
        for dup in duplicates:
            print(f"    - {dup}")
        return True
    return False

def _report_missing_cross_refs(cross_references, code_anchors, is_partial_workspace):
    missing_cross_refs = set()
    for anchor in (cross_references - code_anchors):
        if not anchor.startswith('example_') and anchor not in ('unique_name', 'name'):
            missing_cross_refs.add(anchor)
            
    if missing_cross_refs and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0055 Cross-Reference Violation. The following anchors are referenced via 'Triggers' or 'Triggered by' but do not exist in the codebase:")
        for anchor in missing_cross_refs:
            print(f"    - `{anchor}`")
        return True
    return False

def _report_missing_tests(tests_links, code_anchors, is_partial_workspace):
    missing_tested = set()
    for links in tests_links.values():
        for link in links:
            if link not in code_anchors and not link.startswith('example_') and link not in ('unique_name', 'name'):
                missing_tested.add(link)
                
    if missing_tested and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Violation. The following anchors are referenced as 'Tests' but do not exist in the codebase:")
        for anchor in missing_tested:
            print(f"    - `{anchor}`")
        return True
    return False

def _report_bidirectional_orphans(code_anchors, tests_links_set, verified_by_links, is_partial_workspace):
    test_anchors = {a for a in code_anchors if a.startswith('test_')}
    source_anchors = {a for a in code_anchors if not a.startswith('test_') and not a.startswith('example_') and a not in ('unique_name', 'name')}
    orphaned_source = source_anchors - tests_links_set
    orphaned_tests = test_anchors - verified_by_links
    has_errors = False
    if orphaned_source and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. Source anchors missing corresponding '# Tests [%ANCHOR: ...]' link:")
        for anchor in orphaned_source:
            print(f"    - `{anchor}`")
        has_errors = True
    if orphaned_tests and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0054 Bidirectional Violation. Test anchors not cited by '# Verified by [%ANCHOR: ...]':")
        for anchor in orphaned_tests:
            print(f"    - `{anchor}`")
        has_errors = True
    return has_errors, source_anchors

def _report_documentation_gaps(source_anchors, docs_anchors, code_anchors, is_partial_workspace):
    undocumented = source_anchors - docs_anchors
    missing_in_code = {a for a in (docs_anchors - code_anchors) if not a.startswith('example_') and a not in ('unique_name', 'name')}
    has_errors = False
    if undocumented and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: ADR-0055 Bidirectional Documentation Violation. Source anchors missing from formal docs (docs/):")
        for anchor in undocumented:
            print(f"    - `{anchor}`")
        has_errors = True
    if missing_in_code and not is_partial_workspace:
        print("\n[!] CI/CD FAILURE: Documentation references anchors missing from the codebase:")
        for anchor in missing_in_code:
            print(f"    - `{anchor}`")
        has_errors = True
    return has_errors

def main():
    print("[*] Scanning documentation and codebase for Semantic Anchors...")
    docs_anchors = find_anchors_in_docs('docs')
    
    # If ham_base is missing, we are in the hams_community isolated repository
    is_partial_workspace = not os.path.exists('ham_base')

    code_anchors, anchor_locations, tests_links, tests_links_set, verified_by_links, cross_references, duplicates = find_anchors_in_code_and_manifests('.', is_partial_workspace)
    
    errs = [_report_duplicates(duplicates), _report_missing_cross_refs(cross_references, code_anchors, is_partial_workspace), _report_missing_tests(tests_links, code_anchors, is_partial_workspace)]
    
    bidi_err, source_anchors = _report_bidirectional_orphans(code_anchors, tests_links_set, verified_by_links, is_partial_workspace)
    errs.append(bidi_err)
    errs.append(_report_documentation_gaps(source_anchors, docs_anchors, code_anchors, is_partial_workspace))

    if any(errs):
        sys.exit(1)
    else:
        print(f"\n[+] SUCCESS: Verified {len(code_anchors)} Semantic Anchors across the codebase and documentation boundaries.")
        sys.exit(0)

if __name__ == '__main__':
    main()
