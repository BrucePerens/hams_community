/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// [@ANCHOR: test_tour_toast_notifications]
// Tests [@ANCHOR: toast_notifications_logic]
registry.category("web_tour.tours").add("toast_notifications_tour", {
    url: "/?report_submitted=1",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        TourUtils.waitForElement('.o_notification_manager .o_notification', 'Check that the success toast notification is pushed to the DOM'),
        TourUtils.waitForRPC()
    ],
});
