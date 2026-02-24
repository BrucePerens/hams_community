# ADR 0030: Accessible Real-Time DOM Mutation (ARIA-Live Toggling)

## Status
Accepted

## Context
The platform features high-velocity data feeds like the DX Cluster and Live Net Rosters. While `aria-live="polite"` is standard for dynamic UI elements, pushing 50 updates a minute traps screen readers in an endless loop, rendering the page entirely unusable for visually impaired operators.

## Decision
Any frontend widget rendering high-velocity real-time data (updates occurring more than once per minute) MUST implement a user-accessible toggle that completely disables background DOM mutations and switches off `aria-live` announcements.

1. The OWL component state must track a `screenReaderMode` or `isPaused` boolean.
2. When toggled on, the component explicitly changes the DOM attribute from `aria-live="polite"` to `aria-live="off"`.
3. The incoming WebSocket payload listener must check this boolean and explicitly `return` (discarding the update) to prevent the DOM from mutating while the user is reading the static snapshot.

## Consequences
* **Positive:** Achieves strict WCAG 2.1 AA compliance for dynamic content, ensuring the platform is accessible to visually impaired hams.
* **Negative:** Paused data streams will miss historical data that flows in while paused, requiring a page refresh to grab the latest state if the cache is bypassed.
