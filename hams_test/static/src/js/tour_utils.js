/** @odoo-module **/

/**
 * Centralized macros for Odoo UI Tours to guarantee architectural compliance.
 * Stripped of legacy jQuery and MutationObserver polyfills, and redundant wait macros.
 */
export const TourUtils = {
    safeSave: function (saveButtonTrigger, waitTrigger) {
        saveButtonTrigger = saveButtonTrigger || '.o_form_button_save';
        waitTrigger = waitTrigger || '.o_form_button_create';
        return [
            {
                content: "[MACRO] Click the save button",
                trigger: saveButtonTrigger,
                run: 'click',
            },
            {
                content: "[MACRO] Wait for DOM element: RPC resolution / Dirty Form safe save (" + waitTrigger + ")",
                trigger: waitTrigger,
                run: function() {}
            }
        ];
    },

    bypassDialogs: function () {
        return {
            content: "[MACRO] Bypass native blocking dialogs",
            trigger: 'body',
            run: function () {
                window.alert = function (msg) {
                    console.warn("[ALARM] Native window.alert intercepted and bypassed! Message: " + msg);
                };
                window.confirm = function (msg) {
                    console.warn("[ALARM] Native window.confirm intercepted and bypassed! Message: " + msg);
                    return true;
                };
            }
        };
    },

    mockExternalRequests: function (urlPattern, mockResponse) {
        return {
            content: "[MACRO] Mock external requests for " + urlPattern,
            trigger: 'body',
            run: function () {
                const originalFetch = window.fetch;
                window.fetch = async function (...args) {
                    const url = typeof args[0] === 'string' ? args[0] : (args[0] ? args[0].url : '');
                    if (url.includes(urlPattern)) {
                        return new Response(JSON.stringify(mockResponse), { status: 200 });
                    }
                    return originalFetch.apply(this, args);
                };
            }
        };
    },

    waitForAbsence: function (selector, description) {
        description = description || "";
        return {
            content: "[MACRO] Wait for DOM absence: " + (description || selector),
            trigger: 'body:not(:has(' + selector + '))',
            run: function () {}
        };
    }
};
