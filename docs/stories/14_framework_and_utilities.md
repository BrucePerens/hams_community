# Epics & User Stories: Framework & Utilities

## Epic: Automated Documentation Injection
* **Story:** As a platform architect, I want every module to automatically push its technical manual into the Knowledge base upon installation, so developers have an immediate, on-board reference without searching through GitHub.
    * **BDD Criteria:**
        * *Given* the installation of any proprietary `ham_` module
        * *When* the `post_init_hook` executes
        * *Then* it MUST read the `data/documentation.html` file and create/update a `knowledge.article` record.
        * *Implementation Context:*
            * The Testing & CAPTCHA manual is injected by `ham_testing` [@ANCHOR: doc_inject_ham_testing].
            * The Identity & Onboarding manual is injected by `ham_onboarding` [@ANCHOR: doc_inject_ham_onboarding].
            * The Callbook directory manual is injected by `ham_callbook` [@ANCHOR: doc_inject_ham_callbook].
            * The Logbook & ADIF manual is injected by `ham_logbook` [@ANCHOR: doc_inject_ham_logbook].
            * The Club Management manual is injected by `ham_club_management` [@ANCHOR: doc_inject_ham_club_management].
            * The Site Initialization manual is injected by `ham_init` [@ANCHOR: doc_inject_ham_init].
            * The Events & Nets manual is injected by `ham_events` [@ANCHOR: doc_inject_ham_events].
            * The Satellite Tracker manual is injected by `ham_satellite` [@ANCHOR: doc_inject_ham_satellite].
            * The DNS Management manual is injected by `ham_dns` [@ANCHOR: doc_inject_ham_dns].
            * The Classifieds Marketplace manual is injected by `ham_classifieds` [@ANCHOR: doc_inject_ham_classifieds].
            * The DX Cluster manual is injected by `ham_dx_cluster` [@ANCHOR: doc_inject_ham_dx_cluster].
            * The Repeater Directory manual is injected by `ham_repeater_dir` [@ANCHOR: doc_inject_ham_repeater_dir].
            * The Web Shack operating console manual is injected by `ham_shack` [@ANCHOR: doc_inject_ham_shack].
            * The Live Propagation Maps manual is injected by `ham_propagation` [@ANCHOR: doc_inject_ham_propagation].
            * The Tactical AUXCOMM Simulator manual is injected by `ham_auxcomm_training` [@ANCHOR: doc_inject_ham_auxcomm].
