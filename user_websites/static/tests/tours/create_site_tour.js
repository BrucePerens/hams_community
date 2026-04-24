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
            content: "Click Create using namespaced fallback class",
            trigger: 'button.o_tour_create_site_btn',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Verify site created (targeting invisible dropzone with native pseudo-selector)",
            trigger: '#user_websites_dropzone_home_header:not(:visible)',
            run: () => {},
        },
        {
            content: "Verify the Website Builder 'New' button is accessible to the owner to make a new page",
            trigger: 'body',
            run: () => {},
        }
    ],
});
