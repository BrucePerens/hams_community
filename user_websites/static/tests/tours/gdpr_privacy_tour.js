/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_gdpr_privacy]
// Tests [%ANCHOR: controller_my_privacy_dashboard]
// Tests [%ANCHOR: controller_export_user_data]
// Tests [%ANCHOR: controller_delete_user_content]
registry.category("web_tour.tours").add("gdpr_privacy_tour", {
    test: true,
    url: "/my/privacy",
    steps: () => [
        {
            content: "Verify Privacy Dashboard Header",
            trigger: 'h2:contains("Privacy & Data Management")',
            run: () => {}
        },
        {
            content: "Verify Export Data Button is properly wired",
            trigger: 'form[action="/my/privacy/export"] button[type="submit"]',
            run: () => {}
        },
        {
            content: "Verify Erasure Form invokes the JS confirmation safeguard",
            trigger: 'form[action="/my/privacy/delete_content"][onsubmit*="return confirm"] button[type="submit"]',
            run: () => {}
        }
    ],
});
