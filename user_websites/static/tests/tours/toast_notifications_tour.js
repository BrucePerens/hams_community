/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_toast_notifications]
// Tests [@ANCHOR: toast_notifications_logic]
registry.category("web_tour.tours").add("toast_notifications_tour", {
    test: true,
    url: "/?report_submitted=1",
    steps: () => [
        {
            content: "Check that the success toast notification is pushed to the DOM",
            trigger: '.o_notification_manager .o_notification',
            run: () => {
                if (!document.querySelector('.o_notification')) {
                    console.error("Success notification missing");
                }
            }
        }
    ],
});
