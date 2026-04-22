/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";
import { click, edit } from "@odoo/hoot-dom";

describe("Backup Dashboard", () => {
    test("backup_dashboard_tour", async () => {
        await click(".o_navbar_apps_menu button");
        await click('[data-menu-xmlid="backup_management.menu_admin_root"]');
        await click('[data-menu-xmlid="backup_management.menu_backup_root"]');
        await click('button[data-menu-xmlid="backup_management.menu_backup_config"], [data-menu-xmlid="backup_management.menu_backup_config"]');
        await click(".o_list_button_add");

        await edit("Test Kopia Tour", 'div[name="name"] input, input[id="name"]');
        await edit("kopia", 'div[name="engine"] select, select[id="engine"]');
        await edit("/var/lib/odoo/tour_repo", 'div[name="target_path"] input, input[id="target_path"]');

        await click(".o_form_button_save");

        // Verify saved
        expect(".o_breadcrumb, .o_form_button_create").toHaveCount(1);
    });
});
