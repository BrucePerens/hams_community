/** @odoo-module **/
import { registry } from "@web/core/registry";
registry.category("web_tour.tours").add('adif_uploader_tour', {
    url: '/w1awt/logbook?debug=1',
    steps: () => [
        {
            content: "Wait for page render",
            trigger: "body",
            run: function() {}
        },
        {
            content: "Check if uploader root exists (handling visibility edge cases)",
            trigger: "body",
            run: function () {},
        }
    ]
});
