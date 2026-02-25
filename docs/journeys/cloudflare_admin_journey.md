# User Journey: Cloudflare Edge Administrator

## 1. Persona Profile
* **Role:** System Administrator
* **Goal:** Protect the platform from malicious traffic, manage edge caching, and review honeypot triggers without leaving the Odoo ERP environment.

---

## 2. Journey: Reviewing and Lifting a Honeypot Ban

**Trigger:** A legitimate user complains they are receiving a Cloudflare "Access Denied" block screen when trying to access the site.

1. **Discovery:** The Administrator logs into Odoo and navigates to the **Cloudflare Edge** app.
2. **Inspection:** They click on **Honeypot Triggers (Bans)**.
3. **Verification:** They search the list view for the user's IP address and see it was blocked 30 minutes ago with the note "Honeypot Triggered".
4. **Action:** The Administrator opens the record and clicks the **Lift Ban & Unblock API** button.
5. **Resolution:** The system makes a synchronous API call to Cloudflare, deletes the specific firewall rule, and updates the UI badge to "Lifted". The user can instantly access the site again.

---

## 3. Journey: Customizing the Firewall

**Trigger:** The Administrator wants to whitelist a specific external IP address from the XML-RPC block rule.

1. **Synchronization:** The Administrator navigates to **Settings > Cloudflare Edge Orchestration** and clicks **Pull from Edge** to ensure Odoo has the latest state.
2. **Editing:** They navigate to the **Cloudflare Edge > WAF Rulesets** menu.
3. **Modification:** They open the "Block Legacy XML-RPC" rule and modify the Cloudflare Wirefilter expression to include `and ip.src ne 203.0.113.5`.
4. **Deployment:** They return to **Settings > Cloudflare** and click **Push to Edge**. Odoo compiles the AST JSON and updates the live ruleset on Cloudflare.
