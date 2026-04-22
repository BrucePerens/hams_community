/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("user_websites_seo_tour", {
    test: true,
    url: '/seo-ui-test-user/blog',
    steps: () => [
        {
            trigger: '.o_menu_systray *:contains("Site")',
            content: 'Open Site Menu',
            run: 'click',
        },
        {
            trigger: 'a[data-action="seo"]',
            content: 'Check for Optimize SEO menu item',
            run: 'click',
        },
        {
            trigger: '.modal-title:contains("Optimize SEO"), *:contains("Optimize SEO")',
            content: 'Wait for SEO modal to open',
            run: () => {},
        }
    ],
});
