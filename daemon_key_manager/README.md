# Daemon Key Manager (`daemon_key_manager`)

An Open Source, generalized utility that manages Odoo API Keys for external background daemons.
It removes the need to store static passwords in repository code or manually rotate tokens by generating native Odoo API keys and exporting them to highly restricted local `.env` files.

## Integration API
Other modules can request a bearer token and configure a file drop path during their installation or upon configuration:

```python
def setup_daemon_credentials(env):
    env['daemon.key.registry'].register_daemon(
        daemon_name="My External Daemon",
        user_xml_id="my_module.my_service_account",
        env_file_path="/var/lib/odoo/daemon_keys/my_daemon.env"
    )
```

## Security Design
* **OS-Level Sandboxing:** The `.env` files are written with strict `chmod 0600` permissions.
* **Auto-Rotation:** An `ir.cron` job automatically revokes and regenerates the keys every 60 days, pushing the new credentials to the designated `.env` files automatically. Daemons utilizing these files simply need to reload their environment variables upon detecting an `AccessError` via JSON-RPC.
