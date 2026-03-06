{
    "name": "Pager Duty",
    "summary": "Pager duty scheduling and incident management.",
    "author": "Bruce Perens K6BP",
    "website": "https://perens.com/",
    "category": "Ham Radio",
    "license": "AGPL-3",
    "version": "1.0",
    "depends": ["base", "mail", "calendar", "bus", "zero_sudo", "distributed_redis_cache"],
    "data": [
        "data/cron.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/incident_views.xml",
        "views/schedule_views.xml",
        "wizard/pager_config_wizard_views.xml",
        "views/pager_check_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pager_duty/static/src/components/board/board.js",
            "pager_duty/static/src/components/board/board.xml",
        ]
    },
}
