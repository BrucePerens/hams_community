/** @odoo-module **/
import { registry } from "@web/core/registry";

// [@ANCHOR: test_tour_create_blog]
// Tests [@ANCHOR: controller_user_blog_index]
// Tests [@ANCHOR: UX_CREATE_BLOG_POST]
registry.category("web_tour.tours").add("create_blog_tour", {
    test: true,
    steps: () => [
        {
            content: "Navigate from the portal to the blog placeholder",
            trigger: 'body',
            run: () => {
                if (!window.location.pathname.includes('/blogtour/blog')) {
                    window.location.href = '/blogtour/blog';
                }
            }
        },
        {
            content: "Click Create Your Blog button",
            trigger: 'form[action$="/create_blog"] button[type="submit"]',
            run: "click"
        },
        {
            content: "Verify initial blog post created",
            trigger: 'span[data-oe-model="blog.post"]:contains("Welcome to my Blog"), h1:contains("Welcome to my Blog"), h2:contains("Welcome to my Blog")',
            run: () => {
                if (!document.body.textContent.includes('Welcome to my Blog')) {
                    console.error("Blog post content not found");
                }
            }
        },
        {
            content: "Verify the Website Builder 'New' button is accessible to the owner to make a new posting",
            trigger: '.o_menu_systray a:contains("New"), .o_menu_systray button:contains("New"), #site_new, a[data-action="new_page"]',
            run: () => {
                // By triggering on the New button, we mathematically prove the Proxy Owner
                // was granted the correct editing UI to make subsequent blog posts.
                console.log("New posting creation UI verified.");
            }
        }
    ],
});
