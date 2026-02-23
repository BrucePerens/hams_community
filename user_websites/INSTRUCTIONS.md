# User Websites Module Instructions

*Copyright © Bruce Perens K6BP. Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).*

This document provides instructions for installing, configuring, and using the User Websites module in Odoo.

## 1. Installation

1.  **Place the Module:** Copy the `user_websites` directory into your Odoo `addons` path.
2.  **Restart Odoo:** Restart the Odoo server to make the new module available.
3.  **Install the App:**
    * Log in to Odoo as an administrator.
    * Navigate to the **Apps** menu.
    * Click on **Update Apps List** in the menu.
    * Remove the default "Apps" filter and search for "User Websites".
    * Click the **Install** button on the "User Websites" module.

## 2. Configuration (for Administrators)

The module's settings can be accessed by navigating to **Settings > General Settings > User Websites**.
* **Global Page Limit:** You can set a default maximum number of web pages a user can create. A user-specific limit will override this global setting.
* **Administrators:** You can grant specific users administrative rights over the User Websites module. These administrators can view and manage all content violation reports.

## 3. User Guide

### 3.1. Creating User Content

* **Website Pages:** Users can create pages under their personal URL (`/<username>`).
* **Blog Posts:** Users can create blog posts which will appear at `/<username>/blog`.

### 3.2. Managing Your Public Profile

Users can control their visibility in the community directory:

1.  Go to your **Preferences**.
2.  Under the "User Websites" section, you will find the **"Show in Public Directory"** checkbox.
3.  Check this box if you want a link to your website to appear on the community directory page.

### 3.3. Reporting Content Violations

If you encounter content that you believe violates the community standards, you can report it:

1.  Click the "Report Violation" button located near the content.
2.  A dialog box will appear. Fill in the details explaining the nature of the violation.
3.  Submit the report. It will be sent to the site administrators for review.

## 4. For Developers

### 4.1. Running Tests

To run the automated tests for this module, execute the following command from your Odoo project's root directory:

```bash
./odoo-bin --test-enable --stop-after-init --addons-path addons -i user_websites
```
