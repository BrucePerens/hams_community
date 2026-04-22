/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("user_websites_seo_tour", {
    url: '/seo-ui-test-user/blog',
    steps: () => [
        {
            trigger: 'body',
            content: 'Open Site Menu',
            run: () => {},
        }
    ],
});
