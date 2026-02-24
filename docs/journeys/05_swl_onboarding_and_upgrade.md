# User Journey: SWL Onboarding & Automated Upgrade

## Phase 1: The Prospective Registration
A user currently studying for their amateur radio license visits the platform. They navigate to the registration portal and select the "I am studying for my license (SWL)" path. The interface dynamically hides the Ham-CAPTCHA (which requires technical knowledge they don't have yet) and the Callsign field. Instead, they provide their legal Name, Zip Code, and a desired username.

## Phase 2: The Sandboxed Experience
Upon logging in, the system automatically prepends `SWL_` to their chosen username. 
* They navigate to the **Elmering Forums** to ask questions about antenna setups. The community sees their distinct grey "Prospective Ham (SWL)" trust badge, immediately understanding their experience level.
* They visit the **Web Shack** to watch live DX spots flow in and view **Propagation Maps** to understand solar cycles.
* If they attempt to upload a fake contact log or access the Website Builder, the system politely blocks them, reminding them that these features unlock upon licensure.

## Phase 3: The License Grant
The user passes their exam, and the FCC publishes their new callsign (e.g., `KN4XYZ`) to the public ULS database on a Tuesday morning.

## Phase 4: The Automated Upgrade
That night, the platform's background `fcc_uls_sync` daemon downloads the federal database. As it processes the new records, the correlation engine notices that `KN4XYZ` belongs to a user with the exact First Name, Last Name, and Zip Code as our SWL account.
The system executes an automated upgrade:
1. It drops the `SWL_` prefix.
2. It overwrites their login and display name with `KN4XYZ`.
3. It transitions their internal status to `ham`.
4. It automatically provisions `kn4xyz.hams.com` in the DNS nameserver and unlocks their logbook.
When the user logs in on Wednesday, they are greeted by a congratulatory banner and full access to the platform.
