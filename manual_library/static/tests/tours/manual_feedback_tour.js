/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

// Tests [@ANCHOR: story_manual_feedback]
// [@ANCHOR: test_tour_manual_feedback]
// Tests [@ANCHOR: controller_manual_feedback]
describe("Manual Feedback Tour", () => {
    test("manual_feedback_tour", async () => {
        await click('button[name="is_helpful"][value="1"]');
        expect('.alert-success:contains("Thank you for your feedback!")').toHaveCount(1);
    });
});
