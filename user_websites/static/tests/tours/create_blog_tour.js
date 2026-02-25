/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_create_blog]
// Tests [%ANCHOR: controller_user_blog_index]
// Tests [%ANCHOR: controller_create_blog_post]
registry.category("web_tour.tours").add("create_blog_tour", {
    test: true,
    steps: () => [
        {
            content: "Click Create Your Blog button",
            trigger: 'form[action$="/create_blog"] button[type="submit"]',
            run: "click"
        },
        {
            content: "Verify blog post created",
            trigger: 'span[data-oe-model="blog.post"]:contains("Welcome to my Blog"), h1:contains("Welcome to my Blog"), h2:contains("Welcome to my Blog")',
            run: () => {}
        }
    ],
});
