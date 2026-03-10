# MASTER 15: Domain Identity & Verification

## Status
Accepted (Consolidates ADRs 0019, 0064)

## Context & Philosophy
Domain-specific rules for verifying User identities securely without exposing internal ERP models.

## Decisions & Mandates

### 1. Identity Verification Fallback Matrix (0019)
* User verification MUST support a diverse, international matrix to guarantee accessibility:
    1. Cryptographic Token (Golden Path)
    2. Knowledge-based / External Bio
    3. Skill-based Challenge
    4. Regulatory Email OTP
    5. Manual ID Upload

### 2. Shadow Profile Indexing (0064)
* To protect Odoo's core `res.users` table from excessive daemon queries and bypass its restrictive internal security assumptions, public routing data (Usernames, API Secrets, IDs) MUST be exposed via isolated PostgreSQL Views (`verified.user.index` and `guest.user.index`).
* Daemons MUST query these shadow views. Standard internal ERP users who lack the specific Domain security groups are natively excluded from the SQL `JOIN`. [%ANCHOR: sync_ham_indices]
