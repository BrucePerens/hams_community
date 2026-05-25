/** @odoo-module **/
import { registry } from "@web/core/registry";
import { TourUtils } from "@hams_test/js/tour_utils";

registry.category("web_tour.tours").add("daemon_key_manager_tour", {
    url: "/odoo?debug=1&action=daemon_key_manager.action_daemon_key_registry",
    steps: () => [
        { trigger: 'body', content: 'Initialize Tour' },
        {
            trigger: '.o_list_button_add',
            content: 'Create new registry entry',
            run: 'click',
        },
        {
            trigger: 'div[name="name"] input',
            content: 'Enter daemon name',
            run: 'edit TestDaemon',
        },
        {
            trigger: 'div[name="user_id"] input',
            content: 'Click to focus service account input',
            run: 'click',
        },
        {
            trigger: 'div[name="user_id"] input',
            content: 'Type service account name',
            run: 'edit facility',
        },
        {
            trigger: '.dropdown-item, .o-autocomplete--dropdown-item',
            content: 'Select the service account from OWL autocomplete',
            run: 'click',
        },
        {
            trigger: 'div[name="env_file_path"] input',
            content: 'Enter environment file path',
            run: 'edit /var/lib/odoo/daemon_keys/test.env',
        },
        {
            trigger: '.o_form_sheet',
            content: 'Click away to force DOM blur and commit text input',
            run: 'click',
        }
    ].concat(TourUtils.safeSave()).concat([
        {
            content: 'Dismiss old notifications to avoid race conditions',
            trigger: 'body',
            run: function () {
                const closers = document.querySelectorAll('.o_notification_close');
                closers.forEach(c => c.click());
            }
        },
        {
            content: 'Wait for the notification to physically leave the DOM after fade-out',
            trigger: 'body:not(:has(.o_notification))',
            run: function () {}
        },
        {
            trigger: 'button[name="action_force_provision_all"]:not([disabled])',
            content: 'Force provision all keys (ensuring button is active)',
            run: 'click',
        },
        {
            trigger: '.o_notification',
            content: 'Wait for NEW RPC resolution and notification to prevent dirty form crash',
            run: function () {}
        }
    ]),
});
