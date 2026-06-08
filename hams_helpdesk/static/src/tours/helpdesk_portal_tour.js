/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@zero_sudo/js/tour_utils";

registry.category("web_tour.tours").add("helpdesk_portal_tour", {
    url: "/my/tickets?debug=1",
    steps: () => [
        {
            content: "Click on New Ticket",
            trigger: '.o_tour_new_ticket',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Fill Subject",
            trigger: 'input[name="name"]',
            run: 'edit Tour Ticket',
        },
        {
            content: "Fill Description",
            trigger: 'textarea[name="description"]',
            run: 'edit This is a ticket created by a tour.',
        },
        {
            content: "Blur inputs to prevent RPC abort during navigation",
            trigger: '#wrapwrap',
            run: 'click',
        },
        {
            content: "Submit Ticket",
            trigger: 'button[type="submit"]',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Wait for Detail Page",
            trigger: '.breadcrumb-item.active',
            run: function() {},
        },
        {
            content: "Close Ticket",
            trigger: '.o_tour_close_ticket',
            run: 'click',
            expectUnloadPage: true,
        },
        {
            content: "Verify Closed Status via native polling",
            trigger: 'body',
            run: function() {
                return new Promise((resolve, reject) => {
                    let interval = setInterval(() => {
                        const badges = document.querySelectorAll('span.badge');
                        for (const badge of badges) {
                            if (badge.textContent.trim() === 'Closed') {
                                clearInterval(interval);
                                resolve();
                                return;
                            }
                        }
                    }, 250);
                    setTimeout(() => {
                        clearInterval(interval);
                        reject(new Error("Ticket status is not Closed"));
                    }, 10000);
                });
            }
        }
    ]
});
