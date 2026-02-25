/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_create_site]
// Tests [%ANCHOR: controller_user_websites_home]
// Tests [%ANCHOR: controller_create_site]
registry.category("web_tour.tours").add("create_site_tour", {
    test: true,
    steps: () => [
        {
            content: "Click Create Your Website button",
            trigger: 'form[action$="/create_site"] button[type="submit"]',
            run: "click"
        },
        {
            content: "Verify site created (we land on home page instead of placeholder)",
            trigger: 'p:contains("This is a new user website.")',
            run: () => {}
        }
    ],
});
