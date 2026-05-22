/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// [@ANCHOR: test_tour_cf_waf_rule]
registry.category("web_tour.tours").add("cf_waf_rule_tour", {
    url: "/odoo",
    steps: () => [
        {
            content: "Open Apps Menu",
            trigger: '.o_navbar_apps_menu button',
            run: "click"
        },
        {
            content: "Open Cloudflare Edge Menu",
            trigger: '[data-menu-xmlid="cloudflare.menu_cloudflare_root"], *:contains("Cloudflare Edge")',
            run: "click"
        },
        {
            content: "Open WAF Rules Menu",
            trigger: '[data-menu-xmlid="cloudflare.menu_cf_waf_rules"]',
            run: "click"
        },
        TourUtils.waitForElement('tr.o_data_row *:contains("Tour XML-RPC Rule")', 'Check if Tour WAF rule exists in list'),
        TourUtils.waitForRPC()
    ],
});
