/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_cf_ip_ban]
// Tests [%ANCHOR: cf_ip_ban_ui]
registry.category("web_tour.tours").add("cf_ip_ban_tour", {
    test: true,
    url: "/web",
    steps: () => [
        {
            content: "Open App Switcher (if needed) or click Cloudflare Edge",
            trigger: '.o_app[data-menu-xmlid="cloudflare.menu_cloudflare_root"], .o_menu_brand:contains("Cloudflare Edge")',
            run: "click"
        },
        {
            content: "Open IP Bans Menu",
            trigger: 'a[data-menu-xmlid="cloudflare.menu_cf_ip_bans"]',
            run: "click"
        },
        {
            content: "Check if ban record exists in the list view",
            trigger: 'tr.o_data_row td:contains("192.168.9.9")',
            run: () => {} // Assert presence
        },
        {
            content: "Click on the IP Ban record to open form view",
            trigger: 'tr.o_data_row td:contains("192.168.9.9")',
            run: "click"
        },
        {
            content: "Verify Lift Ban button is rendered",
            trigger: 'button[name="action_lift_ban"]',
            run: () => {} // Assert presence
        }
    ],
});
