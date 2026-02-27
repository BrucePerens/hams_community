#!/usr/bin/env python3
import os
import re
import sys
import ast
import argparse

ERROR_RULES = [
    (r'\.xml$', re.compile(r'\bt-raw\s*='), "CRITICAL XSS: 't-raw' is deprecated and dangerous. Use 't-out' and Python's markupsafe.Markup() for safe HTML."),
    (r'\.xml$', re.compile(r'request\.env'), "CRITICAL SSTI: Using 'request.env' inside QWeb templates exposes the database to Remote Code Execution. Compute values in Python and pass them via the rendering context."),
    (r'\.js$', re.compile(r'\.bindPopup\(\s*`|\.innerHTML\s*=\s*`'), "JS DOM XSS: Template literal passed to bindPopup or innerHTML. Ensure all variables within the literal are sanitized using an escapeHTML function."),
    (r'\.xml$', re.compile(r'<tree\b'), "Legacy view tag: Use <list> instead of <tree>."),
    (r'\.xml$', re.compile(r't-name\s*=\s*["\']kanban-box["\']'), "Legacy view tag: Use <t t-name='card'> instead of kanban-box."),
    (r'\.xml$', re.compile(r'\bt-esc\s*='), "Deprecated directive: Use t-out instead of t-esc."),
    (r'\.xml$', re.compile(r'expand\s*=\s*["\']0["\']'), "Legacy search view: Remove expand='0' from <group> tags."),
    (r'\.xml$', re.compile(r'<group[^>]*\bstring\s*=\s*["\'][^"\']*["\']'), "Legacy search view: Remove string='...' from <group> tags."),
    (r'\.xml$', re.compile(r'expr\s*=\s*["\'].*?id=["\']snippet_structure["\'].*?["\']'), "CRITICAL FRAGILE XPATH: 'snippet_structure' was removed in Odoo 19. Use `expr=\"/*\"` with `position=\"inside\"` instead."),
    (r'\.xml$', re.compile(r'name\s*=\s*["\']category_id["\']'), "Legacy security: Use 'privilege_id' instead of 'category_id' for res.groups."),
    (r'\.xml$', re.compile(r'<field[^>]+name\s*=\s*["\']users["\']'), "CRITICAL BIAS TRAP: Legacy security mapping detected. You MUST use name='user_ids' instead of 'users' for res.groups mapping in Odoo 18+."),
    (r'\.xml$', re.compile(r'<field[^>]+name\s*=\s*["\']groups_id["\']'), "CRITICAL BIAS TRAP: Odoo 18+ normalized the res.users groups relation to 'group_ids'. Do not use 'groups_id'."),
    (r'\.py$', re.compile(r"['\"]groups_id['\"]\s*:"), "CRITICAL BIAS TRAP: Odoo 18+ normalized the res.users groups relation to 'group_ids'. Do not use 'groups_id'."),
    (r'\.py$', re.compile(r'^\s*_sql_constraints\s*='), "CRITICAL DEPRECATION: Odoo 19+ no longer supports '_sql_constraints'. Use 'models.Constraint' class attributes instead."),
    (r'\.py$', re.compile(r'\bget_module_resource\b'), "CRITICAL DEPRECATION: 'get_module_resource' was removed in Odoo 19. Use 'odoo.tools.file_open' instead."),
    (r'controllers/.*\.py$', re.compile(r'@(?:tools\.)?ormcache'), "CRITICAL ARCHITECTURE: Cannot use @ormcache on Controller methods. Controllers lack the 'pool' attribute. Use class-level dictionary caches instead."),
    (r'\.js$', re.compile(r'\$\('), "jQuery ($) is forbidden. Use Vanilla JS or modern OWL components."),
    (r'\.js$', re.compile(r'useService\s*\(\s*["\']company["\']\s*\)'), "useService('company') is deprecated in modern Odoo frontends.")
]

