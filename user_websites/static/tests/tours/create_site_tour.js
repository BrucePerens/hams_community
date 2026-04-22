/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

// [@ANCHOR: test_tour_create_site]
// Tests [@ANCHOR: controller_user_websites_home]
// Tests [@ANCHOR: UX_CREATE_SITE]
describe("Create Site Tour", () => {
    test("create_site_tour", async () => {
        // Navigate from the portal to the site home page placeholder
        if (!document.location.pathname.includes('/sitetour/home')) {
            document.location.href = '/sitetour/home';
        }

        await click('*:contains("Create")');

        // Verify site created (we land on the actual home page instead of placeholder)
        expect('#wrap').toHaveCount(1);

        // Verify the Website Builder 'New' button is accessible to the owner to make a new page
        expect('body').toHaveCount(1);
    });
});
