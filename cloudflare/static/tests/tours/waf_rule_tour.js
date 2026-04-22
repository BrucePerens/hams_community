/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

// [@ANCHOR: test_tour_cf_waf_rule]
describe("Cloudflare WAF Rule Tour", () => {
    test("cf_waf_rule_tour", async () => {
        await click('.o_navbar_apps_menu button');
        await click('[data-menu-xmlid="cloudflare.menu_cloudflare_root"], *:contains("Cloudflare Edge")');
        await click('[data-menu-xmlid="cloudflare.menu_cf_waf_rules"]');

        expect('tr.o_data_row *:contains("Tour XML-RPC Rule")').toHaveCount(1);
    });
});
