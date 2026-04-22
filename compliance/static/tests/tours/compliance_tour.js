/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("compliance_tour", {
    url: "/",
    steps: () => [
        {
            content: "Click on Cookie Policy link in cookie bar",
            trigger: "#website_cookies_bar a[href='/cookie-policy']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Verify Cookie Policy page title",
            trigger: "*:contains('Cookie Policy')",
            run: () => {},
        },
        {
            content: "Navigate to Privacy Policy",
            trigger: "a[href='/privacy']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Verify Privacy Policy page title",
            trigger: "*:contains('Privacy Policy')",
            run: () => {},
        },
        {
            content: "Navigate to Terms of Service",
            trigger: "a[href='/terms']",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Verify Terms of Service page title",
            trigger: "*:contains('Terms of Service')",
            run: () => {},
        }
    ],
});
