# ADR 0056: Clear, Conversational, and Direct Writing Style

## Status
Accepted

## Context
AI assistants and developers often fall into the trap of writing in an "oblique" tone. This means using passive voice, abstract nouns, and dense corporate or academic jargon (e.g., "This module acts as the centralized infrastructure for multi-tenant content provisioning"). While people often mistake this for being "professional," it is actually an anti-pattern that impedes communication, slows down onboarding, and makes documentation exhausting to read.

## Decision
All documentation, READMEs, pull requests, and code comments MUST be written in a clear, conversational, and direct tone. 

1. **Use Active Voice:** Say "This module deletes user data," not "Data erasure is handled by this module."
2. **Be Direct:** Explain exactly what something does in plain English. Avoid abstract architectural jargon when a simple explanation works better.
3. **Ban Oblique AI-isms:** Do not use phrases like "It is a testament to," "It serves as the foundational layer for," "Infrastructure for managing," or "It enables decentralized creation." 
4. **Speak to the Reader:** Write as if you are explaining the system to a capable coworker sitting next to you. It is okay to be conversational as long as you are concise.

## Consequences
* **Positive:** Code and documentation become highly readable. Developers can instantly understand the purpose of a module or function without translating jargon.
* **Negative:** Requires the LLM to actively fight its training bias, which naturally defaults to formal, oblique, and verbose writing.
