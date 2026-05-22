/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// Tests [@ANCHOR: user_websites:UX_REPORT_VIOLATION]
registry.category("web_tour.tours").add("test_tour_violation_report", {
    url: "/",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        {
            trigger: 'a[data-bs-target="#reportViolationModal"]',
            content: "Open violation reporting modal",
            run: "click",
        },
        {
            trigger: '.o_select_menu[name="reason"]',
            content: "Click to open the custom Odoo 19 select dropdown menu",
            run: "click",
        },
        TourUtils.clickElement('.o_select_menu_item:contains("Spam")', "Select the specific menu option item"),
        {
            trigger: 'textarea[name="description"]',
            content: "Provide description notes using correct Odoo 19 input simulator",
            run: "edit Unsolicited advertising links.",
        },
        {
            trigger: 'button[type="submit"].btn-danger',
            content: "Submit violation ticket",
            run: "click",
        },
        TourUtils.waitForAbsence('.modal.show', 'Wait for submission modal to close'),
        TourUtils.waitForRPC()
    ]
});
