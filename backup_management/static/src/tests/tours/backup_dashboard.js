/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("backup_dashboard_tour", {
    url: "/web",
    steps: () => [
        {
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="backup_management.menu_admin_root"]',
            content: "Click on Backup Management app",
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="backup_management.menu_backup_root"]',
            content: "Click on Backups Submenu",
            run: 'click',
        },
        {
            trigger: 'button[data-menu-xmlid="backup_management.menu_backup_config"], [data-menu-xmlid="backup_management.menu_backup_config"]',
            content: "Open Configurations",
            run: 'click',
        },
        {
            trigger: ".o_list_button_add",
            content: "Create new configuration",
            run: 'click',
        },
        {
            trigger: 'div[name="name"] input, input[id="name"]',
            run: "edit Test Kopia Tour",
            content: "Enter name",
        },
        {
            trigger: 'div[name="engine"] select, select[id="engine"]',
            run: "text kopia",
            content: "Select Kopia engine",
        },
        {
            trigger: 'div[name="target_path"] input, input[id="target_path"]',
            run: "edit /var/lib/odoo/tour_repo",
            content: "Enter target path",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save configuration",
            run: "click",
        },
        {
            trigger: ".o_breadcrumb, .o_form_button_create",
            content: "Verify saved",
            run: () => {},
        }
    ],
});
