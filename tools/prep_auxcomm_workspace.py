#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

SPEC_CONTENT = """# Feature Specification: Tactical AUXCOMM Simulator

**Status:** Proposed (Ready for Architecture)
**Related Mandates:** MASTER 14 (Context Management), MASTER 11 (Agile Workflow)

## 1. Objective
To build an interactive, context-aware training simulator that translates dry federal NIMS/ICS doctrines into operational amateur radio scenarios. It moves operators away from memorizing multiple-choice answers and forces them to apply NIMS concepts in simulated, high-stress environments.

## 2. Scope of Curriculum
The simulator will integrate and contextualize the following federal frameworks:
* **IS-100 & IS-200:** Basic and Initial Action Incident Command System.
* **IS-700 & IS-800:** NIMS and the National Response Framework (specifically ESF #2).
* **IS-2200:** Basic EOC Functions.
* **IS-802.a:** Emergency Support Function (ESF) #2 — Communications.
* **IS-242.c & IS-244.b:** Effective Communication and Volunteer Management.
* **Bridges to:** ICS-300 (The Planning P), CISA AUXCOMM, SKYWARN, and CERT.

## 3. Core Engine Components

### A. The Tabletop Scenario Engine
* **Data Models Needed:** `ham.auxcomm.scenario`, `ham.auxcomm.inject`.
* **Function:** A branching, text-based simulation feeding the operator "Injects" (e.g., resource requests, infrastructure failures). The user must identify NIMS violations and route messages correctly through the ICS hierarchy.

### B. The EOC Sandbox & Message Drills
* **Integration:** Will hook into `ham_shack` and `ham_events`.
* **Function:** Users practice transcribing live, chaotic inputs into strict ICS-213 General Message forms. Simulates EOC stress by introducing audio QRM (static) or rapid, conflicting UI popups that must be triaged according to NIMS priority protocols.

### C. AI-Debunking Spaced Repetition
* **Integration:** Expands `ham.testing.progress`.
* **Function:** Uses the AI-Synthesis pipeline to generate targeted HTML explanations debunking the exact distractors a user falls for in the FEMA question pools.
"""

NEXT_SESSION_PROMPT = """You are operating in an Isolated Task Workspace per MASTER 14.

We are building a new Odoo 19 module called `ham_auxcomm_training` which acts as a Tactical AUXCOMM Simulator to teach NIMS and ICS doctrines.

Please review the specification in `docs/specs/auxcomm_simulator.md`.

Your first task is to define the PostgreSQL/ORM data models (`ham.auxcomm.scenario` and `ham.auxcomm.inject`) in Python, ensuring they adhere to the Zero-Sudo architecture and standard platform naming conventions. Generate the `models/` files and the `__manifest__.py` for this new module.
"""


def main():
    # 1. Write the specification to the current docs tree
    spec_dir = os.path.join("docs", "specs")
    os.makedirs(spec_dir, exist_ok=True)
    spec_path = os.path.join(spec_dir, "auxcomm_simulator.md")

    print(f"[*] Writing specification to {spec_path}...")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(SPEC_CONTENT)

    # 2. Invoke the workspace creator
    workspace_name = f"../auxcomm_workspace_{datetime.now().strftime('%Y%m%d_%H%M')}"
    workspace_path = os.path.abspath(workspace_name)

    print(f"[*] Invoking create_task_workspace.py -> {workspace_path}...")
    try:
        subprocess.run(
            ["python3", "tools/create_task_workspace.py", "--dest", workspace_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to generate workspace: {e}")
        return
    except FileNotFoundError:
        print("[!] tools/create_task_workspace.py not found. Are you in the repo root?")
        return

    # 3. Write the handoff prompt into the new workspace
    prompt_path = os.path.join(workspace_path, "NEXT_SESSION_PROMPT.txt")
    print(f"[*] Writing handoff prompt to {prompt_path}...")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(NEXT_SESSION_PROMPT)

    print("\n[+] Success! Your reduced workspace is ready.")
    print(f"    Navigate to: {workspace_path}")
    print("    Feed the contents of NEXT_SESSION_PROMPT.txt to your next LLM session.")


if __name__ == "__main__":
    main()
