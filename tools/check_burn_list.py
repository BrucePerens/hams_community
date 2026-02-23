#!/usr/bin/env python3
"""
Odoo 19+ Burn List Linter
-------------------------
Scans the repository for deprecated Odoo syntax, legacy XML tags, and 
architectural traps defined in LLM_ODOO_REQUIREMENTS.md.

Usage:
    python3 check_burn_list.py [directory_to_scan]
"""

import os
import re
import sys
import ast
import argparse

# ERROR RULES: Will cause the linter to fail (Exit Code 1)
ERROR_RULES = [
    # --- Python & ORM Traps ---
    (r'\.py$', re.compile(r'\bnumbercall\b'), "Remove 'numbercall'. Odoo 18+ crons run indefinitely if active='True'."),
    (r'\.py$', re.compile(r'\b_sql_constraints\b'), "Use 'models.Constraint' instead of '_sql_constraints'."),
    (r'\.py$', re.compile(r'self\._context\b'), "Use 'self.env.context' instead of 'self._context'."),
    (r'\.py$', re.compile(r'self\._uid\b'), "Use 'self.env.uid' instead of 'self._uid'."),
    (r'\.py$', re.compile(r'@api\.returns'), "@api.returns is deprecated. Remove it."),
    (r'\.py$', re.compile(r"type\s*=\s*['\"]json['\"]"), "Use type='jsonrpc' instead of type='json' for HTTP routes."),
    (r'\.py$', re.compile(r'\b_sign_token\s*\('), "Verify '_sign_token' is not called on models lacking an 'access_token' field (e.g., res.users). Use stateless HMAC instead."),
    (r'\.py$', re.compile(r'\bclear_caches\s*\('), "ORM cache invalidation in Odoo 19+ MUST use `self.env.registry.clear_cache()`."),
    (r'\.py$', re.compile(r'(?<!registry)\.clear_cache\s*\('), "ORM cache invalidation in Odoo 19+ MUST use `self.env.registry.clear_cache()` instead of calling `.clear_cache()` on methods or models."),
    (r'\.py$', re.compile(r'\bself\.(?:sudo\(\)\.)?(?:search|create|browse)\s*\('), "Ambiguous ORM call: Use `self.env['your.model'].search/create/browse()` instead of `self.search/create/browse()` for clarity and to avoid unintended scope."),
    (r'\.py$', re.compile(r'self\.env\.context\s*=[^=]'), "Never modify `self.env.context` directly. Use the non-mutating `self.with_context(...)` method instead."),
    (r'\.py$', re.compile(r'\b_check_recursion\s*\('), "Odoo 18+ Hierarchy: Use '_has_cycle()' instead of the deprecated '_check_recursion()'. Note: '_has_cycle()' evaluates to True if a cycle exists, which is the reverse of '_check_recursion()'."),
    (r'\.py$', re.compile(r"(?:group|groups|_group_id)\.users\b|related\s*=\s*['\"][^'\"]*\.users['\"]"), "Legacy security relation: Use 'user_ids' instead of 'users' when referencing members of res.groups in Python."),
    (r'\.py$', re.compile(r"index\s*=\s*['\"]trgm['\"]"), "Invalid Index Type: Use index='trigram' instead of index='trgm' for PostgreSQL pg_trgm extensions in Odoo 19+."),
    (r'\.py$', re.compile(r'\.send_mail\s*\('), "Mail Templates: Verify that the model_id of the XML template exactly matches the model of the record ID passed to send_mail()."),
    (r'\.py$', re.compile(r"(?:env\['\"].*\.\['\"].*\]|\.user_id|self\.env\.user)\.(?:message_post|message_subscribe)\s*\("), "Messaging & Followers: Do not call message_post() or message_subscribe() directly on res.users. (Must be called on the underlying user.partner_id)."),
    
    # --- Critical Security Traps ---
    (r'\.py$', re.compile(r'\.sudo\(\)'), "CRITICAL PRIVILEGE ESCALATION: The use of `.sudo()` is strictly forbidden for ORM operations. Use the Service Account Pattern (`with_user`), Public User ACLs, or add `# burn-ignore` if this is a secure cryptographic system parameter fetch."),
    
    # NOTE: SQL Injection checks for cr.execute are now primarily handled by the AST visitor for deeper taint analysis.
    (r'\.xml$', re.compile(r'\bt-raw\s*='), "CRITICAL XSS: 't-raw' is deprecated and dangerous. Use 't-out' and Python's markupsafe.Markup() for safe HTML."),
    (r'\.py$', re.compile(r'\beval\s*\('), "CRITICAL RCE: Never use native eval(). Use ast.literal_eval() for data structures or odoo.tools.safe_eval() for domains/contexts."),
    (r'\.py$', re.compile(r'\bexec\s*\('), "CRITICAL RCE: The use of exec() is strictly forbidden."),
    (r'\.py$', re.compile(r'\bimport pickle\b|\bpickle\.(loads|dumps)\b'), "CRITICAL RCE: The pickle module is vulnerable to arbitrary code execution. Use the json module instead."),
    (r'\.py$', re.compile(r'csrf\s*=\s*(?:False|not\s+True|0)'), "SECURITY ALERT: csrf=False found. Ensure this route uses strict HMAC/API key auth, otherwise it is vulnerable to CSRF."),
    (r'\.py$', re.compile(r'\bhashlib\.(md5|sha1)\s*\('), "WEAK CRYPTO: MD5 and SHA1 are cryptographically broken. Use hashlib.sha256() or higher."),
    (r'\.py$', re.compile(r'import random\b|\brandom\.(choice|randint|random)\b'), "WEAK CRYPTO: Do not use 'random' for security tokens or passwords. Use the 'secrets' module."),
    (r'\.py$', re.compile(r'shell\s*=\s*True'), "CRITICAL SHELL INJECTION: Avoid subprocess with shell=True. Pass arguments as a list with shell=False."),
    (r'\.js$', re.compile(r'\.bindPopup\(\s*`|\.innerHTML\s*=\s*`'), "JS DOM XSS: Template literal passed to bindPopup or innerHTML. Ensure all variables within the literal are sanitized using an escapeHTML function."),

    # --- XML & QWeb Traps ---
    (r'\.xml$', re.compile(r'<tree\b'), "Legacy view tag: Use <list> instead of <tree>."),
    (r'\.xml$', re.compile(r't-name\s*=\s*["\']kanban-box["\']'), "Legacy view tag: Use <t t-name='card'> instead of kanban-box."),
    (r'\.xml$', re.compile(r'\bt-esc\s*='), "Deprecated directive: Use t-out instead of t-esc."),
    (r'\.xml$', re.compile(r'expand\s*=\s*["\']0["\']'), "Legacy search view: Remove expand='0' from <group> tags."),
    (r'\.xml$', re.compile(r'<group[^>]*\bstring\s*=\s*["\'][^"\']*["\']'), "Legacy search view: Remove string='...' from <group> tags."),
    (r'\.xml$', re.compile(r'name\s*=\s*["\']category_id["\']'), "Legacy security: Use 'privilege_id' instead of 'category_id' for res.groups."),
    (r'\.xml$', re.compile(r'<field[^>]+name\s*=\s*["\']users["\']'), "🚨 CRITICAL BIAS TRAP: Legacy security mapping detected. You MUST use name='user_ids' instead of 'users' for res.groups mapping in Odoo 18+."),
    
    # --- Frontend JS Traps ---
    (r'\.js$', re.compile(r'\$\('), "jQuery ($) is forbidden. Use Vanilla JS or modern OWL components."),
    (r'\.js$', re.compile(r'useService\s*\(\s*["\']company["\']\s*\)'), "useService('company') is deprecated in modern Odoo frontends.")
]

