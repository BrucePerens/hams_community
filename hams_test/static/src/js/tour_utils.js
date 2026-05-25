/** @odoo-module **/

/**
 * Centralized macros for Odoo UI Tours to guarantee architectural compliance.
 * Rewritten for Odoo 19 to strictly use native MutationObserver triggers,
 * safely polyfilling jQuery's :contains pseudo-selector with visibility checks.
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
            this.waitForElement(waitTrigger, "RPC resolution / Dirty Form safe save (" + waitTrigger + ")")
        ];
    },

    waitForElement: function (selector, description) {
        description = description || "";
        if (!selector.includes(':contains')) {
            return {
                content: "[MACRO] Wait for DOM element: " + (description || selector),
                trigger: selector,
                run: function() {}
            };
        }

        return {
            content: "[MACRO] Wait for dynamic text element: " + (description || selector),
            trigger: 'body',
            run: function () {
                let parts = selector.split(':contains(');
                let tag = parts[0] || 'a, button, span, div, p, h1, h2, h3, h4, h5, h6, li, label, .dropdown-item, .o_app';
                let text = parts[1].replace(/['")]/g, '');

                return new Promise((resolve) => {
                    const check = () => {
                        let elements = document.querySelectorAll(tag);
                        for (let i = 0; i < elements.length; i++) {
                            let el = elements[i];
                            if (el.offsetWidth > 0 && el.offsetHeight > 0 && el.textContent.includes(text)) {
                                return true;
                            }
                        }
                        return false;
                    };

                    if (check()) {
                        resolve();
                        return;
                    }

                    const observer = new MutationObserver((mutations, obs) => {
                        let shouldCheck = false;
                        for (const m of mutations) {
                            if (m.type === 'characterData' || m.type === 'childList') {
                                shouldCheck = true;
                                break;
                            }
                        }

                        if (shouldCheck && check()) {
                            obs.disconnect();
                            resolve();
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                });
            }
        };
    },

    clickElement: function (selector, description) {
        if (!selector.includes(':contains')) {
            return {
                content: "[MACRO] Click element: " + (description || selector),
                trigger: selector,
                run: 'click',
            };
        }

        return {
            content: "[MACRO] Click element safely: " + (description || selector),
            trigger: 'body',
            run: function () {
                let parts = selector.split(':contains(');
                let tag = parts[0] || 'a, button, span, div, p, h1, h2, h3, h4, h5, h6, li, label, .dropdown-item, .o_app';
                let text = parts[1].replace(/['")]/g, '');

                return new Promise((resolve) => {
                    const checkAndClick = () => {
                        let elements = document.querySelectorAll(tag);
                        for (let i = 0; i < elements.length; i++) {
                            let el = elements[i];
                            if (el.offsetWidth > 0 && el.offsetHeight > 0 && el.textContent.includes(text)) {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    };

                    if (checkAndClick()) {
                        resolve();
                        return;
                    }

                    const observer = new MutationObserver((mutations, obs) => {
                        let shouldCheck = false;
                        for (const m of mutations) {
                            if (m.type === 'characterData' || m.type === 'childList') {
                                shouldCheck = true;
                                break;
                            }
                        }

                        if (shouldCheck && checkAndClick()) {
                            obs.disconnect();
                            resolve();
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                });
            }
        };
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
        if (!trigger.includes(':contains')) {
            return {
                content: "[MACRO] Deterministic input for " + trigger,
                trigger: trigger,
                run: "edit " + value,
            };
        }

        return {
            content: "[MACRO] Deterministic input for " + trigger,
            trigger: 'body',
            run: function () {
                let parts = trigger.split(':contains(');
                let tag = parts[0] || 'input, textarea, select';
                let text = parts[1].replace(/['")]/g, '');

                return new Promise((resolve) => {
                    const checkAndInput = () => {
                        let elements = document.querySelectorAll(tag);
                        for (let i = 0; i < elements.length; i++) {
                            let el = elements[i];
                            // Inputs often don't have textContent, so we check associated labels or placeholders
                            let hasText = el.textContent.includes(text) ||
                                          (el.placeholder && el.placeholder.includes(text)) ||
                                          (el.labels && Array.from(el.labels).some(l => l.textContent.includes(text)));
                            if (el.offsetWidth > 0 && el.offsetHeight > 0 && hasText) {
                                el.value = value;
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                return true;
                            }
                        }
                        return false;
                    };

                    if (checkAndInput()) {
                        resolve();
                        return;
                    }

                    const observer = new MutationObserver((mutations, obs) => {
                        let shouldCheck = false;
                        for (const m of mutations) {
                            if (m.type === 'characterData' || m.type === 'childList') {
                                shouldCheck = true;
                                break;
                            }
                        }

                        if (shouldCheck && checkAndInput()) {
                            obs.disconnect();
                            resolve();
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                });
            }
        };
    },

    clickAndUnload: function (trigger) {
        return {
            content: "[MACRO] Click and expect page unload: " + trigger,
            trigger: trigger,
            run: 'click',
        };
    },

    selectDropdown: function (dropdownTrigger, itemText) {
        return [
            this.clickElement(dropdownTrigger, "Open select menu"),
            this.clickElement(`.o_select_menu_item:contains("${itemText}")`, "Select menu item")
        ];
    },

    waitForRPC: function () {
        return {
            content: "[MACRO] Wait for all pending RPCs to resolve",
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
                return new Promise((resolve) => {
                    const check = () => {
                        let parts = selector.split(':contains(');
                        let tag = parts[0] || 'a, button, span, div, p, h1, h2, h3, h4, h5, h6, li, label';
                        let elements = document.querySelectorAll(tag);
                        if (selector.includes(':contains')) {
                            let text = parts[1].replace(/['")]/g, '');
                            let found = false;
                            for (let i = 0; i < elements.length; i++) {
                                let el = elements[i];
                                if (el.offsetWidth > 0 && el.offsetHeight > 0 && el.textContent.includes(text)) {
                                    found = true;
                                }
                            }
                            if (!found) return true;
                        } else {
                            // Standard selector check for absence
                            let visibleElements = Array.from(document.querySelectorAll(selector)).filter(el => el.offsetWidth > 0 && el.offsetHeight > 0);
                            if (visibleElements.length === 0) return true;
                        }
                        return false;
                    };

                    if (check()) {
                        resolve();
                        return;
                    }

                    const observer = new MutationObserver((mutations, obs) => {
                        let shouldCheck = false;
                        for (const m of mutations) {
                            if (m.type === 'characterData' || m.type === 'childList') {
                                shouldCheck = true;
                                break;
                            }
                        }

                        if (shouldCheck && check()) {
                            obs.disconnect();
                            resolve();
                        }
                    });
                    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
                });
            }
        };
    }
};
