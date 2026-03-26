#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re

FILES_TO_FIX = [
    "daemons/ham_dx_daemon/dx_daemon.py",
    "daemons/ham_dx_daemon/README.md",
    "daemons/lotw_eqsl_sync/test_lotw_eqsl_sync.py",
    "ham_callbook/tests/test_callbook_address_edge_cases.py",
    "ham_callbook/tests/test_callbook_privacy.py",
    "ham_dx_cluster/tests/test_dx_spot.py",
    "ham_events/tests/test_contest_scoring.py",
    "ham_logbook/tests/test_live_api.py",
    "ham_logbook/tests/test_qsl_sync_edge_cases.py",
    "ham_logbook/tests/test_qso_logic.py",
    "ham_onboarding/static/tests/tours/morse_tour.js",
    "ham_onboarding/tests/test_callsign_history_edge_cases.py",
    "ham_onboarding/tests/test_captcha_signup.py",
    "ham_onboarding/tests/test_morse_tour.py",
    "ham_onboarding/tests/test_verification.py",
    "ham_testing/static/src/js/morse_ve_exam.js",
]


def migrate_n0call():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # We replace N0CALL with AB1CDE, a standard, fully compliant 2x3 test callsign
    # that doesn't trigger any 1x1, Experimental, or length constraints.
    for rel_path in FILES_TO_FIX:
        filepath = os.path.join(root_dir, rel_path)
        if not os.path.exists(filepath):
            print(f"[WARN] File not found: {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace uppercase and lowercase variations
        new_content = re.sub(r"N0CALL", "AB1CDE", content)
        new_content = re.sub(r"n0call", "ab1cde", new_content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Migrated: {rel_path}")
        else:
            print(f"➖ No changes needed (already migrated): {rel_path}")


if __name__ == "__main__":
    print("[*] Starting N0CALL test suite migration...")
    migrate_n0call()
    print("[*] Migration complete. All target files now use 'AB1CDE'.")
