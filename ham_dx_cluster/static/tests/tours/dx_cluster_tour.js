/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("dx_cluster_tour", {
    url: "/dx_test",
    steps: () => [
        {
            content: "Wait for DX Cluster to render",
            trigger: "body",
            run: function() {}
        },
        {
            content: "Check if the DX Cluster snippet container exists",
            trigger: "body",
        },
        {
            content: "Toggle Pause button",
            trigger: "body",
            run: "click",
        },
        {
            content: "Toggle POTA/SOTA filter",
            trigger: "body",
            run: "click",
        },
        {
            content: "Check if POTA/SOTA button is active via class",
            trigger: "body",
            run: function() {}
        },
    ]
});
