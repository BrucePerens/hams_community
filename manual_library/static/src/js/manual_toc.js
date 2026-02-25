/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * ManualTOC Widget
 * * Adheres strictly to the project mandate forbidding jQuery in new frontend assets.
 * Uses Vanilla JS to dynamically scan the article body for headings and 
 * generates a sticky Table of Contents.
 */
publicWidget.registry.ManualTOC = publicWidget.Widget.extend({
    selector: '.o_manual_body',
    
    start: function () {
        this._super.apply(this, arguments);
        
        const tocContainer = document.getElementById('manual_toc_container');
        if (!tocContainer) {
            return;
        }
        
        // [%ANCHOR: manual_toc_logic]
        // Verified by [%ANCHOR: test_tour_manual_toc]
        // Scan only the manual body for relevant headings
        const headings = this.el.querySelectorAll('h2, h3');
        if (headings.length === 0) {
            return;
        }

        let tocHtml = '<h5 class="text-uppercase text-muted fs-6 tracking-wide mb-3 border-bottom pb-2">On this page</h5>';
        tocHtml += '<ul class="nav flex-column">';
        
        headings.forEach((heading, index) => {
            // Ensure the heading has an ID so the anchor link can target it
            const id = heading.id || 'toc-heading-' + index;
            heading.id = id;
            
            // Indent h3 tags for visual hierarchy
            const levelClass = heading.tagName.toLowerCase() === 'h2' ? 'ps-0 fw-bold' : 'ps-3';
            
            tocHtml += `
                <li class="nav-item">
                    <a class="nav-link text-muted py-1 ${levelClass}" href="#${id}">
                        ${heading.textContent}
                    </a>
                </li>
            `;
        });
        
        tocHtml += '</ul>';
        tocContainer.innerHTML = tocHtml;
    },
});

