/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_manual_feedback]
// Tests [@ANCHOR: controller_manual_feedback]
registry.category("web_tour.tours").add("manual_feedback_tour", {
    test: true,
    steps: () => [
        {
            content: "Click Helpful button",
            trigger: 'button[name="is_helpful"][value="1"]',
            run: "click"
        },
        {
            content: "Check success message",
            trigger: '.alert-success:contains("Thank you for your feedback!")',
            run: () => {
                if (!document.querySelector('.alert-success')) {
                    console.error("Feedback success alert did not render in the DOM.");
                }
            }
        }
    ],
});
