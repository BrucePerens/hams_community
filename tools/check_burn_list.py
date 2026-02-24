#!/usr/bin/env python3
import os
import re
import sys
import ast
import argparse

ERROR_RULES = [
    (r'\.xml$', re.compile(r'\bt-raw\s*='), "CRITICAL XSS: 't-raw' is deprecated and dangerous. Use 't-out' and Python's markupsafe.Markup() for safe HTML."),
    (r'\.js$', re.compile(r'\.bindPopup\(\s*`|\.innerHTML\s*=\s*`'), "JS DOM XSS: Template literal passed to bindPopup or innerHTML. Ensure all variables within the literal are sanitized using an escapeHTML function."),
    (r'\.xml$', re.compile(r'<tree\b'), "Legacy view tag: Use <list> instead of <tree>."),
    (r'\.xml$', re.compile(r't-name\s*=\s*["\']kanban-box["\']'), "Legacy view tag: Use <t t-name='card'> instead of kanban-box."),
    (r'\.xml$', re.compile(r'\bt-esc\s*='), "Deprecated directive: Use t-out instead of t-esc."),
    (r'\.xml$', re.compile(r'expand\s*=\s*["\']0["\']'), "Legacy search view: Remove expand='0' from <group> tags."),
    (r'\.xml$', re.compile(r'<group[^>]*\bstring\s*=\s*["\'][^"\']*["\']'), "Legacy search view: Remove string='...' from <group> tags."),
    (r'\.xml$', re.compile(r'expr\s*=\s*["\'].*?id=["\']snippet_structure["\'].*?["\']'), "CRITICAL FRAGILE XPATH: 'snippet_structure' was removed in Odoo 19. Use `expr=\"/*\"` with `position=\"inside\"` instead."),
    (r'\.xml$', re.compile(r'name\s*=\s*["\']category_id["\']'), "Legacy security: Use 'privilege_id' instead of 'category_id' for res.groups."),
    (r'\.xml$', re.compile(r'<field[^>]+name\s*=\s*["\']users["\']'), "CRITICAL BIAS TRAP: Legacy security mapping detected. You MUST use name='user_ids' instead of 'users' for res.groups mapping in Odoo 18+."),
    (r'\.xml$', re.compile(r'<field[^>]+name\s*=\s*["\']groups_id["\']'), "CRITICAL BIAS TRAP: Legacy security mapping detected. You MUST use name='group_ids' instead of 'groups_id' for res.users mapping in Odoo 18+."),
    (r'\.py$', re.compile(r"['\"]groups_id['\"]\s*:"), "CRITICAL BIAS TRAP: Legacy security mapping detected. You MUST use 'group_ids' instead of 'groups_id' when assigning groups to res.users in Odoo 18+."),
    (r'\.js$', re.compile(r'\$\('), "jQuery ($) is forbidden. Use Vanilla JS or modern OWL components."),
    (r'\.js$', re.compile(r'useService\s*\(\s*["\']company["\']\s*\)'), "useService('company') is deprecated in modern Odoo frontends.")
]

WARNING_RULES = [
    (r'\.xml$', re.compile(r'<record.*?model=["\']ir\.cron["\']'), "[AUDIT] CRON ARCHITECTURE: Ensure the Python method implements stateless batching via _trigger() to prevent transaction timeouts."),
    (r'\.xml$', re.compile(r'<xpath\b'), "[AUDIT] XPATH RENDERING: All <xpath> injections must be proven to render correctly. Use to bypass.")
]

MULTILINE_WARNING_RULES = []
EXEMPTIONS = {}

