/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

describe("Compliance Tour", () => {
    test("compliance_tour", async () => {
        await click("#website_cookies_bar a[href='/cookie-policy']");
        expect("*:contains('Cookie Policy')").toHaveCount(1);

        document.location.href = '/privacy';
        expect("*:contains('Privacy Policy')").toHaveCount(1);

        document.location.href = '/terms';
        expect("*:contains('Terms of Service')").toHaveCount(1);
    });
});
