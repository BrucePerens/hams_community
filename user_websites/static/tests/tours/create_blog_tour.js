/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("create_blog_tour", {
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
            trigger: '*:contains("Create")',
            run: 'click',
        },
        {
            content: "Verify blog created",
            trigger: '#wrap',
            run: () => {},
        }
    ],
});
