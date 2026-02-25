/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_cf_waf_rule]
// Tests [%ANCHOR: cf_waf_rule_ui]
registry.category("web_tour.tours").add("cf_waf_rule_tour", {
    test: true,
    url: "/web",
    steps: () => [
        {
            content: "Open Cloudflare Edge Menu",
            trigger: '.o_app[data-menu-xmlid="cloudflare.menu_cloudflare_root"], .o_menu_brand:contains("Cloudflare Edge")',
            run: "click"
        },
        {
            content: "Open WAF Rules Menu",
            trigger: 'a[data-menu-xmlid="cloudflare.menu_cf_waf_rules"]',
            run: "click"
        },
        {
            content: "Check if Tour WAF rule exists in list",
            trigger: 'tr.o_data_row td:contains("Tour XML-RPC Rule")',
            run: () => {} // Assert presence
        }
    ],
});
