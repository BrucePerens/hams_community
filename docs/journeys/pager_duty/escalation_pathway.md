# Journey: Escalation Pathway

This journey describes the automated fallback mechanism when an incident is ignored or missed by the primary on-call engineer.

## 1. Monitoring Loop
- **Trigger:** The Odoo standard cron `cron_escalate_incidents` runs every minute [@ANCHOR: test_pager_escalation].
- **Sweep:** It calls `action_escalate_unacknowledged()`.

## 2. Threshold Detection
- **Filter:** The method searches for incidents where:
    - `status == 'open'` (Not yet acknowledged).
    - `is_escalated == False`.
    - `create_date` is more than 15 minutes in the past.

## 3. High-Priority Alerting
- **Identity Elevation:** The system switches to the `mail_service_internal` service account context.
- **Group Lookup:** It identifies all users in the `pager_duty.group_pager_admin` security group.
- **Broadcast:** A high-priority message is posted to the incident chatter, and all administrators are notified.
- **Marking:** `is_escalated` is set to `True` to prevent repeat escalations for the same incident.

## 4. Resolution
- **Visibility:** The escalated incident remains at the top of the NOC Dashboard until a team member acknowledges or resolves it [@ANCHOR: pager_board_data].
