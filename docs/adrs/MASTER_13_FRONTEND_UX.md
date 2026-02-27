# MASTER 13: Frontend UX & Accessibility

## Status
Accepted (Consolidates ADR 0030)

## Context & Philosophy
The platform must remain accessible to visually impaired operators while rendering complex, high-velocity data streams.

## Decisions & Mandates

### 1. Accessible Real-Time DOM Mutation (0030)
* UI widgets rendering high-velocity data (like the live DX Cluster WebSockets) use `aria-live` to notify screen readers of changes.
* However, frequent updates trap screen readers in an infinite reading loop. These components MUST feature an accessible "Pause" toggle.
* Toggling pause MUST change the DOM to `aria-live="off"` and instruct the WebSocket payload listener to drop incoming state mutations, giving the user a static snapshot to navigate.
