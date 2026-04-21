# Administrator Configures Module Journey

This journey describes the lifecycle of the module's documentation during installation and server operation.

1. **Module Installation**: The administrator installs the `user_websites_seo` module.
2. **Post-Init Hook**: The `post_init_hook` in `hooks.py` is executed.
3. **Documentation Bootstrap**:
   - `install_knowledge_docs(env)` is called.
   - *Code Reference*: `[@ANCHOR: soft_dependency_docs_installation]`
4. **API Detection**: The hook checks if `knowledge.article` is present in the Odoo registry.
5. **Article Creation**: If the API is present and the guide isn't already installed, it reads `data/documentation.html` and creates a new `knowledge.article` using the `odoo_facility_service_internal` service account.
6. **Persistence**: A system parameter `user_websites_seo.docs_installed` is set to ensure the process is idempotent.
7. **Runtime Registry Update**: If the documentation module is installed *after* `user_websites_seo`, the `_register_hook` in `ResUsersSEO` ensures the documentation is installed when the server starts and the registry is loaded.
   - *Code Reference*: `ResUsersSEO._register_hook` in `models/res_users.py`
