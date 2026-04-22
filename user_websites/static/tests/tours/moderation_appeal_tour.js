/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("moderation_appeal_tour", {
    url: "/my/home",
    steps: () => [
        {
            content: "Verify Suspension Alert",
            trigger: 'body',
            run: () => {}
        }
    ],
});
