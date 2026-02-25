# Operational Runbook: Cloudflare Edge

## Overview
This runbook outlines the operational procedures for managing the Odoo-to-Cloudflare integration. The `cloudflare` module acts as the control plane, utilizing background queues and synchronous REST API calls to manipulate edge caching and Web Application Firewalls (WAF).

---

## 1. Initial Authentication Setup
The module requires environment variables to authenticate with the Cloudflare API. These MUST be stored in the deployment `.env` vault.

**Required Variables:**
* `CLOUDFLARE_API_TOKEN`: A scoped API token (Requires `Zone.Cache Purge`, `Zone.Firewall Services`).
* `CLOUDFLARE_ZONE_ID`: The unique 32-character ID of the target domain.

*For CLI instructions on injecting these variables, refer to `deploy/DOCKER_DEPLOYMENT.md`.*

---

## 2. Troubleshooting the Cache Purge Queue
If users report that their website pages or blog posts are not updating after they make edits, the async purge queue may be failing or stalled.

**Symptom:** Records in `cloudflare.purge.queue` are stuck in `pending` or marked as `failed`.

**Resolution Steps:**
1. **Check Credentials:** Verify the API token has not expired.
2. **Check Cron State:** Navigate to **Settings > Technical > Scheduled Actions**. Ensure `Cloudflare: Process Cache Purge Queue` is active. Manually trigger it.
3. **Batch Rate Limiting:** Cloudflare limits cache purging to 30 URLs per request. If a massive operation generated 1,000+ URLs, the queue will process them in batches of 30 every 1 minute to respect API limits. Wait for the queue to clear.

---

## 3. Disaster Recovery: WAF Lockouts
If a pushed WAF rule contains a malformed expression that accidentally blocks ALL traffic (including administrators), the Odoo UI will become unreachable from the public internet.

**Resolution Steps:**
1. Log into the physical server via SSH or access the Odoo instance via a local internal tunnel (bypassing Cloudflare routing).
2. Navigate to the **Cloudflare Edge > Config Backups** menu in Odoo.
3. Open the latest backup created before the lockout.
4. Copy the raw JSON payload and manually paste/import it into the Cloudflare Web Dashboard, or simply uncheck the offending rule in Odoo and click **Push to Edge** from the internal network.
