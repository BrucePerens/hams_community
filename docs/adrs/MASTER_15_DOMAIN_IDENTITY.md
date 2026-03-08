# MASTER 15: Domain Identity & Verification

## Status
Accepted (Consolidates ADRs 0019, 0064)

## Context & Philosophy
Domain-specific rules for verifying Amateur Radio operator identities securely without exposing internal ERP models.

## Decisions & Mandates

### 1. Identity Verification Fallback Matrix (0019)
* Operator verification MUST support a diverse, international matrix to guarantee accessibility:
    1. Cryptographic LoTW (Golden Path)
    2. Knowledge-based (Ham-CAPTCHA / QRZ)
    3. Skill-based (Dynamic Morse Code Challenge)
    4. Regulatory (Official FCC Email OTP)
    5. Manual ID Upload

### 2. Shadow Profile Indexing (0064)
* To protect Odoo's core `res.users` table from excessive daemon queries and bypass its restrictive internal security assumptions, public routing data (Callsigns, API Secrets, FRNs) MUST be exposed via isolated PostgreSQL Views (`ham.operator.index` and `ham.swl.index`).
* Daemons MUST query these shadow views. Standard internal ERP users who lack the specific Ham/SWL security groups are natively excluded from the SQL `JOIN`.
