# Story: Automated Documentation Installation
[@ANCHOR: story_manual_doc_installation]

This story describes how the system automatically discovers and installs documentation from other modules.

## Scenario
A new Odoo module with a `data/documentation.html` file is installed.

## Process
1. During server boot or module installation, the `_register_hook` in `ir.module.module` is called.
2. The `_install_all_module_documentation` method `[@ANCHOR: manual_doc_auto_install]` is triggered.
3. The system identifies available knowledge-base providers (either `manual_library` or Odoo Enterprise `knowledge`).
4. It iterates through installed modules and looks for `data/documentation.html` or `LLM_DOCUMENTATION.md`.
5. If found, it reads the content and creates a new article record under a service account context.
6. This ensures documentation is always available regardless of module installation order (soft-dependency pattern).

## Technical Details
- Model: `ir.module.module`
- Methods: `_register_hook`, `_install_all_module_documentation`, `_install_module_documentation`
- Access: Uses `manual_library.user_manual_library_service_account` or `zero_sudo.odoo_facility_service_internal`.
