/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_frontend_misc]
registry.category("web_tour.tours").add("frontend_misc_tour", {
    url: "/user-websites/documentation",
    steps: () => [
        {
            content: "Verify Documentation Page renders correctly",
            trigger: 'body',
            run: () => {}
        }
    ],
});
