# Epics & User Stories: Live Propagation Forecasting Maps

## Epic: HF Propagation Visualization
* **Story:** As an operator planning a session, I want to see a visual heatmap of reachable regions based on current solar conditions.
*(Reference: ham_propagation/controllers/api.py -> get_muf_paths -> [@ANCHOR: calculate_muf_paths])*
    * **BDD Criteria:**
        * *Given* an authenticated user with a known Grid Square
        * *When* they access the Propagation Dashboard
        * *Then* the backend MUST check Redis for a cached response. If empty, it MUST calculate MUF paths utilizing the latest `ham.space.weather` row, cache the output in Redis for 15 minutes to prevent DoS, and return an array of geographic polygons.

* **Story:** As an operator planning a session, I want the UI to dynamically render the visual heatmap of reachable regions based on the returned data.
    * **BDD Criteria:**
        * *Given* the calculated MUF path data
        * *When* the propagation dashboard mounts
        * ** *Then* the frontend MUST render the visual map container. *(Reference: [@ANCHOR: UX_FRONTEND_PROPAGATION_DASHBOARD])*])*

* **Story:** As a visually impaired operator, I want text-based propagation forecasts rather than relying solely on a visual heatmap.
*(*(Reference: ham_propagation/static/src/xml/propagation_dashboard.xml -> PropagationDashboard -> [@ANCHOR: UX_A11Y_PROPAGATION_TABLE])*])*
    * **BDD Criteria:**
        * *Given* the Propagation Dashboard is loaded
        * *When* parsed by a screen reader
        * *Then* an `aria-live` region MUST provide a localized tabular summary (e.g., "Europe: 20 Meters Open, Japan: 40 Meters Closed").
