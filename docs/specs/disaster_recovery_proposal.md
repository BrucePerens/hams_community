# Proposal: Open Source Disaster Recovery Documentation Management System (OS-DRDMS)

**Status:** Proposed
**Related Mandates:** MASTER 01 (Zero-Sudo), MASTER 08 (Core Architecture), MASTER 10 (Access Control)

## 1. Executive Summary
This proposal outlines the architecture to transition and create an enterprise-grade Open Source Disaster Recovery Documentation Management System (OS-DRDMS) within Odoo 19 Community.
Modeled after systems utilized by the Mississippi Emergency Management Agency (MEMA) post-Katrina, this suite serves as a standardized interface between federal, state, and local government entities.

The primary operational goal is to prevent the financial disaster of local entities having to repay the Federal Government due to undocumented or misappropriated recovery funds.
By bridging interactive, SVG-based ICS forms with Odoo's relational database (Accounting, Document Management, and HR), the platform will provide automated cost-tracking, verifiable audit trails, and real-time project closeout administration.

---

## 2. Detailed Module Ecosystem & Integration Strategy

The system will be built using a tiered framework (Data, Logic, Presentation) mapped natively to Odoo's PostgreSQL backend, Python ORM, and OWL frontend.
We will develop the following domain-extension modules:

### 2.1. `dr_ics_core` (Electronic Document Management, Workflow & CMS)
This module acts as the foundation, absorbing the standalone `ics_forms` logic and translating it into an Odoo-native portal application.

#### Core Screens & Views
* **Incident Command Dashboard:** The primary landing page for an active disaster.
Displays a Kanban view of operational periods, missing mandatory documentation alerts, and quick links to initiate new ICS forms.
* **OWL Interactive Form Renderer:** A specialized frontend OWL component that renders the underlying SVG forms interactively.
It features auto-scaling text inputs, dynamic pagination, and buttons to save data to the backend or export directly to JSON/PDF without relying on external web browsers' print dialogues.
* **Document Vault & Revision Panel:** A list view displaying all submitted forms by type and incident.
Selecting a form opens a split-screen view: the rendered PDF snapshot on the left, and Odoo's native `mail.thread` (chatter) on the right for audit trails and revision notes.
* **SOP CMS Builder:** A WYSIWYG editor page allowing Incident Commanders to publish standard operating procedures, training bulletins, and ad-hoc data collection forms directly to the responder portal.

#### Key Functions & Automated Routines
* `action_submit_form(json_payload)`: An RPC controller method that receives the raw JSON from the OWL form renderer.
It validates the payload against the required fields for that specific ICS form type and commits it to the database.
* `_generate_pdf_snapshot()`: A background method triggered post-submission. It uses a headless browser utility to render the completed form into a static PDF and attaches it to an `ir.attachment` record, securing an immutable point-in-time snapshot.
* `_evaluate_workflow_completeness()`: A nightly scheduled action (`ir.cron`) that cross-references submitted forms against the active operational period.
If an ICS-201 (Incident Briefing) or ICS-214 (Activity Log) is missing, it utilizes the `dr_mail_service_internal` account to dispatch automated warning emails to the assigned section chiefs.
* `action_carry_forward_data()`: A helper method for responders creating forms for a new operational period.
It queries the previous day's forms and pre-populates static fields (like personnel rosters on an ICS-204) to save data-entry time.

### 2.2. `dr_finance` (Recovery Accounting, Compliance & Closeout)
This module integrates ICS form data directly into Odoo's native `account` and `purchase` modules to track burn rates and generate audit-proof FEMA reimbursement packages.

#### Core Screens & Views
* **FEMA Closeout Board:** A high-level Kanban dashboard for state auditors and financial officers.
Columns represent the reimbursement pipeline (Draft, Pending Review, Submitted to FEMA, Approved, Disbursed).
Each card displays the aggregated cost and burn rate for a specific project worksheet.
* **Timesheet Reconciliation View:** A specialized list view that cross-references personnel hours submitted via field ICS-214 (Activity Log) forms against Odoo's native HR/Payroll timesheets, highlighting discrepancies in red.
* **Resource Order (ICS-260) to PO Wizard:** A transient model wizard.
When an ICS-260 is approved by Logistics, this screen allows the finance officer to map the requested line items to standard Odoo products and instantly generate an actionable Purchase Order.

#### Key Functions & Automated Routines
* `_parse_ics214_to_analytic_lines()`: An asynchronous queue worker.
When an ICS-214 is finalized, it extracts the personnel hours and equipment usage, automatically generating `account.analytic.line` entries mapped to the specific disaster's cost center.
* `action_generate_fema_packet()`: Compiles all documentation associated with a project worksheet into a single, comprehensive PDF/ZIP manifest.
It extracts the raw form PDFs, associated Purchase Orders, and vendor receipts, significantly reducing the administrative burden of final audits.
* `_check_compliance_rules()`: A validation hook that runs before a project is moved to "Submitted".
It ensures that force account labor (internal staff) vs. contracted work rules are met and that pre-disaster asset valuations are attached.

### 2.3. `dr_logistics` (Inventory & Fleet Management)
This module maps standard ICS physical resource forms directly to Odoo's backend logistics routing and map interfaces.

