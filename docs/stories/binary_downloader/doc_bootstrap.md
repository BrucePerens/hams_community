# Story: Documentation Bootstrapping

## Purpose
The `install_knowledge_docs` hook ensures that the module's technical and user documentation is automatically available in the Odoo Knowledge or Manual Library system upon installation.

## Process
1. **API Detection:** It checks if the `knowledge.article` model is present in the Odoo environment.
2. **Service Account Selection:** It attempts to use the `manual_library.user_manual_library_service_account`, falling back to `zero_sudo.odoo_facility_service_internal` if necessary.
3. **Idempotency Check:** It searches for an existing article titled "Binary Downloader Facility" to avoid duplicate creation.
4. **Content Loading:** If the article is missing, it reads the content from `binary_downloader/data/documentation.html`.
5. **Article Creation:** It creates a new `knowledge.article` (or `manual.article`) record with the documentation content, setting appropriate icons and permissions based on the available API fields.

## Traceability
- **Code:** `install_knowledge_docs` in `hooks.py` `[@ANCHOR: binary_doc_bootstrap]`