WARNING_RULES = [
    (r'\.xml$', re.compile(r'<record.*?model=["\']ir\.cron["\']'), "[AUDIT] CRON ARCHITECTURE: Ensure the Python method implements stateless batching via _trigger() to prevent transaction timeouts."),
    (r'\.xml$', re.compile(r'<xpath\b'), "[AUDIT] XPATH RENDERING: All <xpath> injections must be proven to render correctly. Use an audit-ignore-xpath anchor bypass.")
]

MULTILINE_WARNING_RULES = []
EXEMPTIONS = {}

# ADR-0059: Deep AST Test Verification
REQUIRE_TEST_VERIFICATION = []
FOUND_TEST_CONTENTS = {}

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

        def visit_With(self, node):
            is_cursor = False
            for item in node.items:
                if isinstance(item.context_expr, ast.Call):
                    if isinstance(item.context_expr.func, ast.Attribute) and item.context_expr.func.attr == 'cursor':
                        is_cursor = True
            if is_cursor:
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) and child.func.attr in ('commit', 'rollback'):
                        self.add_error(child.lineno, "CURSOR MISMANAGEMENT: Do not manually call commit() or rollback() inside a `with registry.cursor():` block. It breaks the psycopg2 state. Use `cr = registry.cursor()` with try/finally instead.")
            self.generic_visit(node)

        def visit_Dict(self, node):
            keys_found = set()
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys_found.add(k.value)
                    if k.value in ('error', 'success', 'warning', 'message'):
                        if self.is_untranslated_string(v):
                            self.add_warning(node.lineno, f"[AUDIT] I18N: Untranslated string assigned to UI feedback dict key '{k.value}'. Wrap in _().")
                    if k.value == 'groups_id':
                        self.add_error(node.lineno, "CRITICAL BIAS TRAP: Odoo 18+ normalized the res.users groups relation to 'group_ids'. Do not use 'groups_id'.")
            
            if 'owner_user_id' in keys_found and 'user_websites_group_id' in keys_found:
                self.add_error(node.lineno, "MUTUAL EXCLUSIVITY TRAP: Cannot assign both 'owner_user_id' and 'user_websites_group_id' in the same dictionary. They are mutually exclusive.")
                
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
            elif getattr(node, 'module', '') == 'odoo.modules':
                for alias in node.names:
                    if alias.name == 'get_module_resource':
                        self.add_error(node.lineno, "CRITICAL DEPRECATION: 'get_module_resource' is removed in Odoo 19. Use 'odoo.tools.file_open' instead.")
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
            elif node.arg == 'groups_id':
                self.add_error(getattr(node, 'lineno', 1), "CRITICAL BIAS TRAP: Odoo 18+ normalized the res.users groups relation to 'group_ids'. Do not use 'groups_id'.")
            elif node.arg in ('oldname', 'select'):
                self.add_error(getattr(node, 'lineno', 1), f"CRITICAL DEPRECATION: '{node.arg}' is a legacy database field attribute. Remove 'oldname' entirely, and use 'index=' instead of 'select='.")
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
                if node.func.id == 'hash':
                    self.add_error(node.lineno, "CRITICAL NON-DETERMINISM: Python's native `hash()` is salted per-process and MUST NOT be used for database locks or distributed systems. Use `env['zero_sudo.security.utils']._get_deterministic_hash()` instead.")
                elif node.func.id == 'eval':
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
            attr = ""
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
                elif attr == 'sleep':
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'time':
                        line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""
                        if 'audit-ignore-sleep' not in line_content:
                            self.add_warning(node.lineno, "[AUDIT] THREAD BLOCKING: 'time.sleep()' halts the worker. Ensure this is inside a background thread/daemon for rate-limiting, NOT a synchronous web request. Use an audit-ignore-sleep bypass if verified.")
                elif attr == 'Thread':
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'threading':
                        self.add_error(node.lineno, "CRITICAL DOS VECTOR: Do not spawn unbounded `threading.Thread` instances. Use a bounded `ThreadPoolExecutor` or message queue.")
                
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
                    pass 
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

    if filename.startswith('test_') and filename.endswith('.py'):
        FOUND_TEST_CONTENTS[filepath] = content

    if filename.endswith('.py'):
        ast_errors, ast_warnings = check_ast_vulnerabilities(filepath, content, lines)
        for lineno, msg in ast_errors:
            stripped = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            errors_found.append(f"Line {lineno} (AST): {msg}\n      Code: `{stripped}`")
        for lineno, msg in ast_warnings:
            stripped = lines[lineno - 1].strip() if lineno <= len(lines) else ""
            warnings_found.append(f"Line {lineno} (AST): {msg}\n      Code: `{stripped}`")

    current_xml_model = None
    current_xml_view_type = None
    skip_next_line = False
    in_py_multiline = False
    py_multiline_marker = None
    in_view_block = False
    view_has_tour_anchor = False
    view_start_line = 0

    if filename.endswith('.js'):
        if 'web_tour.tours' in content and 'trigger:' not in content:
            errors_found.append("UI TOUR MANDATE VIOLATION: Odoo UI Tours MUST contain at least one 'trigger:' step to validate DOM elements.")

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
        if filename.endswith('.xml') and stripped.startswith('<' + '!--'):
            continue

        if skip_next_line:
            skip_next_line = False
            if filename.endswith('.xml'):
                model_match = re.search(r'<record.*?model=["\']([^">]+)["\']', line)
                if model_match:
                    current_xml_model = model_match.group(1)
            continue

        if 'burn-ignore' in line:
            if not ('database.secret' in line or '.sudo().unlink()' in line):
                errors_found.append(f"Line {line_num}: UNAUTHORIZED BYPASS. '# burn-ignore' was used on an unauthorized line.\n      Code: `{stripped}`")
            continue

        if 'audit-ignore' in line:
            valid_audits = ['audit-ignore-cron', 'audit-ignore-mail', 'audit-ignore-search', 'audit-ignore-xpath', 'audit-ignore-sleep', 'audit-ignore-view']
            if not any(tag in line for tag in valid_audits):
                errors_found.append(f"Line {line_num}: UNAUTHORIZED BYPASS. Invalid audit-ignore tag used.\n      Code: `{stripped}`")
            else:
                anchor_match = re.search(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]', line)
                if anchor_match:
                    ignore_type = next((tag for tag in valid_audits if tag in line), None)
                    REQUIRE_TEST_VERIFICATION.append({
                        'anchor': anchor_match.group(1),
                        'type': ignore_type,
                        'file': filepath,
                        'line': line_num
                    })

        if 'burn-ignore-sudo' in line:
            anchor_match = re.search(r'\[%ANCHOR:\s*([a-zA-Z0-9_]+)\s*\]', line)
            if anchor_match:
                REQUIRE_TEST_VERIFICATION.append({
                    'anchor': anchor_match.group(1),
                    'type': 'burn-ignore-sudo',
                    'file': filepath,
                    'line': line_num
                })

        if filename.endswith('.xml'):
            model_match = re.search(r'<record.*?model=["\']([^">]+)["\']', line)
            if model_match:
                current_xml_model = model_match.group(1)
                if current_xml_model == 'ir.ui.view':
                    in_view_block = True
                    view_has_tour_anchor = False
                    view_start_line = line_num
            elif '<search' in line:
                current_xml_view_type = 'search'
            elif '<form' in line:
                current_xml_view_type = 'form'
            elif '<list' in line:
                current_xml_view_type = 'list'
            elif re.search(r'<template\b', line):
                in_view_block = True
                view_has_tour_anchor = False
                view_start_line = line_num
                
            if in_view_block:
                if 'Verified by [%ANCHOR:' in line or 'Tested by [%ANCHOR:' in line or 'audit-ignore-view' in line:
                    view_has_tour_anchor = True
                    
            if '</record>' in line or '</template>' in line:
                if in_view_block and not view_has_tour_anchor:
                    errors_found.append(f"Line {view_start_line}: UI TOUR MANDATE VIOLATION: Every template and ir.ui.view MUST be tested by a frontend UI Tour. Add an anchor or use audit-ignore-view to bypass.")
                in_view_block = False
                if '</record>' in line:
                    current_xml_model = None
                    current_xml_view_type = None

        for ext_pattern, regex, error_msg in ERROR_RULES:
            if re.search(ext_pattern, filename):
                if current_xml_model != 'res.groups' and ('category_id' in regex.pattern or 'users' in regex.pattern):
                    continue
                if 'Legacy search view' in error_msg and current_xml_view_type != 'search':
                    continue
                if regex.search(line):
                    exempted = False
                    for ex_file_pat, ex_line_pats in EXEMPTIONS.items():
                        if re.search(ex_file_pat, filename):
                            for ex_pat in ex_line_pats:
                                if re.search(ex_pat, line):
                                    exempted = True
                                    break
                            if exempted:
                                break
                    if exempted:
                        continue
                    errors_found.append(f"Line {line_num}: {error_msg}\n      Code: `{stripped}`")
                    
        for ext_pattern, regex, warning_msg in WARNING_RULES:
            if re.search(ext_pattern, filename):
                if current_xml_model != 'res.groups' and ('category_id' in regex.pattern or 'users' in regex.pattern):
                    continue
                if regex.search(line):
                    if 'audit-ignore-cron' in line and 'CRON ARCHITECTURE' in warning_msg:
                        continue
                    if 'audit-ignore-xpath' in line and 'XPATH RENDERING' in warning_msg:
                        continue
                    exempted = False
                    for ex_file_pat, ex_line_pats in EXEMPTIONS.items():
                        if re.search(ex_file_pat, filename):
                            for ex_pat in ex_line_pats:
                                if re.search(ex_pat, line):
                                    exempted = True
                                    break
                            if exempted:
                                break
                    if exempted:
                        continue
                    warnings_found.append(f"Line {line_num}: {warning_msg}\n      Code: `{stripped}`")
                    
    return errors_found, warnings_found

