/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click, edit } from "@odoo/hoot-dom";

// Tests [@ANCHOR: story_manual_search]
// [@ANCHOR: test_tour_manual_search]
// Tests [@ANCHOR: controller_manual_search]
describe("Manual Search Tour", () => {
    test("manual_search_tour", async () => {
        await edit("Odoo", 'input[name="search"]');
        await click('button[aria-label="Submit search"]');
        expect('*:contains("Search Results for:")').toHaveCount(1);
    });
});
