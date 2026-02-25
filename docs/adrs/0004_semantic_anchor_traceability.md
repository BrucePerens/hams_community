# ADR 0004: Semantic Anchor Traceability

## Status
Accepted

## Context
To maintain sync between Agile documentation (Stories, Journeys) and execution logic, we need to map requirements directly to code. Relying on file line numbers is incredibly brittle, as routine refactoring breaks the links. Relying on internal AI citation tags (e.g., ``) is completely ineffective, as these markers are ephemeral artifacts of context ingestion that do not persist across developer sessions.

## Decision
We will implement a Semantic Anchor Architecture. Developers and AI agents MUST inject explicit string anchors directly into the source code at critical execution points.
* Format: `# [%ANCHOR: unique_name]` (Python), `// [%ANCHOR: unique_name]` (JS), or `<!-- [%ANCHOR: unique_name] -->` (XML/HTML).
* Documentation must reference these anchors using the explicit format: `*(Reference: path/to/file.py -> method_name -> [%ANCHOR: unique_name])*`.
* LLM context protocols mandate that these anchors are actively scanned, preserved during refactoring, and mapped when creating new features.

## CI/CD Enforcement
To prevent silent breakage, the `tools/verify_anchors.py` script MUST run during the automated test pipeline. If an anchor is referenced in `docs/` but cannot be found in the application source code, the build MUST fail.

## Consequences
* **Positive:** Creates an unbreakable, mathematically verifiable traceability matrix. Eliminates LLM "feature amnesia" by legally binding the AI to read the anchor's business logic before modifying code.
* **Negative:** Requires strict developer and AI discipline to ensure anchors are not accidentally deleted and are moved alongside their respective logic blocks during deep refactoring.
