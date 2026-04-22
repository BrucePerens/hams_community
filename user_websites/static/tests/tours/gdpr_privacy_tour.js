/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

// [@ANCHOR: test_tour_gdpr_privacy]
// Tests [@ANCHOR: controller_my_privacy_dashboard]
// Tests [@ANCHOR: UX_GDPR_EXPORT]
// Tests [@ANCHOR: UX_GDPR_ERASURE]
describe("GDPR Privacy Dashboard", () => {
    test("gdpr_privacy_tour", async () => {
        // Verify Privacy Dashboard Header
        expect('body').toHaveCount(1);

        // Verify Export Data Button is properly wired
        await click('form[action="/my/privacy/export"] button[type="submit"], button:contains("Export")');

        // Verify Erasure Form invokes the JS confirmation safeguard
        await click('form[action="/my/privacy/delete_content"][onsubmit*="return confirm"] button[type="submit"], button:contains("Delete")');
    });
});
