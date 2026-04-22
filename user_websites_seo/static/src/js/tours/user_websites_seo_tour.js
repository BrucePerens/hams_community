/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("tours").add("user_websites_seo_tour", {
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
