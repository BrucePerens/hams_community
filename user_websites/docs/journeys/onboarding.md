# Journey: First Time Site Setup

This journey describes the path a new user takes to establish their presence on the platform.

## Path: Onboarding and Creation

1. **Discovery**: The user navigates to the Community Directory ([@ANCHOR: UX_COMMUNITY_DIRECTORY]) to see what others have built.
2. **Accessing Profile**: The user clicks on their own name in the navbar or enters their slug directly (e.g., `/alice`).
3. **Routing**: The system resolves the slug and determines no site exists yet ([@ANCHOR: controller_user_websites_home]).
4. **Placeholder**: The user sees the placeholder page with the "Create My Site" call-to-action.
5. **Initialization**: The user clicks the button, triggering the `create_site` controller ([@ANCHOR: UX_CREATE_SITE]).
6. **Security Check**: The system verifies the user owns the slug and hasn't exceeded their page quota ([@ANCHOR: website_page_quota_check]).
7. **Provisioning**: The system creates the `website.page` record using a proxy service account ([@ANCHOR: mixin_proxy_ownership_create]).
8. **Redirect**: The user is redirected to their live home page, now ready for customization.

## Path: Starting a Blog

1. **Blog Index**: The user navigates to `/alice/blog` ([@ANCHOR: controller_user_blog_index]).
2. **First Post**: The user clicks "Create Blog Post" ([@ANCHOR: UX_CREATE_BLOG_POST]).
3. **Provisioning**: The system initializes the `blog.blog` container for the user if it doesn't exist and creates a "Welcome" post.
4. **Engagement**: Visitors can now subscribe to Alice's updates ([@ANCHOR: UX_SUBSCRIBE]).
