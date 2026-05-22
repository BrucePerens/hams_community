/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// [@ANCHOR: test_tour_moderation_appeal]
// Tests [@ANCHOR: UX_SUBMIT_APPEAL]
registry.category("web_tour.tours").add("moderation_appeal_tour", {
    url: "/my/home",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        TourUtils.waitForElement('body', 'Verify Suspension Alert'),
        TourUtils.waitForRPC()
    ],
});
