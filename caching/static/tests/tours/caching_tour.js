/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("caching_service_worker_check", {
    url: "/",
    steps: () => [
        {
            content: "Wait for page to load",
            trigger: "body",
        },
        {
            content: "Check if Service Worker is supported and registered",
            trigger: "body",
            run: function () {
                // Verified by [@ANCHOR: caching_sw_fetch_interceptor]
                console.log('Tour started');
                if ('serviceWorker' in navigator) {
                    navigator.serviceWorker.getRegistrations().then(registrations => {
                        if (registrations.length > 0) {
                            console.log('Service Worker found');
                            document.body.classList.add('sw-registered');
                        } else {
                            console.error('No Service Worker found');
                            document.body.classList.add('sw-failed');
                        }
                    });
                } else {
                    console.error('Service Worker not supported');
                    document.body.classList.add('sw-unsupported');
                }
            },
        },
        {
            content: "Wait for SW status to be updated",
            trigger: "body.sw-registered",
        }
    ],
});
