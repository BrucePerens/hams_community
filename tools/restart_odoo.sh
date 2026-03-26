#!	/bin/bash
runuser -p -u odoo -- /opt/hams/.venv/bin/python /usr/bin/odoo -c /opt/hams/etc/odoo.conf -d hams_prod -u ham_onboarding --stop-after-init
systemctl restart odoo
