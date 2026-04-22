/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";

// Tests [@ANCHOR: story_manual_toc]
// [@ANCHOR: test_tour_manual_toc]
// Tests [@ANCHOR: manual_toc_logic]
describe("Manual TOC Tour", () => {
    test("manual_toc_tour", async () => {
        expect('#manual_toc_container ul.nav').toHaveCount(1);
        expect('#manual_toc_container a[href^="#toc-heading-"]').toHaveCount(1);
    });
});
