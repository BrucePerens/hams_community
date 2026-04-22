/** @odoo-module **/
import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("db_management_slow_query_tour", { // # Verified by [@ANCHOR: test_db_slow_query_tour]
    url: "/web",
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="database_management.menu_admin_root"]',
        },
        {
            trigger: 'a[data-menu-xmlid="database_management.menu_db_queries"]',
        },
        {
            trigger: '.o_list_table',
            run: () => {},
        }
    ],
});
