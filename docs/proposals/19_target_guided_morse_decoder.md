# Proposal 19: Target-Guided Morse Decoder

## 1. Architectural Context
The current Morse Code verification challenge uses a naive k-means clustering algorithm to determine the threshold between dots and dashes based solely on the user's tapped durations. Network latency, keyboard ghosting, and natural human error (a "bad fist") frequently cause the clustering algorithm to misinterpret the input, forcing legitimate operators to retry multiple times.

## 2. Integration Design

### A. Heuristic Mapping
**Targets:** `ham_onboarding/static/src/js/morse_challenge.js`
* **The Fix:** The JavaScript component already knows the target callsign (e.g., `W1AW`). The script must be updated to translate this callsign into its expected elemental composition (e.g., 5 dots, 8 dashes).
* **Guided Classification:** When the user finishes tapping, the algorithm counts the total number of key-down elements (`marks`). 
    * If the element count exactly matches the expected count (e.g., 13 elements), the algorithm simply sorts the array of durations. It designates the longest 8 elements as dashes and the shortest 5 as dots. This mathematically guarantees correct decoding even if the user's timing fluctuates wildly during the transmission.
    * If the element count is mismatched (indicating extra or missing taps), it falls back to a weighted clustering algorithm seeded by the expected ratio, rather than arbitrary min/max limits.

## 3. BDD Acceptance Criteria
* **Story:** As an operator with a poor physical keying rhythm, I want the system to understand what I am trying to send based on context.
    * *Given* a target callsign with known elements (e.g., `N0CALL` = 11 dashes, 5 dots)
    * *When* the user inputs exactly 16 marks with highly erratic durations
    * *Then* the `_decode` function MUST assign the 11 longest marks as dashes and the 5 shortest as dots, bypassing the standard k-means threshold and returning a successful match.