# WARNING RULES: Will flag for manual review but won't halt the build (Exit Code 0)
WARNING_RULES = [
    (r'\.py$', re.compile(r"env\['\"][^'\"]+['\"]\]\.(?:search|search_count)\s*\("), "[AUDIT] Data Integrity: Direct `search()` on an env model without `.sudo()` may cause false negatives if used for uniqueness checks. Review manually."),
    (r'\.py$', re.compile(r'\.(?:create|write)\(\s*(?:kwargs|kw|post)\s*\)'), "[AUDIT] RPC MASS ASSIGNMENT: Never pass raw request payloads directly to create/write. Verify fields are extracted securely."),
    (r'\.py$', re.compile(r'def\s+action_[a-zA-Z0-9_]+\s*\('), "[AUDIT] ACTION METHOD RPC: Public action methods are exposed to XML-RPC. Verify `self.env.user` owns the record before escalating privileges."),
    (r'\.py$', re.compile(r'\.message_post\('), "[AUDIT] CHATTER XSS: Ensure any user input passed into message_post() body is strictly escaped using html.escape()."),
    (r'\.xml$', re.compile(r'<record.*?model=["\']ir\.cron["\']'), "[AUDIT] CRON ARCHITECTURE: Ensure the Python method implements stateless batching via _trigger() to prevent transaction timeouts."),
]

