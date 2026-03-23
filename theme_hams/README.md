Hams.com Theme (theme_hams)
===========================

*Copyright © Bruce Perens K6BP. All Rights Reserved.*

*This software is proprietary and confidential.*

Overview
--------
A dedicated Odoo 19 theme module that applies a kitschy, ham-radio-inspired aesthetic to the entire Hams.com platform. It acts as an overlay layer on top of standard Bootstrap 5, transforming Odoo's clean corporate look into a rugged, hardware-focused design.

Design Elements
---------------

* **Morse Code Borders:** Replaces standard "hr" HTML usage with an SVG-powered border that literally spells out WELCOME TO HAMS.COM.
* **Hardware Color Palette:** Heavy use of Military Olive Drab (#4a5d23), Amber Vacuum Tube Glow (#ff9900), and Matte Black (#1a1a1a).
* **Perforated Speaker Grille:** A pure-CSS radial gradient applied to the body tag creates the illusion of an old metal radio grille behind the main content.
* **Tactile Buttons:** Push-buttons are styled with a thick 3D bottom border that visually depresses when clicked.
* **Digital Displays:** A "digital-display" utility class allows content creators to style text as glowing VFD/LCD screens.

Installation
------------
Install via the Odoo Apps menu. Ensure website and user_websites are installed prior. Once installed, the theme will automatically overwrite the primary SCSS variables and inject the layout overrides globally.