def check_ast_vulnerabilities(filepath, content, lines):
    errors = []
    warnings = []
    filename = os.path.basename(filepath)
    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        errors.append((e.lineno or 1, f"CRITICAL SYNTAX/INDENTATION ERROR: {e.msg}"))
        return errors, warnings
        
    class TaintVisitor(ast.NodeVisitor):
        def __init__(self, filename, lines):
            self.errors = []
            self.warnings = []
            self.assignments = {}
            self.loop_depth = 0
            self.in_http_controller = False
            self.filename = filename
            self.lines = lines
            self._assignment_stack = set()
            self.current_method = None
            self.current_decorators = []
            self.current_kwarg_name = None

        def add_error(self, lineno, msg):
            if lineno <= len(self.lines) and 'burn-ignore' in self.lines[lineno - 1]:
                return
            self.errors.append((lineno, msg))

        def add_warning(self, lineno, msg):
            if lineno <= len(self.lines):
                line_content = self.lines[lineno - 1]
                if 'burn-ignore' in line_content:
                    return
                if 'audit-ignore-mail' in line_content and 'Mail Templates' in msg:
                    return
                if 'audit-ignore-search' in line_content and 'Data Integrity' in msg:
                    return
            self.warnings.append((lineno, msg))

        def is_tainted_sql(self, node):
            if isinstance(node, ast.JoinedStr): 
                return "f-string"
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.Mod): return "%% interpolation"
                if isinstance(node.op, ast.Add): return "string concatenation"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
                is_safe_sql = isinstance(node.func.value, ast.Call) and getattr(node.func.value.func, 'attr', '') == 'SQL'
                if not is_safe_sql: 
                    return ".format()"
            if isinstance(node, ast.Name):
                if node.id in self._assignment_stack:
                    return False
                if node.id in self.assignments:
                    self._assignment_stack.add(node.id)
                    res = self.is_tainted_sql(self.assignments[node.id])
                    self._assignment_stack.remove(node.id)
                    if res:
                        return f"variable '{node.id}' assigned via {res}"
            return False

        def is_untranslated_string(self, node):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value.strip()
                if len(val) < 5 or ' ' not in val:
                    return False
                if val.upper().startswith(('SELECT ', 'UPDATE ', 'INSERT ', 'DELETE ')):
                    return False
                return True
            elif isinstance(node, ast.JoinedStr):
                return True
            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Mod, ast.Add)):
                    return self.is_untranslated_string(node.left)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
                    return self.is_untranslated_string(node.func.value)
                if isinstance(node.func, ast.Name) and node.func.id == '_':
                    return False
            return False

        def visit_Dict(self, node):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in ('error', 'success', 'warning', 'message'):
                    if self.is_untranslated_string(v):
                        self.add_warning(node.lineno, f"[AUDIT] I18N: Untranslated string assigned to UI feedback dict key '{k.value}'. Wrap in _().")
            self.generic_visit(node)

        def visit_For(self, node):
            is_chunking_loop = False
            if isinstance(node.iter, ast.Call) and getattr(node.iter.func, 'id', '') == 'range':
                if len(node.iter.args) == 3:
                    step_arg = node.iter.args[2]
                    if isinstance(step_arg, ast.Name) and step_arg.id in ('chunk_size', 'batch_size'):
                        is_chunking_loop = True

            if not is_chunking_loop:
                self.loop_depth += 1
            self.generic_visit(node)
            if not is_chunking_loop:
                self.loop_depth -= 1

        def visit_FunctionDef(self, node):
            is_controller = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == 'route':
                    is_controller = True
                elif isinstance(dec, ast.Attribute) and dec.attr == 'route':
                    is_controller = True
                
                if isinstance(dec, ast.Attribute) and dec.attr == 'returns':
                    if isinstance(dec.value, ast.Name) and dec.value.id == 'api':
                        self.add_error(node.lineno, "@api.returns is deprecated. Remove it.")
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == 'returns':
                    if isinstance(dec.func.value, ast.Name) and dec.func.value.id == 'api':
                        self.add_error(node.lineno, "@api.returns is deprecated. Remove it.")
            
            old_assignments = self.assignments.copy()
            old_http = self.in_http_controller
            old_method = self.current_method
            old_decorators = self.current_decorators
            old_kwarg = self.current_kwarg_name
            
            self.assignments = {}
            self.in_http_controller = is_controller
            self.current_method = node.name
            self.current_decorators = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute):
                    self.current_decorators.append(dec.attr)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    self.current_decorators.append(dec.func.attr)
            self.current_kwarg_name = node.args.kwarg.arg if node.args.kwarg else None

            self.generic_visit(node)

            self.assignments = old_assignments
            self.in_http_controller = old_http
            self.current_method = old_method
            self.current_decorators = old_decorators
            self.current_kwarg_name = old_kwarg

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.assignments[target.id] = node.value
                elif isinstance(target, ast.Attribute) and target.attr == 'context':
                    if isinstance(target.value, ast.Attribute) and target.value.attr == 'env':
                        if isinstance(target.value.value, ast.Name) and target.value.value.id == 'self':
                            self.add_error(node.lineno, "Never modify `self.env.context` directly. Use the non-mutating `self.with_context(...)` method instead.")
                elif isinstance(target, ast.Name) and target.id == '_sql_constraints':
                    self.add_error(node.lineno, "Use 'models.Constraint' instead of '_sql_constraints'.")
                elif isinstance(target, ast.Subscript):
                    if getattr(target, 'slice', None) and isinstance(getattr(target.slice, 'value', target.slice), str):
                        key_value = getattr(target.slice, 'value', target.slice)
                        if key_value in ('error', 'success', 'warning', 'message'):
                            if self.is_untranslated_string(node.value):
                                self.add_warning(node.lineno, f"[AUDIT] I18N: Untranslated string assigned to UI feedback dict key '{key_value}'. Wrap in _().")
            self.generic_visit(node)

        def visit_Import(self, node):
            for alias in node.names:
                if alias.name == 'pickle':
                    self.add_error(node.lineno, "CRITICAL RCE: The pickle module is vulnerable to arbitrary code execution. Use the json module instead.")
                elif alias.name == 'random':
                    self.add_error(node.lineno, "WEAK CRYPTO: Do not use 'random' for security tokens or passwords. Use the 'secrets' module.")
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module == 'pickle':
                self.add_error(node.lineno, "CRITICAL RCE: The pickle module is vulnerable to arbitrary code execution. Use the json module instead.")
            elif node.module == 'random':
                self.add_error(node.lineno, "WEAK CRYPTO: Do not use 'random' for security tokens or passwords. Use the 'secrets' module.")
            self.generic_visit(node)

        def visit_Constant(self, node):
            if isinstance(node.value, str):
                if re.search(r'\bnumbercall\b', node.value):
                    self.add_error(node.lineno, "Remove 'numbercall'. Odoo 18+ crons run indefinitely if active='True'.")
            self.generic_visit(node)

        def visit_Name(self, node):
            if node.id == 'numbercall':
                self.add_error(node.lineno, "Remove 'numbercall'. Odoo 18+ crons run indefinitely if active='True'.")
            elif node.id == '_sql_constraints':
                self.add_error(node.lineno, "Use 'models.Constraint' instead of '_sql_constraints'.")
            self.generic_visit(node)

        def visit_keyword(self, node):
            if node.arg == 'numbercall':
                self.add_error(getattr(node, 'lineno', 1), "Remove 'numbercall'. Odoo 18+ crons run indefinitely if active='True'.")
            elif node.arg == 'type' and isinstance(node.value, ast.Constant) and node.value.value == 'json':
                self.add_error(getattr(node, 'lineno', 1), "Use type='jsonrpc' instead of type='json' for HTTP routes.")
            elif node.arg == 'index' and isinstance(node.value, ast.Constant) and node.value.value == 'trgm':
                self.add_error(getattr(node, 'lineno', 1), "Invalid Index Type: Use index='trigram' instead of index='trgm' for PostgreSQL pg_trgm extensions in Odoo 19+.")
            elif node.arg == 'csrf' and isinstance(node.value, ast.Constant) and node.value.value in (False, 0):
                if not re.search(r'.*_?api\.py$', self.filename):
                    self.add_error(getattr(node, 'lineno', 1), "SECURITY ALERT: csrf=False found. Ensure this route uses strict HMAC/API key auth, otherwise it is vulnerable to CSRF.")
            elif node.arg == 'shell' and isinstance(node.value, ast.Constant) and node.value.value == True:
                self.add_error(getattr(node, 'lineno', 1), "CRITICAL SHELL INJECTION: Avoid subprocess with shell=True. Pass arguments as a list with shell=False.")
            elif node.arg == 'related' and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and node.value.value.endswith('.users'):
                self.add_error(getattr(node, 'lineno', 1), "Legacy security relation: Use 'user_ids' instead of 'users' when referencing members of res.groups in Python.")
            self.generic_visit(node)

        def visit_Attribute(self, node):
            if node.attr == 'sudo':
                line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                if self.filename == 'security_utils.py':
                    if '.sudo()._xmlid_to_res_id' not in line_content and '.sudo().get_param' not in line_content:
                        self.add_error(node.lineno, "CRITICAL PRIVILEGE ESCALATION: The use of `.sudo()` is strictly forbidden. Use the Service Account Pattern instead.")
                else:
                    if not ('# burn-ignore' in line_content and ('database.secret' in line_content or '.sudo().unlink()' in line_content)):
                        self.add_error(node.lineno, "CRITICAL PRIVILEGE ESCALATION: The use of `.sudo()` is strictly forbidden. Use the Service Account Pattern (`with_user`), Public User ACLs, or add `# burn-ignore` if this is a secure cryptographic system parameter fetch.")

            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                if node.attr == '_context':
                    self.add_error(node.lineno, "Use 'self.env.context' instead of 'self._context'.")
                elif node.attr == '_uid':
                    self.add_error(node.lineno, "Use 'self.env.uid' instead of 'self._uid'.")
            elif node.attr == 'users':
                if isinstance(node.value, ast.Name) and node.value.id in ('group', 'groups', '_group_id'):
                    self.add_error(node.lineno, "Legacy security relation: Use 'user_ids' instead of 'users' when referencing members of res.groups in Python.")
                elif isinstance(node.value, ast.Attribute) and node.value.attr in ('group', 'groups', '_group_id'):
                    self.add_error(node.lineno, "Legacy security relation: Use 'user_ids' instead of 'users' when referencing members of res.groups in Python.")
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                if node.func.id == 'eval':
                    self.add_error(node.lineno, "CRITICAL RCE: Never use native eval(). Use ast.literal_eval() for data structures or odoo.tools.safe_eval() for domains/contexts.")
                elif node.func.id == 'exec':
                    self.add_error(node.lineno, "CRITICAL RCE: The use of exec() is strictly forbidden.")
                elif node.func.id == '_sign_token':
                    self.add_error(node.lineno, "Verify '_sign_token' is not called on models lacking an 'access_token' field (e.g., res.users). Use stateless HMAC instead.")
                elif node.func.id == 'clear_caches':
                    self.add_error(node.lineno, "ORM cache invalidation in Odoo 19+ MUST use `self.env.registry.clear_cache()`.")
                elif node.func.id == '_check_recursion':
                    self.add_error(node.lineno, "Odoo 18+ Hierarchy: Use '_has_cycle()' instead of the deprecated '_check_recursion()'. Note: '_has_cycle()' evaluates to True if a cycle exists, which is the reverse of '_check_recursion()'.")
                elif node.func.id == 'getattr':
                    if len(node.args) >= 2 and getattr(node.args[1], 'value', None) == 'sudo':
                        self.add_error(node.lineno, "CRITICAL PRIVILEGE ESCALATION: Obfuscated use of sudo via getattr().")

            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in ('UserError', 'AccessError', 'ValidationError'):
                if node.args and self.is_untranslated_string(node.args[0]):
                    self.add_warning(node.lineno, f"[AUDIT] I18N: User-facing exception message in '{func_name}' should be wrapped in _() for translation.")
            elif func_name in ('message_post', 'message_subscribe'):
                for kw in node.keywords:
                    if kw.arg in ('body', 'subject') and self.is_untranslated_string(kw.value):
                        self.add_warning(node.lineno, f"[AUDIT] I18N: User-facing chatter '{kw.arg}' in {func_name} should be wrapped in _() for translation.")

            is_cr_execute = False
            if isinstance(node.func, ast.Attribute):
                attr = node.func.attr
                if attr == 'execute':
                    if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'cr':
                        is_cr_execute = True
                    elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'cr':
                        is_cr_execute = True
                elif attr == 'send_mail':
                    self.add_warning(node.lineno, "[AUDIT] Mail Templates: Verify that the model_id of the XML template exactly matches the model of the record ID passed to send_mail().")
                elif attr == '_sign_token':
                    self.add_error(node.lineno, "Verify '_sign_token' is not called on models lacking an 'access_token' field (e.g., res.users). Use stateless HMAC instead.")
                elif attr == 'clear_caches':
                    self.add_error(node.lineno, "ORM cache invalidation in Odoo 19+ MUST use `self.env.registry.clear_cache()`.")
                elif attr == 'clear_cache':
                    is_registry = False
                    if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'registry':
                        is_registry = True
                    elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'registry':
                        is_registry = True
                    if not is_registry:
                        self.add_error(node.lineno, "ORM cache invalidation in Odoo 19+ MUST use `self.env.registry.clear_cache()` instead of calling `.clear_cache()` on methods or models.")
                elif attr in ('search', 'create', 'browse'):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                        self.add_error(node.lineno, "Ambiguous ORM call: Use `self.env['your.model'].search/create/browse()` instead of `self.search/create/browse()` for clarity and to avoid unintended scope.")
                elif attr == '_check_recursion':
                    self.add_error(node.lineno, "Odoo 18+ Hierarchy: Use '_has_cycle()' instead of the deprecated '_check_recursion()'. Note: '_has_cycle()' evaluates to True if a cycle exists, which is the reverse of '_check_recursion()'.")
                elif attr in ('message_post', 'message_subscribe'):
                    val_dump = ast.unparse(node.func.value).strip() if hasattr(ast, 'unparse') else ""
                    if 'res.users' in val_dump or val_dump.endswith('.user_id') or val_dump.endswith('.user'):
                        self.add_error(node.lineno, "Messaging & Followers: Do not call message_post() or message_subscribe() directly on res.users. (Must be called on the underlying user.partner_id).")
                elif attr in ('loads', 'dumps'):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pickle':
                        self.add_error(node.lineno, "CRITICAL RCE: The pickle module is vulnerable to arbitrary code execution. Use the json module instead.")
                elif attr in ('md5', 'sha1'):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'hashlib':
                        self.add_error(node.lineno, "WEAK CRYPTO: MD5 and SHA1 are cryptographically broken. Use hashlib.sha256() or higher.")
                elif attr in ('choice', 'randint', 'random'):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'random':
                        self.add_error(node.lineno, "WEAK CRYPTO: Do not use 'random' for security tokens or passwords. Use the 'secrets' module.")
                
                if attr == 'get' and self.in_http_controller:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == self.current_kwarg_name:
                        self.add_warning(node.lineno, "[AUDIT] CONTROLLER BINDING: Ensure expected form inputs are explicitly declared in the method signature rather than relying solely on kwargs.get().")
                elif attr in ('create', 'write') and self.in_http_controller:
                    for arg in node.args:
                        if isinstance(arg, ast.Name) and arg.id in ('kwargs', 'kw', 'post'):
                            self.add_warning(node.lineno, "[AUDIT] RPC MASS ASSIGNMENT: Never pass raw request payloads directly to create/write. Verify fields are extracted securely.")
                    for kw in node.keywords:
                        if kw.arg is None and isinstance(kw.value, ast.Name) and kw.value.id in ('kwargs', 'kw', 'post'):
                            self.add_warning(node.lineno, "[AUDIT] RPC MASS ASSIGNMENT: Never pass raw request payloads directly to create/write. Verify fields are extracted securely.")

                if self.loop_depth > 0:
                    if attr in ('search', 'search_count', 'read_group'):
                        self.add_error(node.lineno, f"CRITICAL N+1 DB LOCK: ORM '.{attr}()' inside a loop. Pre-fetch outside the loop per ADR-0022.")
                
                if attr in ('search', 'search_count'):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 're':
                        pass # Explicitly ignore re.search
                    else:
                        if attr == 'search':
                            has_limit = any(kw.arg == 'limit' for kw in node.keywords)
                            if not has_limit and not self.filename.startswith('test_'):
                                self.add_warning(node.lineno, "[AUDIT] UNBOUNDED SEARCH: '.search()' called without 'limit'. Ensure strict domain boundaries to prevent OOM (ADR-0022). Note: slicing search() without a limit still fetches all records into memory first.")
                        
                        val = node.func.value
                        is_env_subscript = False
                        if isinstance(val, ast.Subscript):
                            if isinstance(val.value, ast.Attribute) and val.value.attr == 'env':
                                is_env_subscript = True
                            elif isinstance(val.value, ast.Name) and val.value.id == 'env':
                                is_env_subscript = True
                        
                        if is_env_subscript:
                            is_uniqueness_context = False
                            if self.current_method and (self.current_method in ('create', 'write') or self.current_method.startswith('_check_') or self.current_method.startswith('_validate_')):
                                is_uniqueness_context = True
                            elif self.current_decorators and ('constrains' in self.current_decorators or 'onchange' in self.current_decorators):
                                is_uniqueness_context = True
                                
                            if is_uniqueness_context:
                                self.add_warning(node.lineno, f"[AUDIT] Data Integrity: Direct `{attr}()` on an env model without `.sudo()` may cause false negatives if used for uniqueness checks. Review manually.")

            if is_cr_execute and node.args:
                arg = node.args[0]
                taint_reason = self.is_tainted_sql(arg)
                if taint_reason:
                    self.add_error(node.lineno, f"CRITICAL SQLi: Query constructed via {taint_reason} passed to cr.execute(). Use parameterized psycopg2 queries.")

            self.generic_visit(node)

    visitor = TaintVisitor(filename, lines)
    visitor.visit(tree)
    return visitor.errors, visitor.warnings

