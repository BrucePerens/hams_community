/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_manual_search]
// Tests [%ANCHOR: controller_manual_search]
registry.category("web_tour.tours").add("manual_search_tour", {
    test: true,
    url: "/manual",
    steps: () => [
        {
            content: "Enter search term",
            trigger: 'input[name="search"]',
            run: 'edit Odoo'
        },
        {
            content: "Submit search",
            trigger: 'button[aria-label="Submit search"]',
            run: "click"
        },
        {
            content: "Check results",
            trigger: 'h2:contains("Search Results for:")',
            run: () => {}
        }
    ],
});
