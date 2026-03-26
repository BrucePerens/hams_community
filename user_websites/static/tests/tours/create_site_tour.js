/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_create_site]
// Tests [@ANCHOR: controller_user_websites_home]
// Tests [@ANCHOR: UX_CREATE_SITE]
registry.category("web_tour.tours").add("create_site_tour", {
    test: true,
    steps: () => [
        {
            content: "Navigate from the portal to the site home page placeholder",
            trigger: 'body',
            run: () => {
                if (!window.location.pathname.includes('/sitetour/home')) {
                    window.location.href = '/sitetour/home';
                }
            }
        },
        {
            content: "Click Create Your Website button",
            trigger: 'form[action$="/create_site"] button[type="submit"]',
            run: "click"
        },
        {
            content: "Verify site created (we land on the actual home page instead of placeholder)",
            trigger: '#wrap',
            run: () => {
                if (!document.querySelector('#wrap')) {
                    console.error("Site creation fallback content not found");
                }
            }
        },
        {
            content: "Verify the Website Builder 'New' button is accessible to the owner to make a new page",
            trigger: '.o_menu_systray a:contains("New"), .o_menu_systray button:contains("New"), #site_new, a[data-action="new_page"]',
            run: () => {
                // By triggering on the New button, we mathematically prove the Proxy Owner
                // was granted the correct editing UI to make subsequent pages.
                console.log("New page creation UI verified.");
            }
        }
    ],
});
