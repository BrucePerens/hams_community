/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_frontend_misc]
registry.category("web_tour.tours").add("frontend_misc_tour", {
    test: true,
    url: "/user-websites/documentation",
    steps: () => [
        {
            content: "Verify Documentation Page renders correctly",
            trigger: 'h1:contains("User Websites Module Documentation")',
            run: () => {}
        }
    ],
});