def main():
    parser = argparse.ArgumentParser(description="Scan Odoo modules for Odoo 19+ deprecated syntax.")
    parser.add_argument("directory", nargs='?', default=".", help="Directory to scan (default: current)")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.directory)
    print(f"Scanning {target_dir} for Odoo 19+ Burn List violations...")

    total_errors = 0
    total_warnings = 0
    scanned_files = 0
    this_script_name = os.path.basename(__file__)

    for root, dirs, files in os.walk(target_dir):
        # Exclude tools, daemons, and environments to prevent false positives
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('__pycache__', 'node_modules', 'tools', 'daemons', 'venv', 'env', 'hams_local_relay')]
        
        for file in files:
            if file == this_script_name or file == 'LLM_LINTER_GUIDE.md':
                continue
            
            if file.endswith('.py') or file.endswith('.xml') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                scanned_files += 1
                
                errors, warnings = scan_file(filepath)
                
                if errors or warnings:
                    rel_path = os.path.relpath(filepath, target_dir)
                    print(f" 📄 {rel_path}")
                
                    if warnings:
                        total_warnings += len(warnings)
                        for warn in warnings:
                            print(f"  ⚠️  WARNING: {warn}")
                            
                    if errors:
                        total_errors += len(errors)
                        for err in errors:
                            print(f"  ❌ ERROR: {err}")

    # Phase 2: Test Verification for Bypasses (ADR-0058/0059)
    verification_errors = 0
    print("\nExecuting Phase 2: Test Verification for Bypasses (ADR-0058/0059)...")
    for req in REQUIRE_TEST_VERIFICATION:
        anchor = req['anchor']
        b_type = req['type']
        
        target_content = None
        target_file = None
        for t_file, t_content in FOUND_TEST_CONTENTS.items():
            if f"[%ANCHOR: {anchor}]" in t_content:
                target_content = t_content
                target_file = t_file
                break
                
        if not target_content:
            print(f"  ❌ ERROR: Orphaned Bypass. {b_type} in {req['file']}:{req['line']} cites anchor '{anchor}', but this anchor was not found in any test file.")
            verification_errors += 1
            total_errors += 1
            continue
            
        if target_file.endswith('.js'):
            is_valid = False
            missing_msg = ""
            if b_type == 'audit-ignore-xpath':
                if 'get_view' in target_content or 'url_open' in target_content or '_get_combined_arch' in target_content or 'trigger:' in target_content:
                    is_valid = True
                else:
                    missing_msg = "Must contain 'trigger:' to verify UI rendering in JS."
            else:
                is_valid = True
            
            if not is_valid:
                print(f"  ❌ ERROR: Invalid JS Test Implementation. {missing_msg}")
                verification_errors += 1
                total_errors += 1
            continue

        try:
            tree = ast.parse(target_content, filename=target_file)
        except SyntaxError as e:
            print(f"  ❌ ERROR: Syntax error in test file {target_file}: {e}")
            verification_errors += 1
            total_errors += 1
            continue

        anchor_line = -1
        for i, t_line in enumerate(target_content.splitlines(), 1):
            if f"[%ANCHOR: {anchor}]" in t_line:
                anchor_line = i
                break
                
        target_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if getattr(node, 'lineno', 0) <= anchor_line <= getattr(node, 'end_lineno', float('inf')):
                    target_func = node
                    break
                    
        if not target_func:
            print(f"  ❌ ERROR: Test Anchor '{anchor}' is not inside an AST FunctionDef in {target_file}.")
            verification_errors += 1
            total_errors += 1
            continue

        found_query_count = False
        found_view = False
        found_trigger = False
        found_mail = False
        
        for node in ast.walk(target_func):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ('assertQueryCount', 'assertLess', 'assertLessEqual'): found_query_count = True
                if node.func.attr in ('get_view', 'url_open', '_get_combined_arch'): found_view = True
                if node.func.attr == '_trigger': found_trigger = True
                if node.func.attr in ('send_mail', 'message_post'): found_mail = True
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call) and isinstance(item.context_expr.func, ast.Attribute):
                        if item.context_expr.func.attr == 'assertQueryCount':
                            found_query_count = True

        is_valid = False
        missing_msg = ""
        if b_type in ('audit-ignore-xpath', 'audit-ignore-view'):
            if found_view: is_valid = True
            else: missing_msg = "AST requires 'get_view', 'url_open', or '_get_combined_arch' call inside the test function."
        elif b_type == 'audit-ignore-search':
            has_limit = any(isinstance(k, ast.keyword) and k.arg == 'limit' for n in ast.walk(target_func) if isinstance(n, ast.Call) for k in n.keywords)
            if found_query_count or has_limit: is_valid = True
            else: missing_msg = "AST requires 'assertQueryCount' context manager or 'limit=' kwarg inside the test function."
        elif b_type == 'audit-ignore-cron':
            if found_trigger: is_valid = True
            else: missing_msg = "AST requires '_trigger()' call inside the test function for batching."
        elif b_type == 'audit-ignore-mail':
            if found_mail: is_valid = True
            else: missing_msg = "AST requires 'send_mail' or 'message_post' inside the test function."
        else:
            is_valid = True

        if not is_valid:
            print(f"  ❌ ERROR: Invalid Test Implementation (AST). {b_type} in {req['file']}:{req['line']} cites anchor '{anchor}'. The test fails mechanical AST verification: {missing_msg}")
            verification_errors += 1
            total_errors += 1

    if verification_errors == 0 and len(REQUIRE_TEST_VERIFICATION) > 0:
        print(f"✅ Verified {len(REQUIRE_TEST_VERIFICATION)} bypass anchors successfully.")

    print(f"\nScan Complete: Checked {scanned_files} files.")
    print(f"Total Errors: {total_errors} | Total Warnings (Audits): {total_warnings}")
    
    if total_errors > 0:
        print("❌ Found Burn List errors. Please fix them before deploying.")
        sys.exit(1)
    else:
        if total_warnings > 0:
            print("✅ Passed with warnings. Audits require manual verification, but the build will continue.")
        else:
            print("✅ No Burn List violations found! Your codebase is clean.")
        sys.exit(0)

if __name__ == '__main__':
    main()
