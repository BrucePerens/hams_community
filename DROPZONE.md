=== SYSTEM DIRECTIVE FOR AI ASSISTANT: DROPZONE ARCHITECTURE ===

# Context & Architectural Mandate
You are an expert AI developer operating in our strict, exact-execution DevSecOps environment. 

We are enforcing a strict **Open Source Isolation Mandate** for the `user_websites` module. Downstream proprietary modules (such as `ham_logbook`, `ham_shack`, and `ham_classifieds`) need to inject domain-specific widgets (e.g., "Last QSO displays", "Recent Classifieds", "DX Cluster maps") into the personal websites provisioned by the `user_websites` module. 

To prevent monolithic entanglement, `user_websites` MUST NOT contain any hardcoded references to these downstream features. Instead, we use the **Dropzone Pattern**: `user_websites` must provide explicitly named, empty structural containers (`<div>` tags) specifically designed for downstream modules to target via `<xpath>`.

# Your Immediate Task
Your objective is to define and implement the explicit structural "Dropzones" within the `user_websites` XML templates. 

Please execute the following steps:

### 1. Identify & Inject Structural Dropzones
Analyze the frontend UI layout of `user_websites` (e.g., the user profile page, the blog index, the site header/footer). Inject empty `<div>` containers into these templates to serve as stable hooks. 
* **Requirement:** Each dropzone MUST have a highly specific, globally unique `id` attribute (e.g., `id="user_websites_dropzone_profile_header"` or `id="user_websites_dropzone_sidebar"`). 
* **Constraint:** Do not use generic classes like `card` as targets, as they are flagged as fragile by the AST linter.

### 2. Establish Semantic Anchors
For each Dropzone you create in the XML, you MUST assign a unique Semantic Anchor as an HTML comment directly inside the `<template>` or dropzone container (e.g., ``).

### 3. Update the API Contract
You must output a patch for the `docs/modules/user_websites.md` (or `LLM_DOCUMENTATION.md`) API contract. 
* Add a new subsection under "Public API & Extensibility Methods" detailing the newly created Dropzones.
* Explicitly list the exact `id` of each dropzone and the mandatory Semantic Anchor that downstream modules MUST cite when injecting their `<xpath>` payloads.

# Execution Constraints
* You MUST deliver all file modifications using the strict **Parcel transport schema** (wrapped in at least 4 backticks of type `python`).
* You MUST URL-encode angle brackets (`%3C`, `%3E`) for all vulnerable XML comments to survive Web UI extraction.
* For files under 500 lines, use the unabridged `overwrite` operation. 

Please acknowledge these instructions and provide your proposed XML Dropzone locations and the API contract updates.
