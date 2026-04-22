/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("binary_install_tour", {
    url: "/web?debug=1",
    steps: () => [
        {
            trigger: '.o_navbar_apps_menu button',
            run: 'click',
        },
        {
            trigger: '[data-menu-xmlid="base.menu_administration"], a[data-menu-xmlid="base.menu_administration"]',
            content: "Click on Settings",
            run: "click",
        },
        {
            trigger: 'span:contains("Technical"), [data-menu-xmlid="base.menu_custom"]',
            content: "Open Technical menu",
            run: "click",
        },
        {
            trigger: 'a:contains("Binary Manifests"), [data-menu-xmlid="binary_downloader.menu_binary_downloader_manifest"]',
            content: "Go to Binary Manifests",
            run: "click",
        },
        {
            trigger: '.o_list_button_add',
            content: "Create a new manifest",
            run: "click",
        },
        {
            trigger: 'div[name="name"] input',
            content: "Enter binary name",
            run: "edit tourbin",
        },
        {
            trigger: 'div[name="url"] input',
            content: "Enter download URL",
            run: "edit [http://example.com/tourbin](http://example.com/tourbin)",
        },
        {
            trigger: 'div[name="checksum"] input',
            content: "Enter checksum",
            run: "edit tourhash",
        },
        {
            trigger: '.o_form_button_save',
            content: "Save the manifest",
            run: "click",
        },
        {
            trigger: 'button[name="action_install"]',
            content: "Click Install Now",
            run: "click",
        },
        {
            trigger: 'body',
            content: "Verify success notification",
            run: () => {},
        },
    ],
});
