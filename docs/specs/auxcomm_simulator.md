# Feature Specification: Tactical AUXCOMM Simulator

**Status:** Proposed (Ready for Architecture)
**Related Mandates:** MASTER 14 (Context Management), MASTER 11 (Agile Workflow)

## 1. Objective
To build an interactive, context-aware training simulator that translates dry federal NIMS/ICS doctrines into operational amateur radio scenarios.
It moves operators away from memorizing multiple-choice answers and forces them to apply NIMS concepts in simulated, high-stress environments.

## 2. Scope of Curriculum
The simulator will integrate and contextualize the following federal frameworks:
* **IS-100 & IS-200:** Basic and Initial Action Incident Command System.
* **IS-700:** National Incident Management System.
* **IS-2200:** Basic EOC Functions.
* **IS-802.a:** Emergency Support Function (ESF) #2 — Communications.
* **IS-242.c & IS-244.b:** Effective Communication and Volunteer Management.
* **Bridges to:** ICS-300 (The Planning P), CISA AUXCOMM, SKYWARN, and CERT.

## 3. Core Engine Components

### A. The Tabletop Scenario Engine
* **Data Models Needed:** `ham.auxcomm.scenario`, `ham.auxcomm.inject`.
* **Function:** A branching, text-based simulation feeding the operator "Injects" (e.g., resource requests, infrastructure failures).
The user must identify NIMS violations and route messages correctly through the ICS hierarchy.

### B. The EOC Sandbox & Message Drills
* **Integration:** Will hook into `ham_shack` and `ham_events`.
* **Function:** Users practice transcribing live, chaotic inputs into strict ICS-213 General Message forms.
Simulates EOC stress by introducing audio QRM (static) or rapid, conflicting UI popups that must be triaged according to NIMS priority protocols.

### C. AI-Debunking Spaced Repetition
* **Integration:** Expands `ham.testing.progress`.
* **Function:** Uses the AI-Synthesis pipeline to generate targeted HTML explanations debunking the exact distractors a user falls for in the FEMA question pools.
