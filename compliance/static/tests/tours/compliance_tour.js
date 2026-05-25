/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// # Verified by [@ANCHOR: test_compliance_ui_tour]
registry.category("web_tour.tours").add("compliance_tour", {
    url: "/privacy?debug=1",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        TourUtils.waitForElement("#wrap:contains('Privacy Policy')", 'Verify Privacy Policy content'), // hams-ignore-dynamic-text },
        TourUtils.waitForElement("#wrap:contains('Warning: This is the default version')", 'Verify Warning message presence'), // hams-ignore-dynamic-text },
        TourUtils.waitForElement("#wrap:contains('Data Minimization')", 'Verify Data Minimization section'), // hams-ignore-dynamic-text },
        TourUtils.waitForElement("#wrap:contains('Related')", 'Verify related links are present'), // hams-ignore-dynamic-text },
        { trigger: "a[href='/cookie-policy']", content: 'Wait for: Verify Cookie Policy link in related section', run: function() {} },
        { trigger: "a[href='/terms']", content: 'Wait for: Verify Terms of Service link in related section', run: function() {} },
        
    ],
});
