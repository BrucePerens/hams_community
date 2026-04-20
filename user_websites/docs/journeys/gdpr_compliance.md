# Journey: User Data Management (GDPR)

This journey describes how a user manages their data footprint on the platform.

## Path: Data Portability

1. **Dashboard**: The user navigates to `/my/privacy` ([@ANCHOR: controller_my_privacy_dashboard]).
2. **Request**: The user clicks the "Export My Data" button.
3. **Compilation**: The system executes `_get_gdpr_export_data` ([@ANCHOR: res_users_gdpr_export]).
4. **Streaming**: To handle potentially large amounts of content, the system streams the JSON response to the user's browser ([@ANCHOR: UX_GDPR_EXPORT]).
5. **Receipt**: The user receives a comprehensive JSON file containing their site data.

## Path: Account Deletion (Right to Erasure)

1. **Dashboard**: The user navigates to the Privacy Dashboard.
2. **Deletion**: The user clicks "Delete My Content" ([@ANCHOR: UX_GDPR_ERASURE]).
3. **Asynchronous Processing**: The system hands off the erasure task to a background executor ([@ANCHOR: gdpr_sudo_erasure]).
4. **Content Removal**: The background task unlinks all pages, blog posts, and media associated with the user.
5. **Anonymization**: The user's profile is scrubbed of PII and deactivated.
6. **Confirmation**: The user is logged out and redirected to a confirmation page.
