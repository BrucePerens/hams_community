# Documentation Setup Journey

This journey describes how the `test_real_transaction` module ensures its documentation is properly installed.

1.  **Server Start/Module Loading**: The Odoo server starts or the module is installed/updated.
2.  **Registry Loading**: Odoo builds the model registry.
3.  **Bootstrap Trigger**: Once the registry is ready, the `test_real_transaction.noisy_table` model executes its `_register_hook` ([@ANCHOR: documentation_bootstrap]).
4.  **API Detection**: The hook calls the documentation injection logic ([@ANCHOR: documentation_injection]), which checks if a compatible documentation model (like `knowledge.article`) is available in the environment.
5.  **Service Account Context**: If the API is available, the system switches to a secure service account context (usually `zero_sudo.odoo_facility_service_internal`) to perform the installation.
6.  **Idempotent Check**: The system checks if the "Real Transaction Testing Facility Guide" already exists to avoid duplicate entries.
7.  **Content Loading**: The documentation content is read from `test_real_transaction/data/documentation.html`.
8.  **Record Creation**: A new article is created and published in the knowledge base, making it accessible to authorized users.
