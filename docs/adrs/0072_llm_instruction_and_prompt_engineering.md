# ADR 0072: LLM Instruction & Prompt Engineering Standards

## Status
Accepted

## Context
The platform relies heavily on Large Language Models (LLMs) executing within restricted Web UI environments (like Canvas or generic chat interfaces). These underlying environments inject strong, generic base system instructions into the LLM's context window (e.g., "always use Firebase for storage," "bundle all web code into a single file," "maintain a bubbly, conversational tone"). These generic assumptions fundamentally conflict with this platform's strict DevSecOps, PostgreSQL/Odoo, and exact-execution mandates.

To ensure the LLM consistently adheres to our architectural boundaries without internal probabilistic conflict, we must codify specific prompt engineering techniques that explicitly exploit the LLM's attention mechanism.

## Decision
We mandate the following prompt engineering protocols for all meta-prompts, instruction files (e.g., `AGENTS.md`), and developer interactions:

### 1. The "SYSTEM OVERRIDE" Directive
To resolve conflicts between the LLM's base instructions and the platform's architecture, instructions MUST use the explicit, capitalized prefix `SYSTEM OVERRIDE:`.
* **Why it works:** This creates a highly concentrated semantic signal. It explicitly informs the neural network that the human developer is aware of the base rule and is forcefully commanding the model to prioritize the new rule. It provides the LLM "permission" to ignore its native constraints without triggering internal logic loops.

### 2. Positive Constraints (The Anti-Pink Elephant Rule)
Instructions MUST utilize deterministic positive framing.
* **Why it works:** LLMs struggle with purely negative constraints (e.g., "Don't use Firebase") because the prompt cognitively activates the tokens associated with the forbidden concept, increasing the probability of hallucination. Negative constraints must always be paired with a definitive positive path (e.g., "Do NOT use Firebase. All state persistence MUST be handled strictly via Odoo's native PostgreSQL ORM").

### 3. Persona Framing
System instructions must explicitly declare the LLM's role (e.g., *"You are an expert AI developer assistant operating in a strict, exact-execution environment"*).
* **Why it works:** This fundamentally shifts the LLM's internal vocabulary probabilities away from a "helpful chatbot" persona and toward a "rigid technical executor," naturally suppressing conversational filler and unprompted explanations.

### 4. Recency Bias Utilization
Critical execution constraints, particularly those governing output formatting (like the MIME-like Parcel schema), must be placed at the very end of instruction documents or user prompts.
* **Why it works:** LLMs possess a recency bias, weighing the most recently processed tokens heaviest during generation.

### 5. Structural Delimiters
Code, logs, and distinct rule sets must be isolated using clear boundaries (e.g., `---`, `===`, or explicit markdown headers).
* **Why it works:** Delimiters help the LLM perfectly separate meta-instructions from the actual payload data it is analyzing, preventing instruction bleed.

## Consequences
* LLMs behave predictably and adhere strictly to Odoo DevSecOps paradigms despite conflicting generic base instructions.
* Drastic reduction in hallucinated frameworks (e.g., Firebase, React) and UI-induced data loss (e.g., Canvas/Panel auto-generation errors).
* Developers interacting with the LLM have a documented framework for regaining control when the AI drifts back toward its base programming.
