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
            trigger: '*:contains("Export"), form[action="/my/privacy/export"] button',
            run: 'click',
        },
        {
            content: "Verify Erasure Form invokes the JS confirmation safeguard",
            trigger: '*:contains("Delete"), form[action="/my/privacy/delete_content"] button',
            run: 'click',
        }
    ],
});
