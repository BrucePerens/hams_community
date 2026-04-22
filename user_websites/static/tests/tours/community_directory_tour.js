/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_community_directory]
// Tests [@ANCHOR: UX_COMMUNITY_DIRECTORY]
registry.category("web_tour.tours").add("community_directory_tour", {
    test: true,
    url: "/community",
    steps: () => [
        {
            content: "Check that the directory page renders",
            trigger: '*:contains("Community Directory")',
            run: () => {
                if (!document.querySelector('h1').textContent.includes('Community Directory')) {
                    console.error("Directory header missing");
                }
            }
        }
    ],
});
