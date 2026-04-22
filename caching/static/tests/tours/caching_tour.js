/** @odoo-module **/
import { describe, test, expect } from "@odoo/hoot";

describe("Caching Tour", () => {
    test("caching_service_worker_check", async () => {
        // Verified by [@ANCHOR: caching_sw_fetch_interceptor]
        console.log('Tour started');
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            if (registrations.length > 0) {
                console.log('Service Worker found');
                document.body.classList.add('sw-registered');
            } else {
                console.error('No Service Worker found');
                document.body.classList.add('sw-failed');
            }
        } else {
            console.error('Service Worker not supported');
            document.body.classList.add('sw-unsupported');
        }

        expect("body.sw-registered").toHaveCount(1);
    });
});
