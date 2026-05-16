/** @odoo-module **/
import { registry } from "@web/core/registry";

// Verified by [@ANCHOR: test_seo_widget_tour]
registry.category("web_tour.tours").add("user_websites_seo_tour", {
    url: '/my',
    steps: () => [
        {
            trigger: 'body',
            content: 'Verify body loaded',
            run: "click",
        }
    ],
});
