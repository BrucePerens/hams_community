# Hams.com Project Tracker

This document serves as the lightweight Kanban board and backlog for the platform. As we complete features, they move from Backlog to Done.

## 📝 Backlog (Future / Phase 2)
* **[Feature] AI Simulator: Client-Side UI** - Build the HTML5 Canvas waterfall and PTT console.
* **[Feature] AI Simulator: Wasm STT** - Integrate `transformers.js` Whisper model for local microphone transcription.
* **[Feature] AI Simulator: RAG Memory** - Set up `pgvector` schema for robot operator memory extraction.
* **[Feature] AI Simulator: FT8 State Machine** - Build the macro sequencing logic for digital mode simulation.
* **[Feature] AI Simulator: Browser DSP** - Implement Web Audio API nodes for QRN, QSB, and bandpass filtering.

## 🚧 In Progress (Phase 1 - Current Focus)
* All Phase 1 tasks completed. Transitioning to Phase 2 (AI Simulator).

## ✅ Done
* **[Data] FCC Sync Pipelines** - Matured the daily regulatory database parsing to include AM.dat license class mapping.
* **[DevOps] SRE Suite & Pager Duty** - Deployed multi-tier escalation, NOC dashboard, and self-healing infrastructure checks.
* **[DevOps] Database APM & Backups** - Implemented PG optimization, automated Patroni HA generation, and unified Kopia/pgBackRest orchestration.
* **[DevOps] Automated Deployment** - Built interactive Python deployment wizard with dummy SSL scaffolding and Just-In-Time dependencies.
* **[Architecture] Core System Security** - Finalized Zero-Sudo architecture and Multi-Persona isolation.
* **[Testing] CI/CD Hardening** - Resolved Flake8, built strict AST Linter evasions guards, and enforced Semantic Anchor bidirectional checks.
* **[Feature] LoTW mTLS Auth** - Cryptographic authentication via ARRL certificates.
* **[Architecture] ADR-0064 Shadow Profiles** - Decoupled public daemon queries from Odoo's internal `res.users` table.
* **[Architecture] Multi-Persona Matrix** - Established testing boundaries for Web, Standard, Ham, and SWL users.
