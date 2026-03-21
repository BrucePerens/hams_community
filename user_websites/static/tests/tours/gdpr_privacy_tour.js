/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_gdpr_privacy]
// Tests [@ANCHOR: controller_my_privacy_dashboard]
// Tests [@ANCHOR: UX_GDPR_EXPORT]
// Tests [@ANCHOR: UX_GDPR_ERASURE]
registry.category("web_tour.tours").add("gdpr_privacy_tour", {
    test: true,
    url: "/my/privacy",
    steps: () => [
        {
            content: "Verify Privacy Dashboard Header",
            trigger: 'h2:contains("Privacy & Data Management")',
            run: () => {
                if (!document.querySelector('h2').textContent.includes('Privacy & Data')) {
                    console.error("Privacy header missing");
                }
            }
        },
        {
            content: "Verify Export Data Button is properly wired",
            trigger: 'form[action="/my/privacy/export"] button[type="submit"]',
            run: () => {
                if (!document.querySelector('form[action="/my/privacy/export"]')) {
                    console.error("Export form missing");
                }
            }
        },
        {
            content: "Verify Erasure Form invokes the JS confirmation safeguard",
            trigger: 'form[action="/my/privacy/delete_content"][onsubmit*="return confirm"] button[type="submit"]',
            run: () => {
                if (!document.querySelector('form[action="/my/privacy/delete_content"]').getAttribute('onsubmit').includes('return confirm')) {
                    console.error("Erasure confirmation missing");
                }
            }
        }
    ],
});
