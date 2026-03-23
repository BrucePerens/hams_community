# Feature Specification: Contextual UI Validation

**Status:** Proposed (Deferred for Testing Phase)
**Author:** Bruce Perens K6BP
**Related Mandates:** MASTER 11 (Shift-Left Data Validation, Human Time vs. Machine Time)

## 1. Objective
To ruthlessly protect administrator time and prevent downstream data pollution (logbook errors, incorrect distance calculations, failed QSLs) by providing immediate, asynchronous, and non-blocking human-readable feedback at the UI level.

Asking a human to confirm a familiar city name is vastly superior to asking them to re-read a 6-character alphanumeric string like `CM87vs` that they just mis-typed. By making the user catch their own mistakes *before* they hit the database, we eliminate hours of manual backend cleanup.

## 2. Maidenhead Spatial Validation (Grid Squares)

### The Logic
A Maidenhead grid square represents a bounding box on the globe. We will implement a Python utility to mathematically convert any valid 4- or 6-character grid into a center-point Latitude/Longitude coordinate.

### The Data Source
To prevent external network dependencies (and avoid "cybercrud" timeout errors in the logs), we will include a lightweight, offline JSON dictionary or static database table. This will map rough lat/lon bounds to major global cities or regional territories.

### The UI Flow
1. The user types `CM87vs` into a profile, event, or logbook form.
2. On the input field's `blur` or `change` event, an asynchronous Odoo JS controller pings the backend `ir.http` route.
3. The UI dynamically displays helper text below the field:
   * **Success:** `"📍 Near Berkeley, California"`
   * **Failure/Typo:** `"⚠️ Invalid grid square format."`

## 3. Callbook Cross-Reference (Callsigns)

### The Logic
Whenever a callsign is entered (for registration, logging a QSO, or submitting an event), the system will first validate it against standard ITU prefix regexes. Subsequently, it will perform a highly optimized indexed lookup against the local `ham_callbook` table.

### The UI Flow
1. **Auto-Population:** If the callsign matches the database, the system will offer to auto-populate known fields (Name, Grid Square) to save keystrokes.
2. **Soft Warnings:** If the callsign matches a region we *know* we have bulk data for (e.g., the US FCC database), but the specific callsign is missing, the UI will display a soft warning: `"⚠️ Callsign not found in the current directory. Please double-check for typos."`

### Architectural Constraint: Non-Blocking
The callsign warning **MUST** be a soft warning. We cannot hard-block the form submission. Brand new hams might have literally just received their FCC grant that morning, and our local callbook sync might be 24 hours behind. The system must advise, not dictate.

## 4. Implementation Steps
* **Backend:** Create `ham_base.grid_utils` for Maidenhead math and load the static geographic mapping dataset.
* **Backend:** Create a fast, unauthenticated (or public-accessible) JSON-RPC controller endpoint to handle the async lookups.
* **Frontend:** Extend Odoo's `FieldChar` or `InputField` widget in JavaScript to inject the DOM helper elements and debounce the API calls.
