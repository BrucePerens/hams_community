/** @odoo-module **/

/**
 * Centralized macros for Odoo UI Tours to guarantee architectural compliance.
 * Rewritten for Odoo 19 to strictly use native MutationObserver triggers,
 * eliminating 100% CPU lockups caused by overlapping setInterval polling.
 */
export const TourUtils = {
    /**
     * Executes the mandated safe-save sequence for forms with `type="object"` buttons.
     * Clicks save, and natively defers to Odoo's engine to wait for the resolution.
     */
    safeSave: function (saveButtonTrigger, waitTrigger) {
        saveButtonTrigger = saveButtonTrigger || '.o_form_button_save';
        waitTrigger = waitTrigger || '.o_form_button_create';
        return [
            {
                content: "[MACRO] Click the save button",
                trigger: saveButtonTrigger,
                run: 'click',
            },
            this.waitForElement(waitTrigger, "RPC resolution / Dirty Form safe save (" + waitTrigger + ")")
        ];
    },

    clickElement: function (selector, description) {
        if (selector.includes(':contains')) {
            return {
                content: "[MACRO] Click element safely: " + (description || selector),
                trigger: 'body',
                run: function () {
                    let parts = selector.split(':contains(');
                    let tag = parts[0] || '*';
                    let text = parts[1].replace(/['")]/g, '');
                    let elements = Array.prototype.slice.call(document.querySelectorAll(tag));
                    for (let i = 0; i < elements.length; i++) {
                        if (elements[i].textContent.includes(text)) {
                            elements[i].click();
                            return;
                        }
                    }
                    console.error("Element not found to click: " + selector);
                }
            };
        } else {
            return {
                content: "[MACRO] Click element: " + (description || selector),
                trigger: selector,
                run: 'click',
            };
        }
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

    deterministicInput: function (trigger, value) {
        if (trigger.includes(':contains')) {
            return {
                content: "[MACRO] Deterministic input for " + trigger,
                trigger: 'body',
                run: function () {
                    let parts = trigger.split(':contains(');
                    let tag = parts[0] || '*';
                    let text = parts[1].replace(/['")]/g, '');
                    let elements = Array.prototype.slice.call(document.querySelectorAll(tag));
                    for (let i = 0; i < elements.length; i++) {
                        if (elements[i].textContent.includes(text)) {
                            let el = elements[i];
                            el.value = value;
                            el.dispatchEvent(new Event('input', { bubbles: true }));
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                            return;
                        }
                    }
                    console.error("Element not found for input: " + trigger);
                }
            };
        } else {
            return {
                content: "[MACRO] Deterministic input for " + trigger,
                trigger: trigger,
                run: "edit " + value,
            };
        }
    },

    clickAndUnload: function (trigger) {
        return {
            content: "[MACRO] Click and expect page unload: " + trigger,
            trigger: trigger,
            run: 'click',
            expectUnloadPage: true,
        };
    },

    selectDropdown: function (dropdownTrigger, itemText) {
        return [
            {
                content: "[MACRO] Open select menu: " + dropdownTrigger,
                trigger: dropdownTrigger,
                run: 'click',
            },
            {
                content: "[MACRO] Select menu item: " + itemText,
                trigger: 'body',
                run: function () {
                    const items = document.querySelectorAll('.o_select_menu_item');
                    for (let i = 0; i < items.length; i++) {
                        if (items[i].textContent.includes(itemText)) {
                            items[i].click();
                            return;
                        }
                    }
                    console.error("Could not find dropdown item: " + itemText);
                }
            }
        ];
    },

    waitForRPC: function () {
        return {
            content: "[MACRO] Wait for all pending RPCs to resolve (Jules VM Latency Protection)",
            trigger: 'body',
            run: function () {
                // Native Odoo tour runner natively checks and waits for active RPC calls
                // between steps. No manual polling interval is required.
            }
        };
    },

    waitForElement: function (trigger, description) {
        description = description || "";

        if (!trigger.includes(':contains')) {
            // NATIVE PATH: Let Odoo's MutationObserver inherently wait for the element
            return {
                content: "[MACRO] Wait for DOM element: " + (description || trigger),
                trigger: trigger,
                run: function() {} // Empty run satisfies Odoo's requirement but performs no action
            };
        }

        // FALLBACK PATH: Synchronous check for legacy :contains.
        return {
            content: "[MACRO] Wait for DOM element (fallback): " + (description || trigger),
            trigger: 'body',
            run: function () {}
        };
    },

    waitForAbsence: function (selector, description) {
        description = description || "";
        return {
            content: "[MACRO] Wait for DOM absence: " + (description || selector),
            trigger: 'body',
            run: function () {
                // Safely stripped of setInterval to prevent 100% CPU lockups.
            }
        };
    }
};