#### Core Screens & Views
* **Active Deployment Map:** A geospatial Leaflet map (utilizing standard `ham.geo.utils`) that displays the last known locations of vehicle fleets and operational task forces based on geolocation data submitted alongside their active forms.
* **Check-In / Demobilization Kiosk:** A simplified, touch-friendly UI designed for staging areas.
Responders can scan a barcode or QR code on their ID badge to instantly populate an ICS-211 (Check-In List) or trigger an ICS-221 (Demobilization Check-Out).

#### Key Functions & Automated Routines
* `sync_ics218_to_fleet()`: A method that parses incoming ICS-218 (Support Vehicle Inventory) forms.
It checks if the vehicle exists in Odoo's `fleet.vehicle` registry and updates its status, odometer, and current driver assignment.
* `action_trigger_demobilization()`: When an operator's assignment ends, this method evaluates their custody of any serialized equipment (radios, laptops).
It blocks the issuance of an approved ICS-221 checkout form until all physical assets are registered as returned to the supply unit.
* `_route_resource_request()`: Evaluates incoming ICS-213RR (Resource Request) forms and routes them to the appropriate logistics channel based on the requested item category (e.g., Telecom equipment routes to the COMML, heavy machinery to the Ground Support Unit).

### 2.4. `dr_survivability` (Remote Survivability Appliance & Mobility)
Ensures critical application functionality remains available during internet outages or complete loss of connectivity via an airgapped store-and-forward architecture.

#### Core Screens & Views
* **Synchronization Status Dashboard:** An administrative dashboard within the primary Odoo instance detailing the connection status of deployed field appliances.
It displays last-ping timestamps, the volume of pending JSON payloads, and any merge conflicts that require human resolution.
* **Appliance Local Gateway:** A lightweight, localized version of the Odoo portal served directly from the physical field appliance, providing access exclusively to the OWL Interactive Form Renderer.

#### Key Functions & Automated Routines
* `api_sync_offline_payloads()`: A highly secured REST endpoint protected by HMAC-SHA256 signatures.
It acts as the gateway for the local field appliance to dump its encrypted queue of completed forms into the master database once internet connectivity is restored.
* `_resolve_sync_conflicts()`: A backend reconciliation algorithm. If a form was edited both on the master server and the offline appliance simultaneously, this method evaluates the `mtime` (modification time) and applies conflict resolution rules (typically prioritizing the most recent field data).
* `action_remote_wipe_command()`: An emergency security function. If a mobile device or field appliance is reported stolen, this sets a flag.
The absolute first action the appliance performs upon gaining network access is fetching this flag;
if true, the appliance immediately cryptographically shreds its local database.

---

## 3. Security & Extranet Access

Given the privileged nature of disaster documentation and personally identifiable information, the system enforces extreme security measures:

* **Extranets for Localities:** Local entities (mayors, county emergency managers) are granted secure portal access via `base.group_portal`.
They are strictly isolated by Record Rules, allowing them to upload project-critical files (payroll records, bid processes) to personalized secure areas without seeing neighboring jurisdictions' data.
* **Strict Least Privilege:** The system relies entirely on the Micro-Service Account Pattern. No operations are permitted using `.sudo()`.
Background syncs, PDF generation, and financial ledger writing are executed by highly specific, restricted proxy accounts (e.g., `dr_finance_service_internal`).
* **HTTPS/SSL Enforcement:** All frontend, API traffic, and field-appliance synchronizations are strictly enforced over TLS 1.3.
* **RESTful Gatekeepers:** Database communication across physical field clusters and the central state repository will occur on private subnets or VPNs, utilizing RESTful API nodes acting as gatekeepers to prevent direct SQL port exposure.

---

## 4. Yet-To-Be-Specified Details (Areas for Further Definition)

While the high-level architecture is established, several domain-specific rules and algorithmic mappings require explicit specification from subject matter experts (e.g., FEMA compliance officers or Incident Commanders) before implementation can begin:

* **FEMA Compliance & Work Rules:** The `_check_compliance_rules()` validation references "force account labor vs. contracted work rules." The exact mathematical caps, eligible overtime formulas, and specific ratios required for FEMA reimbursement must be formally codified.
* **Pre-Disaster Asset Valuation:** The mechanism for calculating and verifying pre-disaster asset values (e.g., specific depreciation schedules, formulas, or third-party blue-book API integrations) for equipment loss reimbursement is currently undefined.
* **Conflict Resolution Algorithms:** The `_resolve_sync_conflicts()` method mentions prioritizing recent field data. The exact precedence rules for merging offline appliance data with the master database (e.g., timestamp resolution, field-level vs. document-level overwrites, and triggers for manual administrator intervention) must be explicitly detailed.
* **Resource Routing Matrix:** The `_route_resource_request()` method requires a comprehensive lookup matrix that maps specific ICS resource types and categories directly to their designated logistics channels (e.g., mapping telecom requests to the COMML).
* **Mandatory Form Dependencies:** The `_evaluate_workflow_completeness()` hook checks for missing ICS-201 and ICS-214 forms. A complete matrix of mandatory forms required to successfully close an operational period or transition an incident phase needs to be documented.
* **Appliance Initialization & Security:** The exact ritual for provisioning, securely pairing, and rotating keys for a remote `dr_survivability` appliance with the master database (including offline user authentication pathways) requires a dedicated sequence diagram.
