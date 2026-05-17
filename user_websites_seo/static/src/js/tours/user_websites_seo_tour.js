/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

// Verified by [@ANCHOR: test_seo_widget_tour]
registry.category("web_tour.tours").add("user_websites_seo_tour", {
    url: "/web",
    steps: () => [
        {
            content: "Wait for the backend framework to initialize",
            trigger: '.o_home_menu_background, .o_form_sheet, .o_list_view',
        },
        {
            content: "Click the SEO Metadata notebook tab injected by our module",
            trigger: 'a[name="user_websites_seo_settings"]',
            run: 'click',
        },
        {
            content: "Verify SEO Meta Title input exists",
            trigger: 'div[name="website_meta_title"] input',
        },
        {
            content: "Verify SEO Meta Description input exists",
            trigger: 'div[name="website_meta_description"] input',
        }
    ],
});
