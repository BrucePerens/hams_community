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
            trigger: '[data-menu-xmlid="base.menu_custom"]',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="binary_downloader.menu_binary_downloader_manifest"]',
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
            run: 'edit http://example.com/tourbin',
        },
        {
            trigger: 'div[name="checksum"] input',
            run: 'edit tourhash',
        },
        {
            content: "Click Install Now",
            trigger: 'button[name="action_install"]',
            run: 'click',
        },
        {
            trigger: 'body',
            run: () => {},
        }
    ],
});