# MULTILINE AUDIT RULES: Checked against the entire file content
MULTILINE_WARNING_RULES = [
    (r'\.py$', re.compile(r"^\s*def\s+(?!_)[a-zA-Z0-9_]+\s*\(.*\):(?:.*\n)+?\s*(?:self\.env\[.+?\]\.create|self\.env\['bus\.bus'\]\._sendone).*", re.MULTILINE), "[AUDIT] RPC ORM BYPASS: A public @api.model method appears to be modifying external state. Verify manual access controls."),
]

# Centralized whitelist for known false-positives
EXEMPTIONS = {
    "security_utils.py": [
        r'\.sudo\(\)\._xmlid_to_res_id\s*\(',
        r'\.sudo\(\)\.get_param\s*\('
    ],
    "api.py": [
        r'csrf\s*=\s*(?:False|not\s+True|0)'
    ]
}

def check_ast_vulnerabilities(filepath, content, lines):
    """Parses the AST to detect variable taint mapping for SQL injection."""
    errors = []
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError:
        return errors # Handled by the standard execution pipeline
        
    class TaintVisitor(ast.NodeVisitor):
        def __init__(self):
            self.violations = []
            self.assignments = {}

        def visit_FunctionDef(self, node):
            old_assignments = self.assignments.copy()
            self.assignments = {}
            self.generic_visit(node)
            self.assignments = old_assignments

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assignments[target.id] = node.value
            self.generic_visit(node)

        def visit_Call(self, node):
            is_cr_execute = False
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'cr':
                    is_cr_execute = True
                elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'cr':
                    is_cr_execute = True

            if is_cr_execute and node.args:
                # Respect inline burn-ignore overrides
                if node.lineno <= len(lines) and 'burn-ignore' in lines[node.lineno - 1]:
                    pass
                else:
                    arg = node.args[0]
                    if isinstance(arg, ast.JoinedStr):
                        self.violations.append((node.lineno, "CRITICAL SQLi: Direct f-string used in cr.execute(). Use parametrized queries."))
                    elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                        self.violations.append((node.lineno, "CRITICAL SQLi: String interpolation (%) used in cr.execute(). Use parametrized queries."))
                    elif isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute) and arg.func.attr == 'format':
                        self.violations.append((node.lineno, "CRITICAL SQLi: .format() used in cr.execute(). Use parametrized queries."))
                    elif isinstance(arg, ast.Name):
                        var_name = arg.id
                        if var_name in self.assignments:
                            val = self.assignments[var_name]
                            if isinstance(val, ast.JoinedStr):
                                self.violations.append((node.lineno, f"CRITICAL SQLi: Variable '{var_name}' assigned via f-string passed to cr.execute(). Use parametrized queries."))
                            elif isinstance(val, ast.BinOp) and isinstance(val.op, ast.Mod):
                                self.violations.append((node.lineno, f"CRITICAL SQLi: Variable '{var_name}' assigned via % interpolation passed to cr.execute(). Use parametrized queries."))
                            elif isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) and val.func.attr == 'format':
                                self.violations.append((node.lineno, f"CRITICAL SQLi: Variable '{var_name}' assigned via .format() passed to cr.execute(). Use parametrized queries."))
            self.generic_visit(node)

    visitor = TaintVisitor()
    visitor.visit(tree)
    return visitor.violations

