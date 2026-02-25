# Global Compliance (`compliance`) - API Reference

## Purpose
Acts as the central hub for automated regulatory compliance (GDPR, CCPA, ePrivacy). It automatically enables Odoo's native Cookie Consent Bar and provisions AGPL-3 compliant boilerplate legal pages safely.

## API & Usage
This module contains **no callable Python API methods**. It operates entirely via initialization hooks and Odoo framework enforcement.

### Standardized Routes
Dependent modules (like E-Commerce or Onboarding) that require linking to legal documents MUST use the following routes provisioned by this module:
* `/privacy` : Privacy Policy
* `/cookie-policy` : Cookie Policy
* `/terms` : Terms of Service

### Integration Rules
1. **Do Not Build Custom Banners:** Rely entirely on Odoo's native `website.cookies_bar`.
2. **Tracking Scripts:** Any third-party JavaScript tracking MUST hook into the Odoo consent state.
