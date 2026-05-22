/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// Tests [@ANCHOR: story_manual_feedback]
// Tests [@ANCHOR: test_tour_manual_feedback]
// Tests [@ANCHOR: controller_manual_feedback]
registry.category("web_tour.tours").add("manual_feedback_tour", {
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        TourUtils.clickAndUnload('button[name="is_helpful"][value="1"]'),
        TourUtils.waitForElement('.alert-success:contains("Thank you for your feedback!")', 'Check success message'),
        TourUtils.waitForRPC()
    ],
});
