# -*- coding: utf-8 -*-
{
    "name": "Test Tours Infrastructure",
    "summary": "Testing infrastructure module to cleanly inject web_tour assets.",
    "author": "Bruce Perens K6BP",
    "category": "Hidden",
    "version": "1.0",
    "license": "AGPL-3",
    "depends": ["base", "web", "web_tour"],
    "assets": {
        "web.assets_tests": [
            "test_tours/static/src/js/tour_failure_dump.js",
        ],
    },
    "installable": True,
    "auto_install": False,
}
