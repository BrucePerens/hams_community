#!/usr/bin/env python3
import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    new_lines = []
    in_view_block = False
    view_start_idx = -1
    has_anchor = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        
        model_match = re.search(r'<record.*?model=["\']ir\.ui\.view["\']', line)
        template_match = re.search(r'<template\b', line)
        
        if model_match or template_match:
            in_view_block = True
            view_start_idx = len(new_lines) - 1
            has_anchor = False
            continue
            
        if in_view_block:
            if 'Verified by [%ANCHOR:' in line or 'Tested by [%ANCHOR:' in line or 'audit-ignore-view' in line:
                has_anchor = True
                
            if re.search(r'</record>', line) or re.search(r'</template>', line):
                if not has_anchor:
                    # Inject the placeholder right after the opening tag
                    inject_line = new_lines[view_start_idx]
                    indent = "    "
                    ws_match = re.match(r'^(\s*)', inject_line)
                    if ws_match:
                        indent = ws_match.group(1) + "    "
                    new_lines.insert(view_start_idx + 1, f"{indent}")
                in_view_block = False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')

def main():
    count = 0
    for root, _, files in os.walk('.'):
        # Skip ignored directories to avoid false positives
        if any(ignored in root.split(os.sep) for ignored in ['.git', 'venv', 'env', 'node_modules', '__pycache__']): 
            continue
        for file in files:
            if file.endswith('.xml'):
                process_file(os.path.join(root, file))
                count += 1
    print(f"✅ Processed {count} XML files. Injected 'pending_tour' anchors into unverified views.")

if __name__ == '__main__':
    main()
