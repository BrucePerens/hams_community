{
    "name": "Daemon Key Manager",
    "version": "1.0",
    "summary": "Generalized, Open Source API Key Vault and File Writer for External Daemons",
    "category": "Security",
    "author": "Bruce Perens K6BP",
    "license": "AGPL-3",
    "depends": ["base", "zero_sudo"],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/registry_views.xml",
    ],
    "knowledge_docs": [
        {
            "name": "Daemon Key Manager Documentation",
            "path": "daemon_key_manager/LLM_DOCUMENTATION.md",
            "icon": "🔑",
            "category": "workspace"
        }
    ],
    "installable": True,
    "application": False,
}
