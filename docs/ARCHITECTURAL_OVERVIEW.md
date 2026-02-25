# System Architecture Overview

*Copyright © Bruce Perens K6BP. All Rights Reserved. This software is proprietary and confidential.*

This document explains how the Hams.com platform fits together. We built this for developers, sysadmins, and AI assistants to quickly understand our design choices, how data flows, and how we lock things down.

---

## 1. Overall System Paradigm

Hams.com is a fast, high-traffic Amateur Radio portal built on **Odoo 19 Community**. We are pushing Odoo out of its comfort zone: instead of using it as a standard back-office ERP, we are running it as a highly concurrent public community site.

---

## 2. Core Architectural Choices

### A. Offloading Heavy Work to Daemons *(See ADR-0001)*
Odoo's web workers crash or slow down if you give them massive tasks. So, we don't. We push anything heavy to standalone Python scripts (daemons) running in the background:
* **Parsing huge files:** Like multi-megabyte ADIF radio logs.
* **Live data streams:** Our DX Cluster uses WebSockets connected directly to PostgreSQL so we can handle tens of thousands of users without locking up Odoo.

### B. Security & Zero-Sudo *(See ADR-0002, ADR-0005, ADR-0006)*
We never use Odoo's `.sudo()` method in our code because it gives absolute power and causes security disasters. 
Instead, we use a **Zero-Sudo Architecture**. When a background script or API needs to do something, it logs in as a specific "Service Account." These accounts have exactly the permissions they need—and nothing more. We also actively block these service accounts from logging into the web interface, just in case their passwords leak.

### C. Proxy Ownership
We want users to build their own web pages, but giving a normal user Odoo's "Website Designer" access is dangerous. We get around this by letting the system "own" the web pages in the database, while our custom security rules give the specific user full control over their little corner of the site.

### D. Privacy & GDPR
* **Radio logs are forever:** Amateur Radio contacts (QSOs) happen on public airwaves and are public record. When a user asks us to delete their data under GDPR, we delete their profile and websites, but we keep the radio logs (we just strip their name off them).
* **Fuzzing locations:** We store exact coordinates in the database, but when we show a user on the public map, we randomly shift their pin to the center of a large regional box to protect their home address.

---

## 3. How the Modules Stack Up

### The Foundation
* **`zero_sudo`:** The security cop. It provides the safe tools we use to elevate privileges without using `.sudo()`, and locks out service accounts.
* **`ham_base`:** The core anchor. It holds shared tools and UI pieces so other modules don't constantly crash into each other.
* **`user_websites`**: Lets users build their own web pages and blogs.

### Identity & Getting Started
* **`ham_onboarding`:** Proves users are real amateur radio operators (using ARRL certificates, QRZ profiles, FCC emails, or Morse Code tests).
* **`ham_callbook`:** Our main directory of users. It constantly syncs with global government databases.

### The Apps
* **`ham_logbook`:** The main tool for logging radio contacts and checking if other operators confirm them.
* **`ham_dx_cluster`:** A live feed of radio signals worldwide. It skips writing to the database entirely to stay fast.
* **`ham_classifieds`:** A marketplace for buying and selling gear, but only verified operators can use it to stop scams.
* **`ham_shack`:** The main Web UI console users see when they log in.
* **`ham_events`:** Handles community nets, contests, and meetups.
* **`ham_satellite`:** Tells users when satellites are flying overhead.
* **`ham_forum_extension`:** A spam-free Q&A board for helping new operators.
* **`ham_propagation`:** Shows users live maps of how radio waves are bouncing around the atmosphere right now.

---

## 4. Daemons & Background Scripts

To keep the web interface fast, we run these Python scripts separately in the `daemons/` folder. They talk to Odoo via APIs or RabbitMQ.

* **`adif_processor`:** Grabs log files from the queue and saves them to the database.
* **`lotw_eqsl_sync`:** Quietly checks external sites every day to see if contacts were confirmed.
* **`noaa_swpc_sync`:** Grabs space weather data every hour.
* **`dx_firehose`:** Connects directly to the database and blasts live signal spots out to users over WebSockets.
* **`pdns_sync`:** Takes DNS changes from Odoo and pushes them to our PowerDNS servers.
* **`ham_dx_daemon`:** Stays connected to global radio networks to pull in live signal data.
* **Government Syncs (`fcc_uls_sync`, etc.):** Nightly scripts that download massive government databases to keep our callbook up to date.

---

## 5. How We Write and Track Code

We are strict about keeping our documentation tied to reality.

### Semantic Anchors *(See ADR-0004)*
Instead of saying "Look at line 45 in main.py," we put specific tags in the code like `# [%ANCHOR: check_user_login]`. Our docs point to these tags. If we move the code, we move the tag with it. This means our documentation never breaks when we refactor.

### Where to find things:
* **`docs/adrs/`:** Where we explain *why* we made big technical choices.
* **`docs/stories/`:** Exactly what a feature should do, written so we can automatically test it.
* **`docs/journeys/`:** Big-picture walkthroughs of how a user interacts with the site.
* **`docs/runbooks/`:** How-to guides for sysadmins running the servers.
* **`docs/security_models/`:** How we plan to stop hackers and spammers.
* **`CHANGELOG.md`:** The running list of what we just built or fixed.
