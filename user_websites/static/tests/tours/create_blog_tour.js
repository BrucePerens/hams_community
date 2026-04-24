/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("create_blog_tour", {
    steps: () => [
        {
            content: "Navigate from the portal to the site blog page placeholder",
            trigger: 'body',
            run: () => {
                document.location.href = '/sitetour/blog';
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
            content: "Verify blog created (targeting invisible dropzone with native pseudo-selector)",
            trigger: '#user_websites_dropzone_home_header:not(:visible)',
            run: () => {},
        }
    ],
});
