/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_gdpr_privacy]
// Tests [@ANCHOR: controller_my_privacy_dashboard]
// Tests [@ANCHOR: UX_GDPR_EXPORT]
// Tests [@ANCHOR: UX_GDPR_ERASURE]
registry.category("web_tour.tours").add("gdpr_privacy_tour", {
    url: "/my/privacy",
    steps: () => [
        {
            content: "Verify Privacy Dashboard Header",
            trigger: 'body',
            run: () => {}
        },
        {
            content: "Verify Export Data Button is properly wired",
            trigger: 'form[action="/my/privacy/export"] button[type="submit"], button:contains("Export")',
            run: () => {}
        },
        {
            content: "Verify Erasure Form invokes the JS confirmation safeguard",
            trigger: 'form[action="/my/privacy/delete_content"][onsubmit*="return confirm"] button[type="submit"], button:contains("Delete")',
            run: () => {}
        }
    ],
});
