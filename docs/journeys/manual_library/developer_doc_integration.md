# Journey: Developer Integrating Documentation
[@ANCHOR: journey_developer_integration]

This journey follows a developer adding documentation for their module into the global manual.

## Personas
- **Module Developer**: A developer creating a new Odoo module.

## Steps
1. **Documentation Creation**: The developer writes documentation in `data/documentation.html` within their module.
2. **Installation**: When the module is installed, the Manual Library automatically detects the file.
   - *Related Story:* `doc_installation.md`
   - *Anchor:* `[@ANCHOR: manual_doc_auto_install]`
3. **Verification**: The developer visits `/manual` to ensure their documentation is correctly imported and formatted.
4. **Iterative Update**: If the documentation needs updates, the developer modifies the source file, and the system ensures it's synchronized (typically on next server boot or module update).
