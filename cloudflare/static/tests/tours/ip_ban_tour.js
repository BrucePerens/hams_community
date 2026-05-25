/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// [@ANCHOR: test_tour_cf_ip_ban]
registry.category("web_tour.tours").add("cf_ip_ban_tour", {
    url: "/odoo?debug=1",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        {
            content: 'Open App Switcher Dropdown',
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
        {
            content: "Click Cloudflare Edge App",
            trigger: '[data-menu-xmlid="cloudflare.menu_cloudflare_root"]',
            run: 'click',
        },
        {
            content: "Open IP Bans Menu",
            trigger: 'a[data-menu-xmlid="cloudflare.menu_cf_ip_bans"]',
            run: "click"
        },
        TourUtils.clickElement('tr.o_data_row td:contains("192.168.9.9")', "Wait for and click on the IP Ban record to open form view"), // hams-ignore-dynamic-text,
        { trigger: 'button[name="action_lift_ban"]', content: 'Wait for: Verify Lift Ban button is rendered', run: function() {} },
        
    ],
});