def scan_file(filepath):
    errors_found = []
    warnings_found = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        return [f"Could not read file: {e}"], []

    filename = os.path.basename(filepath)
    
    if filename.endswith('.xml'):
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            errors_found.append(f"CRITICAL XML SYNTAX/STRUCTURE ERROR: {e}")

    for ext_pattern, regex, warning_msg in MULTILINE_WARNING_RULES:
        if re.search(ext_pattern, filename):
            if 'test_' in filename and 'RPC ORM BYPASS' in warning_msg:
                continue
            if regex.search(content):
                warnings_found.append(f"Global Match: {warning_msg}")

    if filename.endswith('.py'):
        ast_errors, ast_warnings = check_ast_vulnerabilities(filepath, content, lines)
        for lineno, msg in ast_errors:
            stripped = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            errors_found.append(f"Line {lineno} (AST): {msg}\n    {stripped}")
        for lineno, msg in ast_warnings:
            stripped = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            warnings_found.append(f"Line {lineno} (AST): {msg}\n    {stripped}")

    current_xml_model = None
    current_xml_view_type = None
    skip_next_line = False
    in_py_multiline = False
    py_multiline_marker = None

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if filename.endswith('.py'):
            if not in_py_multiline:
                if '"""' in line or "'''" in line:
                    marker = '"""' if '"""' in line else "'''"
                    if line.count(marker) % 2 != 0:
                        in_py_multiline = True
                        py_multiline_marker = marker
                        continue
            else:
                if py_multiline_marker in line:
                    in_py_multiline = False
                    py_multiline_marker = None
                continue
            if stripped.startswith('#'):
                continue

        if filename.endswith('.js') and stripped.startswith('//'):
            continue
        if filename.endswith('.xml') and stripped.startswith('` to suppress these warnings, but **ONLY AFTER** you have built an automated test that mathematically proves the architectural requirement (e.g., `_trigger()` batching for crons, or exact `model_id` matching for mail templates) is fully implemented.
* ``: Allowed on `<xpath>` XML nodes ONLY if an automated test mathematically proves the injected fragment successfully appears in the compiled `arch` or rendered HTML.
Inventing or using unauthorized bypass tags, or omitting the test anchor, constitutes a critical security violation.

---

## 2. ARCHITECTURE & COMMUNITY REUSE (NATIVE ECOSYSTEM FIRST)

* **The Reusability Mandate:** Before architecting a new custom module from scratch, you **MUST** actively evaluate existing Odoo 19 Community modules (e.g., `event`, `survey`, `membership`, `website_slides`, `forum`, `website_sale`) to determine if they can fulfill the core functional requirements.
* **Specialization Over Silos:** Do not build redundant custom CRUD pipelines or base architectures for features that Odoo already handles natively. Instead, build lightweight "Domain Extension" modules that inherit (`_inherit` or `_inherits`) from the core Community modules to inject domain-specific fields, validation logic, and security rules.
* **Compatibility Check:** You must mentally ensure that the targeted community module exists and retains the required functionality in **Odoo 19** before committing to its use.
* **External Daemons & Workers:** Long-running processes, heavy ETL tasks, or persistent sockets MUST NOT run inside Odoo WSGI workers. They MUST be offloaded to external Python daemons communicating via XML-RPC. Whenever you architect such a module, you **MUST** offer to write the external daemon. Audits must actively scan for modules that specify a daemon dependency where the daemon does not yet exist.

---

## 3. PYTHON & ORM STANDARDS

### 📂 File Organization
* **Modular Extensions:** Organize code by Model.
    * For new models: Use `models/model_name.py`.
    * For extending core models (e.g., `res.users`):
        * Small extensions (<100 lines): Append to `models/res_users.py` if it exists.
        * Feature-specific extensions: Create `models/res_users_feature.py` (e.g., `res_users_website.py`) to maintain separation of concerns.

### 🗄️ Models & Logic
* **Constraints:** Use `models.Constraint` (Python class attribute) instead of `_sql_constraints`.
* **Bulk Operation Safety:** All creation/update methods MUST support batch processing to avoid N+1 query issues. Never assume a payload contains only a single record.
* **Safe Property Access:** NEVER use `'field' in record` (which causes errors). Use `if 'field' in record._fields:` to check field existence before access.
* **Inverse Relationships:**
    * **Rule:** For every `Many2one` field on Model A linking to Model B, you must implement the inverse `One2many` on Model B to ensure data navigability in the backend.

### 🏎️ Performance & Scalability
* **Cron Batching:** Long-running scheduled actions MUST NOT attempt to process an entire database table in one transaction. They MUST process records in manageable batches (e.g., array slicing) and programmatically re-trigger themselves (`self.env.ref('my_module.my_cron')._trigger()`) if unprocessed records remain.
* **ORM Caching:** High-traffic frontend lookups (e.g., resolving string slugs to database IDs on every page load) MUST utilize Odoo's `@tools.ormcache`. Cache MUST be explicitly cleared (e.g., `type(self).clear_cache()`) in the model's `write` or `unlink` methods when indexed fields change.

### 🔒 Security Patterns & Native Idioms
You are strictly **FORBIDDEN** from using `.sudo()` as a crutch to bypass access errors. You MUST utilize one of the following native Odoo idioms:

* **The "Centralized Security Utility" Pattern:**
    * **Context:** The system needs to retrieve system parameters (`ir.config_parameter`) or resolve XML IDs (`ir.model.data`), which generally require escalated privileges, without exposing inline `.sudo()` calls.
    * **Mandate:** Do NOT use `.sudo().get_param()` or `.sudo()._xmlid_to_res_id()`. Instead, delegate to `ham_base.security_utils` via `request.env['ham.security.utils']._get_system_param(key)` or `_get_service_uid(xml_id)`. The latter employs RAM caching (`@tools.ormcache`) to execute the database lookup securely once per boot cycle.
    * **Skeleton Key Prevention (RPC & SSTI):**
        * Methods on the utility model MUST be prefixed with an underscore (`_get_...`) to strictly block public XML-RPC / JSON-RPC execution.
        * `_get_system_param` MUST implement a strict hardcoded `frozenset` whitelist. You MUST NEVER add cryptographic keys (like `database.secret`) to this whitelist, as QWeb template injection could expose it.
        * If a controller strictly requires a cryptographic secret (e.g., for HMAC signing), it must bypass the utility and use `.sudo().get_param('database.secret')` inline, appending `# burn-ignore-sudo: Tested by [\ANCHOR: ...]` to the line to explicitly declare the security exception to the linter.
* **The "Service Account" Pattern (Dedicated Execution Context):**
    * **Context:** The system needs to perform an elevated background task, API token validation, or cryptographic operation triggered by an unauthenticated or under-privileged user.
    * **Mandate:** Do NOT use `.sudo()`. Instead:
        1. Create an isolated `res.groups` with no human members.
        2. Create a dedicated internal `res.users` (the Service Account) belonging *only* to that group.
        3. Flag the user with `is_service_account="True"` in the XML to permanently block interactive web logins (See ADR-0005).
        4. Grant that specific group the exact ACLs (`ir.model.access.csv`) and Record Rules (`ir.rule`) required for the task.
        5. In the controller or method, fetch the Service Account's ID securely via `env['ham.security.utils']._get_service_uid('module.user_xml_id')` and execute the logic using `.with_user(svc_uid)`.
* **The "Public Guest User" Idiom:**
    * **Context:** An unauthenticated guest needs to submit data (e.g., a contact form, an issue report).
    * **Mandate:** Do NOT use `.sudo().create()` in the controller. Instead, define an Access Control List (`ir.model.access.csv`) granting `perm_create=1` to `base.group_public` for that specific model. Rely purely on the database layer to restrict read/write access.
* **The "Impersonation" Idiom (`with_user`):**
    * **Context:** An API webhook or background task identifies a specific user via a token, but the request arrives unauthenticated.
    * **Mandate:** Do NOT use `.sudo().write()`. Instead, shift the environment context to the identified user: `request.env['target.model'].with_user(user).create(...)`. This ensures the action is strictly bound by the user's Record Rules.
* **The "Self-Writeable Fields" Idiom:**
    * **Context:** A user needs to update their own preferences on `res.users`, which normally requires admin rights.
    * **Mandate:** Do NOT use `request.env.user.sudo().write()`. Instead, override `SELF_WRITEABLE_FIELDS` (or `_get_writeable_fields` in Odoo 18+) on the `res.users` model to explicitly whitelist the specific preference fields.
* **Privilege Hierarchy (Odoo 19+):** When defining security groups in XML, `res.groups` must not link directly to a `category_id`. They MUST be nested under a `res.groups.privilege` record (via `privilege_id`), which in turn links to the `ir.module.category`.

### 🧩 Module Initialization & Dynamic Documentation Injection
* **Documentation Payload Injection:** Every module must expose its documentation to the platform's native `knowledge.article` structure dynamically via a `post_init_hook` in `hooks.py`.
* **Decoupled Content (`file_open`):** HTML documentation payloads must reside in separate files (e.g., `data/documentation.html`). Use Odoo's native `odoo.tools.file_open` utility inside the hook to read the file securely. **Never hardcode HTML into Python.**
* **Soft Dependency Management:** The platform `knowledge.article` API (via `manual_library` or Enterprise) must be treated as a **Soft Dependency**.
    * Do NOT explicitly list it in the `depends` block of `__manifest__.py` unless the module fundamentally cannot operate without it.
    * The `post_init_hook` MUST explicitly check for the API's presence before attempting creation: `if 'knowledge.article' in env: ...`.

---

## 4. XML, VIEWS & QWEB STANDARDS

### 🎨 View Syntax & Accessibility
* **Tags:** Use `<list>` instead of `<tree>`, and `<t t-name="card">` instead of `kanban-box`.
* **Output:** Use `t-out` instead of `t-esc`.
* **Safety:** Do not use raw HTML entities (`&larr;`). Use numeric entities (`&#8592;`).
* **WCAG in QWeb:** QWeb templates must produce accessible HTML. Use `aria-label` or `title` attributes on icon-only buttons (e.g., `<button class="btn" icon="fa-trash" aria-label="Delete"/>`). Ensure proper heading hierarchy (`<h1>` to `<h6>`) within `website.page` layouts.
* **QWeb Logic:** Python built-ins (`getattr`, `setattr`, `hasattr`) are **FORBIDDEN** in QWeb. Use `t-if="'field' in record._fields"` only if absolutely necessary for polymorphic views.

### ⚙️ Configuration Views
* **Inheritance:** Must inherit `base.res_config_settings_view_form`.
* **Structure:** Target the form directly using `xpath expr="//form" position="inside"`. Do **not** try to locate internal divs like `div[hasclass('settings')]` as they are fragile.
* **Snippets:** Target snippet menus using `xpath expr="/*" position="inside"` rather than explicitly checking for legacy IDs like `snippet_structure`.
* **Isolation:** Create a new `div` block with `class="app_settings_block"` and a unique `data-key` (e.g., `data-key="my_module"`) to create a dedicated sidebar entry.

### 🖥️ Frontend JavaScript & UX
* **Framework Constraints:** The use of jQuery (`$`) is strictly **FORBIDDEN** in new frontend assets. Use Vanilla JS or OWL for all DOM manipulation and component logic.
* **Native Toast Notifications:** Frontend feedback for transient actions (e.g., successfully submitting a form, handled via URL parameters like `?success=1`) MUST trigger Odoo's native notification bus (Toast messages) rather than relying solely on static inline text renders.

### 🌍 Internationalization (i18n)
* **Translation Architecture:** Every user-facing module MUST include an `i18n/` directory containing a base `module_name.pot` file.
* **Required Languages:** The module MUST also contain `.po` translated files for the seven most popular languages: German (`de.po`), Spanish (`es.po`), French (`fr.po`), Italian (`it.po`), Japanese (`ja.po`), Dutch (`nl.po`), and Portuguese (`pt.po`).
* **Implementation:** Ensure all user-facing strings in Python (using `_()`), XML, and QWeb templates are properly marked for Odoo's translation engine.

### ⚖️ Regulatory Compliance & Cookie Management
* **Native Consent Integration:** Custom modules MUST integrate with and respect Odoo's native website cookie consent mechanism (`website.cookies_bar`). 
* **Prohibition:** You are strictly **FORBIDDEN** from implementing custom, hardcoded cookie banners or third-party consent scripts. All tracking must hook into the core framework's consent state.
* **Data Portability & Erasure (GDPR/CCPA):** Any module that stores Personally Identifiable Information (PII) or user-generated content MUST integrate into the global GDPR framework by extending `res.users`:
    * **Export:** Override `_get_gdpr_export_data(self)` to append the user's records to the export dictionary.
    * **Erasure:** Override `_execute_gdpr_erasure(self)` to permanently hard-delete (`.sudo().unlink()`) the user's data. **CRITICAL:** You are STRICTLY FORBIDDEN from relying on database-level `ondelete='cascade'` constraints to handle data destruction. You MUST programmatically execute the deletion in this hook to guarantee execution at the ORM layer.

### 🔍 SEO & Discovery
* **OpenGraph Automation:** Public-facing, user-generated content pages (e.g., Profiles, Portfolios, Blogs) MUST dynamically inject OpenGraph (`<meta property="og:..."/>`) tags to ensure rich social media previews. This is achieved by passing `default_title`, `default_description`, and `default_image` keys into the QWeb rendering dictionary used by `website.layout`.

---

## 5. CONTROLLERS & ROUTING

* **API:** Use `get_current_website()` instead of `get_main_website()`.
* **Slugs:** Dynamic routing must handle slugs safely.
* **JSON-RPC:** Legacy HTTP routes using `type="json"` must be upgraded to `type="jsonrpc"`.
* **Auth:** Routes creating content must require `auth="user"`. Routes for reading content can be `auth="public"`.
* **Public Route Anti-Spam:** All unauthenticated `POST` routes (e.g., public forms, abuse reports) MUST implement anti-spam measures. Use Odoo's native reCAPTCHA context or honeypot fields to prevent malicious bot automation.
* **Standard Template Context:** When rendering built-in Odoo templates (e.g., `website_blog.blog_post_short`), you MUST verify the template's source code and ensure all expected QWeb context variables (e.g., `pager`, `main_object`, `blogs`) are injected into the rendering dictionary to prevent `KeyError` crashes.
* **Explicit Parameter Binding:** When defining HTTP controller methods, you **MUST** explicitly declare expected form inputs and query parameters in the method signature (e.g., `def my_route(self, my_param=None, **kwargs):`) rather than relying solely on `kwargs.get()` or `request.params`. This guarantees reliable parameter binding when executing automated HTTP tests via `self.url_open()` and prevents silent validation bypasses.

---

## 6. ODOO VERIFICATION & AUDIT PROTOCOL

Please refer to the `FINAL VERIFICATION & AUDIT PROTOCOL` section within `LLM_GENERAL_REQUIREMENTS.md` for the overarching checklist regarding Registry, Imports, Schema Sync, Authorization, Test Coverage, and Accessibility.

---

## 7. OUTPUT FORMATTING

Please refer to the `OUTPUT FORMATTING & TRANSPORT PROTOCOLS` section within `LLM_GENERAL_REQUIREMENTS.md` for the strict AEF 4.0 JSON structure, Base64 prohibition, and UI-crashing tag mitigation mandates.
