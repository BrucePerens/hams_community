/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_community_directory]
// Tests [%ANCHOR: controller_community_directory]
registry.category("web_tour.tours").add("community_directory_tour", {
    test: true,
    url: "/community",
    steps: () => [
        {
            content: "Check that the directory page renders",
            trigger: 'h1:contains("Community Directory")',
            run: () => {}
        }
    ],
});
