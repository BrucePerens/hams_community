/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("create_blog_tour", {
    steps: () => [
        {
            content: "Click Create Your Blog button",
            trigger: '*:contains("Create")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Verify blog created",
            trigger: '#wrap',
            run: () => {}
        }
    ],
});
