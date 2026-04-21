/** @odoo-module **/

import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("tours").add("zero_sudo_tour", {
    // [@ANCHOR: zero_sudo_tour]
    // Verified by [@ANCHOR: test_zero_sudo_tour]
    // Tests [@ANCHOR: story_login_blocking]
    // Tests [@ANCHOR: journey_service_account_lifecycle]
    url: "/web",
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
        },
        {
            trigger: '.o_menu_sections [data-menu-xmlid="base.menu_users"]',
        },
        {
            trigger: '.o_menu_sections [data-menu-xmlid="base.menu_action_res_users"]',
        },
        {
            trigger: '.o_list_button_add',
            content: "Create a new user",
        },
        {
            trigger: 'input[name="name"]',
            run: 'text Tour Service Account',
        },
        {
            trigger: 'input[name="login"]',
            run: 'text tour_service_account',
        },
        {
            trigger: 'div[name="is_service_account"] input',
            run: 'click',
        },
        {
            trigger: '.o_form_button_save',
            content: "Save the user",
        },
        {
            trigger: '.o_form_saved_indicator',
            isCheck: true,
        },
    ],
});
