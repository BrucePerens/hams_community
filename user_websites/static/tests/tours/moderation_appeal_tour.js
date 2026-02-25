/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_moderation_appeal]
// Tests [%ANCHOR: controller_submit_appeal]
registry.category("web_tour.tours").add("moderation_appeal_tour", {
    test: true,
    url: "/my/home",
    steps: () => [
        {
            content: "Verify Suspension Alert",
            trigger: '.alert-danger h4:contains("Account Suspended")',
            run: () => {}
        },
        {
            content: "Fill out the Appeal Reason",
            trigger: 'textarea[name="reason"]',
            run: 'edit I apologize for my actions and will comply.'
        },
        {
            content: "Submit Appeal",
            trigger: 'form[action="/website/submit_appeal"] button[type="submit"]',
            run: 'click'
        },
        {
            content: "Check Pending Status Rendered",
            trigger: 'p:contains("You have a pending appeal under review")',
            run: () => {}
        }
    ],
});
