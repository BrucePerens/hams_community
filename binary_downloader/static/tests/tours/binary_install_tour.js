/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click, edit } from "@odoo/hoot-dom";

describe("Binary Install Tour", () => {
    test("binary_install_tour", async () => {
        await click('.o_navbar_apps_menu button');
        await click('[data-menu-xmlid="base.menu_administration"], a[data-menu-xmlid="base.menu_administration"]');
        await click('[data-menu-xmlid="base.menu_custom"]');
        await click('[data-menu-xmlid="binary_downloader.menu_binary_downloader_manifest"]');
        await click('.o_list_button_add');

        await edit("tourbin", 'div[name="name"] input');
        await edit("[http://example.com/tourbin](http://example.com/tourbin)", 'div[name="url"] input');
        await edit("tourhash", 'div[name="checksum"] input');

        await click('.o_form_button_save');
        await click('button[name="action_install"]');

        // Verify success notification
        expect('body').toHaveCount(1);
    });
});
