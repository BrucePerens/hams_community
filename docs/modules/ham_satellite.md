# 🛰️ Ham Radio Satellite Tracker (`ham_satellite`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

**Context:** Technical documentation strictly for LLMs and Integrators.

---

## 1. Overview
Live AMSAT satellite pass predictions and orbital tracking calculated locally using the `ephem` library.

## 2. Data Model Reference

### Core Model: `ham.satellite.tle`
* **`name`** (`Char`): Satellite name.
* **`line1`**, **`line2`** (`Char`): Two-Line Element data.
* **`sync_tles(tles)`**: XML-RPC target for the background AMSAT daemon to bulk update orbital parameters.

## 3. Public REST API
* **Endpoint:** `GET /api/v1/ham_satellite/passes`
* **Behavior:** Calculates passes. Accepts `location` (Grid Square, Decimal, or DMS) and optional `time` (UTC ISO string). Returns a JSON array of AOS, TCA, and LOS metrics.
