/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_moderation_appeal]
// Tests [@ANCHOR: UX_SUBMIT_APPEAL]
registry.category("web_tour.tours").add("moderation_appeal_tour", {
    test: true,
    url: "/my/home",
    steps: () => [
        {
            content: "Verify Suspension Alert",
            trigger: '.alert-danger h4:contains("Account Suspended")',
            run: () => {
                if (!document.querySelector('.alert-danger')) {
                    console.error("Suspension alert missing");
                }
            }
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
            trigger: 'p:contains("We are currently reviewing your appeal.")',
            run: () => {
                if (!document.body.textContent.includes('currently reviewing your appeal')) {
                    console.error("Appeal pending status missing");
                }
            }
        }
    ],
});
