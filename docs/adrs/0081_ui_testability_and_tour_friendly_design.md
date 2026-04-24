# ADR 0081: UI Testability and Tour-Friendly Design Architecture

## Status
Accepted

## Context
The platform mandates automated testing for all UI views to prevent regressions. However, JavaScript UI Tours in Odoo are inherently brittle due to their reliance on specific DOM structures, CSS selectors, and exact timing. Recent CI pipeline failures highlight severe issues with DOM race conditions, invisible elements, and blocking native dialogs.

To enforce the test reliability mandate without creating a "maintenance trap" of constantly broken tours, we must treat UI testability as a core, upstream architectural requirement rather than an afterthought.

## Decision
All front-end XML templates and custom JavaScript widgets MUST be architected specifically to support deterministic, race-condition-free automated tours. The following mandates apply to all UI development:

### 1. Dedicated Testing Selectors
UI components MUST NOT rely on structural layout classes (e.g., `.col-md-6`, `.mt-4`, `.d-flex`) or translated text strings for test triggers, as these frequently change during UI polish.
* Developers MUST inject dedicated attributes explicitly for testing (e.g., `data-tour="submit-action"`) or utilize strict `name="..."` attributes on fields and buttons.

### 2. Explicit Asynchronous State Exposure (Custom Widgets)
Tours execute steps the millisecond a selector appears in the DOM, which causes violent race conditions when RPC calls (like saving a record) are still in-flight.
* Custom JavaScript widgets MUST explicitly toggle state classes on their parent containers. For example, inject a `.hams-loading` class when an RPC call begins, and swap it to `.hams-ready` when the promise resolves. Tours MUST trigger on `.hams-ready` to mathematically guarantee the background operations have finished.

### 3. Decoupling of Blocking Dialogs
Native JavaScript dialogs (`window.confirm`, `window.alert`, `window.prompt`) halt the browser's execution thread and cause the Odoo tour runner to lose context regarding `beforeUnload` events.
* Developers MUST strictly avoid using inline `onsubmit="return confirm('...');"` handlers in XML templates.
* Interactions requiring confirmation MUST be routed through an Odoo JS Controller utilizing the native `ConfirmationDialog` service, which allows the test framework to interact with the modal natively without thread-blocking.

### 4. Dimensioned Target Elements
Odoo's tour framework inherently ignores elements with a 0x0 pixel dimension.
* If a UI relies on invisible dropzones or placeholder `<div>` tags for dynamic mounting, the elements MUST possess a minimal physical dimension in the CSS (e.g., `min-height: 1px;`).
* If a container must remain completely structureless and invisible, the tour MUST explicitly append `:not(:visible)` to the trigger selector.

### 5. Bidirectional Semantic Anchoring
* Every front-end `<template>` and `<record model="ir.ui.view">` MUST contain a bidirectional semantic anchor (`[@ANCHOR: ...]`) linking the XML element directly to its corresponding JS Tour step. This guarantees traceability and prevents developers from breaking tests when refactoring views.

### 6. Native Auto-Save and RPC Resolution (The "Dirty Form" Rule)
Native Odoo form buttons (e.g., `type="object"`) automatically and asynchronously save the form before invoking their backend methods. If a tour navigates away or terminates before this background save resolves, Odoo will halt the test with a "dirty form view" error to prevent data corruption.
* Tours MUST explicitly wait for a verifiable DOM state change confirming the RPC has resolved after clicking *any* native action button. This must be done by explicitly targeting `.o_notification:contains("Success")`, `.o_form_readonly`, or another guaranteed post-save DOM mutation before ending the tour.

### 7. Action Button State Governance (The "Unsaved Record" Trap)
Relying on Odoo's native auto-save mechanism when clicking an action button on a newly created, dirty form introduces severe race conditions where partial text input is submitted to the backend.
* Native Odoo object buttons (`type="object"`) that execute backend Python methods MUST be hidden on new, unsaved records using `invisible="not id"` (or merged into existing visibility domains, e.g., `invisible="is_installed or not id"`).
* Forcing the user (and the tour) to explicitly save the record first guarantees a deterministic state machine and decouples data entry from RPC execution.
