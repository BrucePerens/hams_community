#!/bin/bash
export PYTHONPATH="/usr/lib/python3/dist-packages:$PYTHONPATH"
./.venv/bin/python /usr/bin/odoo --addons-path="/usr/lib/python3/dist-packages/odoo/addons,." -d <YOUR_TEST_DB_NAME> -u user_websites --stop-after-init
