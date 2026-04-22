/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click } from "@odoo/hoot-dom";

describe("Create Blog Tour", () => {
    test("create_blog_tour", async () => {
        await click('*:contains("Create")');
        expect('#wrap').toHaveCount(1);
    });
});
