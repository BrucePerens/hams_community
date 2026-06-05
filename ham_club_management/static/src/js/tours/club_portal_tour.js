/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ham_club_portal_tour", {
    url: "/my/clubs?debug=1",
    steps: () => [
        {
            content: "Check if My Club profile is loaded",
            trigger: 'body',
            run: function() {}
        }
    ]
});
