/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

registry.category("web_tour.tours").add("helpdesk_portal_tour", {
    url: "/my/tickets",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        TourUtils.clickAndUnload('table tbody tr td a'),
        TourUtils.waitForElement('#optional_classes.container h3', 'Verify that the ticket detail page loaded successfully'),
        TourUtils.waitForElement('.o_portal_chatter', 'Verify the chatter is available'),
        TourUtils.waitForRPC()
    ],
});
