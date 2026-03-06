# ADR-0065: Headless API Translation Ban

## Context
Headless API controllers (e.g., `ham_logbook` ADIF and Live QSO endpoints) return JSON payloads containing error messages. Previously, these error strings were wrapped in Odoo's `_()` translation function. During headless automated testing, the `request.env` context often lacks a fully bound user session. This causes `odoo.tools.translate._get_uid` to throw an `AttributeError: 'NoneType' object has no attribute 'uid'`, crashing the entire endpoint.

## Decision
We strictly **ban** the use of the `_()` translation wrapper around string literals within JSON responses in headless API controllers.

APIs must return static, un-translated English error codes or messages. Client-side applications (such as the web frontend or mobile app) are entirely responsible for mapping these static error strings to localized translations. This guarantees API stability across all execution environments (Test, Cron, Daemon, and Live).