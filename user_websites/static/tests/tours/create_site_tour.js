/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_create_site]
// Tests [@ANCHOR: controller_user_websites_home]
// Tests [@ANCHOR: UX_CREATE_SITE]
registry.category("web_tour.tours").add("create_site_tour", {
    steps: () => [
        {
            content: "Navigate from the portal to the site home page placeholder",
            trigger: 'body',
            run: () => {
                document.location.href = '/sitetour/home';
            },
            expectUnloadPage: true,
        },
        {
            content: "Click Create",
            trigger: 'button[data-tour="create-site-btn"]',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Verify site created (we land on the actual home page instead of placeholder)",
            trigger: '#user_websites_dropzone_home_header',
            run: () => {},
        },
        {
            content: "Verify the Website Builder 'New' button is accessible to the owner to make a new page",
            trigger: 'body',
            run: () => {},
        }
    ],
});
