{
    "name": "Daemon Key Manager",
    "version": "1.0",
    "summary": "Generalized, Open Source API Key Vault and File Writer for External Daemons",
    "category": "Security",
    "author": "Bruce Perens K6BP",
    "license": "AGPL-3",
    "depends": ["base", "zero_sudo"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
    ],
    "installable": True,
    "application": False,
}
