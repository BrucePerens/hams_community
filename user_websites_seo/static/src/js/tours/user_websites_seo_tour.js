/** @odoo-module **/
import tour from 'web_tour.tour';

tour.register('user_websites_seo_tour', {
    test: true,
    url: '/seo-ui-test-user/blog',
}, [
    {
        trigger: 'a[data-action="seo"]',
        content: 'Check for Optimize SEO menu item',
        run: 'click',
    },
    {
        trigger: '.modal-title:contains("Optimize SEO")',
        content: 'Wait for SEO modal to open',
        run: function() {},
    }
]);