def scan_file(filepath):
    """Scans a single file against applicable rules, tracking XML context."""
    errors_found = []
    warnings_found = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        return [f"Could not read file: {e}"], []

    filename = os.path.basename(filepath)
    
    # 1. Multiline Regex Checks (Warnings)
    for ext_pattern, regex, warning_msg in MULTILINE_WARNING_RULES:
        if re.search(ext_pattern, filename):
            if 'test_' in filename and 'RPC ORM BYPASS' in warning_msg:
                continue
            if regex.search(content):
                warnings_found.append(f"Global Match: {warning_msg}")

    # 2. Advanced AST Analysis for Python Files
    if filename.endswith('.py'):
        ast_errors = check_ast_vulnerabilities(filepath, content, lines)
        for lineno, msg in ast_errors:
            stripped = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            errors_found.append(f"Line {lineno} (AST): {msg}\n    {stripped}")

    current_xml_model = None
    current_xml_view_type = None
    skip_next_line = False

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip full-line comments entirely to avoid false positives
        if filename.endswith('.py') and stripped.startswith('#'):
            continue
        if filename.endswith('.js') and stripped.startswith('//'):
            continue
        
        # Skip HTML comments (Ensure AEF transport uses url-encoded to prevent UI crashes)
        if filename.endswith('.xml') and stripped.startswith('<!--'):
            continue

        # Handle 'burn-ignore' logic
        if skip_next_line:
            skip_next_line = False
            # Maintain XML context tracking even if we skip the rules
            if filename.endswith('.xml'):
                model_match = re.search(r'<record.*?model=["\']([^">]+)["\']', line)
                if model_match:
                    current_xml_model = model_match.group(1)
            continue

        if 'burn-ignore' in line:
            # Check for authorized usages of burn-ignore to prevent LLM abuse
            if not ('database.secret' in line):
                errors_found.append(f"Line {line_num}: UNAUTHORIZED BYPASS. '# burn-ignore' was used on an unauthorized line to bypass linter rules. Fix the underlying code instead.\n    {stripped}")
            continue

        # Track active XML record model and view structure
        if filename.endswith('.xml'):
            model_match = re.search(r'<record.*?model=["\']([^">]+)["\']', line)
            if model_match:
                current_xml_model = model_match.group(1)
            elif '<search' in line:
                current_xml_view_type = 'search'
            elif '<form' in line:
                current_xml_view_type = 'form'
            elif '<list' in line:
                current_xml_view_type = 'list'
            elif '</record>' in line:
                current_xml_model = None
                current_xml_view_type = None

        # Evaluate against Error Rules
        for ext_pattern, regex, error_msg in ERROR_RULES:
            if re.search(ext_pattern, filename):
                # Context-Aware Exemptions (XML internal tags)
                if current_xml_model != 'res.groups' and ('category_id' in regex.pattern or 'users' in regex.pattern):
                    continue
                if 'Legacy search view' in error_msg and current_xml_view_type != 'search':
                    continue
                
                if regex.search(line):
                    exempted = False
                    if filename in EXEMPTIONS:
                        for ex_pat in EXEMPTIONS[filename]:
                            if re.search(ex_pat, line):
                                exempted = True
                                break
                    if exempted:
                        continue
                    errors_found.append(f"Line {line_num}: {error_msg}\n    {stripped}")
                    
        # Evaluate against Warning Rules
        for ext_pattern, regex, warning_msg in WARNING_RULES:
            if re.search(ext_pattern, filename):
                if current_xml_model != 'res.groups' and ('category_id' in regex.pattern or 'users' in regex.pattern):
                    continue
                
                if regex.search(line):
                    exempted = False
                    if filename in EXEMPTIONS:
                        for ex_pat in EXEMPTIONS[filename]:
                            if re.search(ex_pat, line):
                                exempted = True
                                break
                    if exempted:
                        continue
                    warnings_found.append(f"Line {line_num}: {warning_msg}\n    {stripped}")
                    
    return errors_found, warnings_found

def main():
    parser = argparse.ArgumentParser(description="Scan Odoo modules for Odoo 19+ deprecated syntax.")
    parser.add_argument("directory", nargs='?', default=".", help="Directory to scan (default: current)")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.directory)
    print(f"\nScanning {target_dir} for Odoo 19+ Burn List violations...\n")

    total_errors = 0
    total_warnings = 0
    scanned_files = 0
    this_script_name = os.path.basename(__file__)

    # Walk directory, explicitly ignoring hidden directories and cache
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules')]
        
        for file in files:
            if file == this_script_name:
                continue
            
            if file.endswith('.py') or file.endswith('.xml') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                scanned_files += 1
            
                errors, warnings = scan_file(filepath)
                
                if errors or warnings:
                    rel_path = os.path.relpath(filepath, target_dir)
                    print(f"\n📄 {rel_path}")
                    
                    if warnings:
                        total_warnings += len(warnings)
                        for warn in warnings:
                            print(f"  ⚠️  WARNING: {warn}")
                            
                    if errors:
                        total_errors += len(errors)
                        for err in errors:
                            print(f"  ❌ ERROR: {err}")

    print(f"\nScan Complete: Checked {scanned_files} files.")
    print(f"Total Errors: {total_errors} | Total Warnings (Audits): {total_warnings}")
    
    if total_errors > 0:
        print("\n❌ Found Burn List errors. Please fix them before deploying.")
        sys.exit(1)
    else:
        if total_warnings > 0:
            print("\n✅ Passed with warnings. Audits require manual verification, but the build will continue.")
        else:
            print("\n✅ No Burn List violations found! Your codebase is clean.")
        sys.exit(0)

if __name__ == '__main__':
    main()
