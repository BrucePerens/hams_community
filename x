@@BOUNDARY_FIX_JS_TOURS@@
Path: cloudflare/static/tests/tours/waf_rule_tour.js
Operation: overwrite

/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_cf_waf_rule]
registry.category("web_tour.tours").add("cf_waf_rule_tour", {
    test: true,
    url: "/web",
    steps: () => [
        {
            content: "Open Cloudflare Edge Menu",
            trigger: '.o_app[data-menu-xmlid="cloudflare.menu_cloudflare_root"], .o_menu_brand:contains("Cloudflare Edge")',
            run: "click"
        },
        {
            content: "Open WAF Rules Menu",
            trigger: 'a[data-menu-xmlid="cloudflare.menu_cf_waf_rules"]',
            run: "click"
        },
        {
            content: "Check if Tour WAF rule exists in list",
            trigger: 'tr.o_data_row td:contains("Tour XML-RPC Rule")',
            run: () => {
                if (!document.querySelector('tr.o_data_row td')) {
                    console.error("WAF rule missing from DOM");
                }
            }
        }
    ],
});
@@BOUNDARY_FIX_JS_TOURS@@
Path: user_websites_seo/static/src/js/tours/user_websites_seo_tour.js
Operation: overwrite

/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("user_websites_seo_tour", {
    test: true,
    url: '/seo-ui-test-user/blog',
    steps: () => [
        {
            trigger: 'a[data-action="seo"]',
            content: 'Check for Optimize SEO menu item',
            run: 'click',
        },
        {
            trigger: '.modal-title:contains("Optimize SEO")',
            content: 'Wait for SEO modal to open',
            run: () => {},
        }
    ],
});
@@BOUNDARY_FIX_JS_TOURS@@
Path: zero_sudo/static/src/tours/zero_sudo_tour.js
Operation: overwrite

/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("zero_sudo_tour", {
    // [@ANCHOR: zero_sudo_tour]
    // Verified by [@ANCHOR: test_zero_sudo_tour]
    // Tests [@ANCHOR: story_login_blocking]
    // Tests [@ANCHOR: journey_service_account_lifecycle]
    url: "/web",
    steps: () => [
        {
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
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
@@BOUNDARY_FIX_JS_TOURS@@
Path: test_real_transaction/static/src/js/tours/test_real_transaction_tour.js
Operation: overwrite

/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("test_real_transaction_tour", {
    url: "/web",
    steps: () => [
        {
            trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            content: "Open Settings",
            run: "click",
        },
        {
            trigger: 'a.nav-link[data-menu-xmlid="base.menu_custom"]',
            content: "Open Technical Menu",
            run: "click",
        },
        {
            trigger: 'a.o_menu_entry_lvl_2[data-menu-xmlid="test_real_transaction.menu_noisy_table"]',
            content: "Open Noisy Tables",
            run: "click",
        },
        {
            trigger: ".o_list_button_add",
            content: "Click Create",
            run: "click",
        },
        {
            trigger: ".o_tour_trigger_noisy_table_name_form input",
            content: "Enter table name",
            run: "text tour_test_table",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save",
            run: "click",
        },
    ],
});
@@BOUNDARY_FIX_JS_TOURS@@--
