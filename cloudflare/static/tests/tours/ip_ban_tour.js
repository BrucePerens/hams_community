/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

// [@ANCHOR: test_tour_cf_ip_ban]
describe("Cloudflare IP Ban Tour", () => {
    test("cf_ip_ban_tour", async () => {
        await click('.o_navbar_apps_menu button');
        await click('[data-menu-xmlid="cloudflare.menu_cloudflare_root"], *:contains("Cloudflare Edge")');
        await click('a[data-menu-xmlid="cloudflare.menu_cf_ip_bans"]');

        expect('tr.o_data_row td:contains("192.168.9.9")').toHaveCount(1);

        await click('tr.o_data_row td:contains("192.168.9.9")');
        expect('button[name="action_lift_ban"]').toHaveCount(1);
    });
});
