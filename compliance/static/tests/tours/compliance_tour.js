/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("compliance_tour", {
    url: "/",
    test: true,
    steps: () => [
        {
            content: "Check if cookie bar is present",
            trigger: ".s_popup[data-v-cookie-bar]",
            run: () => {},
        },
        {
            content: "Click on Cookie Policy link in cookie bar",
            trigger: ".s_popup[data-v-cookie-bar] a[href='/cookie-policy']",
        },
        {
            content: "Verify Cookie Policy page title",
            trigger: "h1:contains('Cookie Policy')",
            run: () => {},
        },
        {
            content: "Navigate to Privacy Policy",
            trigger: "a[href='/privacy']",
        },
        {
            content: "Verify Privacy Policy page title",
            trigger: "h1:contains('Privacy Policy')",
            run: () => {},
        },
        {
            content: "Navigate to Terms of Service",
            trigger: "a[href='/terms']",
        },
        {
            content: "Verify Terms of Service page title",
            trigger: "h1:contains('Terms of Service')",
            run: () => {},
        }
    ],
});
