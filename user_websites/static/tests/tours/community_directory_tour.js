/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";

// [@ANCHOR: test_tour_community_directory]
// Tests [@ANCHOR: UX_COMMUNITY_DIRECTORY]
describe("Community Directory Tour", () => {
    test("community_directory_tour", async () => {
        expect('*:contains("Community Directory")').toHaveCount(1);
    });
});
