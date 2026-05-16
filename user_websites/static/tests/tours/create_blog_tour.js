/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("create_blog_tour", {
    url: "/blogtour/blog",
    steps: () => [
        {
            content: "Click Create using namespaced fallback class",
            trigger: 'button.o_tour_create_site_btn',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Verify blog created by targeting the rendered blog index",
            trigger: '#o_wblog_index_content',
            run: () => {},
        }
    ],
});
