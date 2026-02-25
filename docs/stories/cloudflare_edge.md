# Agile Stories: Cloudflare Edge Orchestration

## Story 1: Automated WAF Provisioning
**As a** System Administrator
**I want** the system to automatically deploy optimized WAF rules to Cloudflare upon installation
**So that** the Odoo database and APIs are immediately protected without manual configuration.

### Acceptance Criteria (BDD)
* **Given** the Cloudflare module is being installed on a fresh Odoo database
* **When** the `post_init_hook` fires and checks the Cloudflare edge
* **Then** if the edge is empty, it MUST deploy the `DEFAULT_WAF_RULES` *(Reference: `cloudflare/models/config_manager.py` -> `initialize_cloudflare_state`)*
* **And** if the edge already has custom rules, it MUST back them up locally and skip deployment to prevent overwriting sysadmin work.

---

## Story 2: Silent Honeypot Banning
**As a** Security Architect
**I want** malicious scrapers triggering honeypots to be banned at the edge
**So that** Odoo WSGI workers are protected from bandwidth exhaustion.

### Acceptance Criteria (BDD)
* **Given** a public guest triggers a hidden honeypot field
* **When** the controller calls the WAF API
* **Then** it MUST push the ban to Cloudflare and log the action locally in the `cloudflare.ip.ban` registry. *(Reference: `cloudflare/models/ip_ban.py` -> `_execute_ban` -> [%ANCHOR: cf_execute_ban])*

---

## Story 3: UI-Driven Ban Lifting
**As a** System Administrator
**I want** to view and lift IP bans directly from the Odoo backend
**So that** I can easily resolve false-positive honeypot triggers without logging into the Cloudflare dashboard.

### Acceptance Criteria (BDD)
* **Given** an IP address is currently banned (`state == 'active'`)
* **When** the administrator clicks the "Lift Ban" button in the UI
* **Then** the system MUST call the Cloudflare REST API to delete the rule, and visually update the record to `lifted`. *(Reference: `cloudflare/models/ip_ban.py` -> `action_lift_ban` -> [%ANCHOR: cf_action_lift_ban])*
