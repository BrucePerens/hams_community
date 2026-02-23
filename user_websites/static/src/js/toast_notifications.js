/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * URL Toast Notification Widget
 * * Adheres to the requirement mandating Odoo's native notification bus for transient actions.
 * Listens for success parameters in the URL, fires a toast notification, 
 * and cleans the URL via history.replaceState to prevent duplicate triggers on refresh.
 */
publicWidget.registry.UrlToastNotification = publicWidget.Widget.extend({
    selector: '#wrapwrap', // Attach to the global wrapper so it runs on all frontend pages
    
    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this._checkUrlForNotifications();
    },

    _checkUrlForNotifications: function () {
        const urlParams = new URLSearchParams(window.location.search);
        let message = '';
        let title = '';
        let type = 'success'; 

        // Map URL query parameters to specific notification messages
        if (urlParams.has('report_submitted')) {
            title = "Success";
            message = "Your report has been submitted for review.";
        } else if (urlParams.has('appeal_submitted')) {
            title = "Submitted";
            message = "Your appeal has been received and is pending review.";
        } else if (urlParams.has('subscribed')) {
            title = "Subscribed";
            message = "You will now receive weekly email digests for this site.";
        } else if (urlParams.has('erased')) {
            title = "Content Deleted";
            message = "Your personal pages and blog posts have been permanently erased from our servers.";
        }

        if (message) {
            // Trigger Odoo's native notification bus
            this.call("notification", "add", message, {
                title: title,
                type: type,
                sticky: false,
            });
            
            // Clean up the URL to maintain a polished UX
            // We use replaceState so the user's back-button history is not affected
            const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.replaceState({path: newUrl}, '', newUrl);
        }
    },
});

