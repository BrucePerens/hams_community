/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("binary_install_tour", {
    url: "/web",
    steps: () => [
        {
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="base.menu_administration"]',
            run: 'click',
        },
        {
            trigger: '.o_settings_container, [data-menu-xmlid="base.menu_custom"], *:contains("Custom")',
            run: () => {},
        },
        {
            trigger: '[data-menu-xmlid="base.menu_custom"], *:contains("Custom")',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="binary_downloader.menu_binary_downloader_manifest"], *:contains("Binary Manifests")',
            run: 'click',
        },
        {
            trigger: '.o_list_button_add',
            run: 'click',
        },
        {
            trigger: 'div[name="name"] input',
            run: 'edit tourbin',
        },
        {
            trigger: 'div[name="url"] input',
            run: 'edit [https://example.com/tourbin](https://example.com/tourbin)',
        },
        {
            trigger: 'div[name="checksum"] input',
            run: 'edit tourhash',
        },
        {
            content: "Explicitly save the record to decouple input from RPC execution",
            trigger: '.o_form_button_save',
            run: 'click',
        },
        {
            content: "Wait for the database save to complete and the action button to appear",
            trigger: 'button[data-tour="install-now-btn"]',
            run: 'click',
        },
        {
            content: "Wait for the success notification to ensure the RPC resolved before ending tour",
            trigger: '.o_notification:contains("Success")',
            run: () => {},
        },
        {
            trigger: 'body',
            run: () => {},
        }
    ],
});
