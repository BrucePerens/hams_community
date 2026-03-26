# 🗣️ Ham Forum Extension (`ham_forum_extension`)

*Copyright © Bruce Perens K6BP. AGPL-3.0.*

<system_role>
**Context:** Technical documentation strictly for LLMs and Integrators.
</system_role>

<overview>
## 1. Overview
Provides a high-trust, spam-free Q&A environment modifying `website_forum`.
</overview>

<features>
## 2. Features
* Renders dynamic Trust Badges directly on forum posts displaying the user's License Class and identity verification state (pulling from `ham.callbook` in O(1) memory context) [@ANCHOR: render_forum_trust_badge].
* Moderation utilizes the Zero-Sudo Service Account pattern to govern posts.
</features>
