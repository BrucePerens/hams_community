# Odoo Core Modules & LLM Development Standards

This repository contains a suite of foundational Odoo 19+ modules designed for general-purpose use—specifically focusing on system compliance, documentation management, and user web integration. 

Additionally, this repository serves as the source of truth for the strict Large Language Model (LLM) operational mandates and Odoo technical standards used to develop these tools.

## 📦 Included Modules

This repository distributes the following core modules:

* **`compliance`**: Implements native frameworks for GDPR/CCPA compliance, including data portability (JSON exports), right to erasure, and native cookie consent integration.
* **`manual_library`**: A dynamic documentation management system that injects end-user guides and system documentation into the platform (designed with Odoo's `knowledge.article` as a soft dependency).
* **`user_websites`**: Infrastructure for managing user-specific web profiles and site integrations.

*(Note: These modules are designed to be domain-agnostic and operate independently of any specific application verticals).*

## 🤖 LLM-Assisted Development Standards

Development in this repository is governed by strict operational and architectural mandates enforced during LLM-assisted coding sessions. These standards ensure security, accessibility (WCAG 2.1 AA), and adherence to modern Odoo 19+ native idioms.

* **`docs/LLM_GENERAL_REQUIREMENTS.md`**: Global operational mandates, Agile/SRE formalizations, security patterns (Zero-Sudo), and the AEF 4.0 JSON transport protocol requirements.
* **`docs/LLM_ODOO_REQUIREMENTS.md`**: Odoo-specific architectural rules, including a strict "Burn List" of deprecated legacy patterns, proper ORM/Caching standards, and secure RPC execution mandates.

## ⚖️ License & Copyright

Copyright © Bruce Perens K6BP. 

This software is licensed under the **GNU Affero General Public License, version 3 (AGPL-3.0)**. See the `LICENSE` file for more details.
