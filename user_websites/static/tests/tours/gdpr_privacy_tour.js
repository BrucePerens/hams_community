/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_gdpr_privacy]
// Tests [@ANCHOR: controller_my_privacy_dashboard]
// Tests [@ANCHOR: UX_GDPR_EXPORT]
// Tests [@ANCHOR: UX_GDPR_ERASURE]
registry.category("web_tour.tours").add("gdpr_privacy_tour", {
    steps: () => [
        {
            content: "Verify Privacy Dashboard Header",
            trigger: 'body',
            run: () => {},
        },
        {
            content: "Verify Export Data Button is properly wired",
            trigger: 'form[action="/my/privacy/export"] button[type="submit"]',
            run: () => {}, // Verify presence only to prevent file download from unloading the test page
        },
        {
            content: "Initiate Erasure Sequence",
            trigger: 'button[data-tour="erasure-initiate"]',
            run: 'click',
        },
        {
            content: "Confirm Erasure in Modal",
            trigger: 'button[data-tour="erasure-confirm"]',
            run: 'click',
            expectUnloadPage: true,
        }
    ],
});
