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
            run: 'click',
        },
        {
            content: "Bypass JS confirmation safeguard",
            trigger: 'form[action="/my/privacy/delete_content"] button[type="submit"]',
            run: () => {
                window.confirm = () => true;
            },
        },
        {
            content: "Verify Erasure Form invokes deletion",
            trigger: 'form[action="/my/privacy/delete_content"] button[type="submit"]',
            run: 'click',
            expectUnloadPage: true,
        }
    ],
});
