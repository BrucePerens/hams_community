/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("tours").add("backup_dashboard_tour", {
    url: "/web",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="backup_management.menu_backup_root"]',
            content: "Click on Backup Management app",
        },
        {
            trigger: 'button[data-menu-xmlid="backup_management.menu_backup_config"]',
            content: "Open Configurations",
        },
        {
            trigger: ".o_list_button_add",
            content: "Create new configuration",
        },
        {
            trigger: 'input[id="name"]',
            run: "text Test Kopia Tour",
            content: "Enter name",
        },
        {
            trigger: 'select[id="engine"]',
            run: "text kopia",
            content: "Select Kopia engine",
        },
        {
            trigger: 'input[id="target_path"]',
            run: "text /var/lib/odoo/tour_repo",
            content: "Enter target path",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save configuration",
        },
        {
            trigger: ".o_breadcrumb",
            content: "Verify saved",
        }
    ],
});
