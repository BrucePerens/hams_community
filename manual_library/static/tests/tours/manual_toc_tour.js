/** @odoo-module **/
import { registry } from "@web/core/registry";

// [%ANCHOR: test_tour_manual_toc]
// Tests [%ANCHOR: manual_toc_logic]
registry.category("web_tour.tours").add("manual_toc_tour", {
    test: true,
    url: "/manual",
    steps: () => [
        {
            content: "Wait for the TOC container to render",
            trigger: '#manual_toc_container ul.nav',
            run: () => {}
        },
        {
            content: "Verify that a heading link was dynamically generated",
            trigger: '#manual_toc_container a.nav-link[href^="#toc-heading-"]',
            run: () => {}
        }
    ],
});
