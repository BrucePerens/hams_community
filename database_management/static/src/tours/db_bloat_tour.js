/** @odoo-module **/
import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("tours").add("db_management_bloat_tour", { // # Verified by [@ANCHOR: test_db_bloat_tour]
    url: "/web",
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="database_management.menu_admin_root"]',
        },
        {
            trigger: 'a[data-menu-xmlid="database_management.menu_db_tables"]',
        },
        {
            trigger: '.o_list_table',
            run: () => {}, // Wait for table to load
        },
        {
            trigger: '.o_list_button_add', // Just to prove we can see buttons, but we want to select an item
            run: () => {},
        },
        {
            trigger: 'tr.o_data_row',
            run: 'click',
        },
        {
            trigger: 'button[name="action_vacuum_analyze"]',
            run: 'click',
        },
    ],
});
