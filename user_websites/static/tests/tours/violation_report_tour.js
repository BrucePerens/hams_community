/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_violation_report]
// Tests [%ANCHOR: violation_report_logic]
registry.category("web_tour.tours").add("violation_report_tour", {
    test: true,
    url: "/",
    steps: () => [
        {
            content: "Click the report violation button",
            trigger: 'button[data-bs-target="#reportViolationModal"]',
            run: "click",
        },
        {
            content: "Wait for modal to open and check URL field is populated",
            trigger: '#reportViolationModal.show input[name="url"]',
            run: () => {
                const val = document.querySelector('#reportViolationModal input[name="url"]').value;
                if (!val) {
                    console.error("URL field is empty! The JS logic failed to inject it.");
                }
            }
        }
    ],
});
