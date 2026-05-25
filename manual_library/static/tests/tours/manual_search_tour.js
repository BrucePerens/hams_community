/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// Tests [@ANCHOR: story_manual_search]
// Tests [@ANCHOR: test_tour_manual_search]
// Tests [@ANCHOR: controller_manual_search]
registry.category("web_tour.tours").add("manual_search_tour", {
    url: "/manual",
    steps: () => [
        {
            content: "Enter search term",
            trigger: 'input[name="search"]',
            run: 'edit Odoo'
        },
        TourUtils.clickAndUnload('button[aria-label="Submit search"]'),
        TourUtils.waitForElement('*:contains("Search Results for:")', 'Check results'), // hams-ignore-dynamic-text },
        
    ],
});
