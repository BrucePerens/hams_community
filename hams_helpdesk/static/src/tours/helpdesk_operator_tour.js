/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@zero_sudo/js/tour_utils";

registry.category("web_tour.tours").add("helpdesk_operator_tour", {
    url: "/odoo?debug=1&action=hams_helpdesk.action_hams_helpdesk_ticket",
    steps: () => [
        {
            content: "Click Create Ticket",
            trigger: '.o_list_button_add',
            run: 'click',
        },
        {
            content: "Fill Subject",
            trigger: 'div[name="name"] input',
            run: 'edit Operator Tour Ticket',
        },
        {
            content: "Click away to blur",
            trigger: '.o_form_sheet',
            run: 'click',
        },
    ].concat(TourUtils.safeSave()).concat([
        {
            content: "Click Shift Handoff",
            trigger: 'button[name="action_shift_handoff"]',
            run: 'click',
        },
        {
            content: "Wait for Wizard",
            trigger: '.modal-body',
            run: function() {},
        },
        {
            content: "Select New User",
            trigger: 'div[name="new_user_id"] input',
            run: 'edit tour',
        },
        {
            content: "Pick First User",
            trigger: '.o-autocomplete--dropdown-item:first',
            run: 'click',
        },
        {
            content: "Force Blur for Wizard before confirmation",
            trigger: '.modal-body',
            run: 'click',
        },
        {
            content: "Fill Notes",
            trigger: 'div[name="handoff_notes"] textarea',
            run: 'edit Handing off for the night.',
        },
        {
            content: "Force Blur for Notes",
            trigger: '.modal-body',
            run: 'click',
        },
        {
            content: "Confirm Handoff",
            trigger: 'button[name="action_confirm_handoff"]:not([disabled])',
            run: 'click',
        },
        TourUtils.waitForAbsence('.modal', 'Wait for modal to close'),
        {
            content: "Wait for form to reload",
            trigger: '.o_form_sheet', // wait for form sheet to render first
            run: function() {}
        },
        {
            content: "Wait for Handoff message in chatter",
            trigger: 'body',
            run: function () {
                return new Promise((resolve) => {
                    function checkText(node, text) {
                        if (node.textContent && node.textContent.includes(text)) return true;
                        if (node.shadowRoot) {
                            if (checkText(node.shadowRoot, text)) return true;
                        }
                        for (let child of node.children || []) {
                            if (checkText(child, text)) return true;
                        }
                        return false;
                    }
                    const interval = setInterval(() => {
                        if (checkText(document.body, "Official Shift Handoff Executed")) {
                            clearInterval(interval);
                            resolve();
                        }
                    }, 250);
                });
            }
        },
        {
            content: "Final click to finish tour",
            trigger: '.o_form_sheet',
            run: 'click'
        }
    ])
});
