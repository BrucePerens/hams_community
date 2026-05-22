/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

registry.category("web_tour.tours").add("db_management_bloat_tour", { // # Verified by [@ANCHOR: test_db_bloat_tour]
    url: "/odoo?debug=1",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        {
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="database_management.menu_admin_root"]',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="database_management.menu_db_root"]',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="database_management.menu_db_tables"]',
            run: 'click',
        },
        TourUtils.waitForElement('.o_list_table', 'Wait for table to render'),
        {
            trigger: '.o_list_table .o_data_row .o_list_record_selector input',
            run: 'click',
        },
        TourUtils.clickElement('*:contains("Vacuum Analyze Selected")', "Vacuum Analyze Selected"),
        TourUtils.waitForRPC()
    ],
});
