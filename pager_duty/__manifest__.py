{
    "name": "Pager Duty",
    "summary": "Pager duty scheduling and incident management.",
    "author": "Bruce Perens K6BP",
    "website": "https://perens.com/",
    "category": "Ham Radio",
    "post_init_hook": "post_init_hook",
    "license": "AGPL-3",
    "version": "1.0",
    "depends": [
        "base",
        "mail",
        "calendar",
        "bus",
        "zero_sudo",
        "distributed_redis_cache",
    ],
    "data": [
        "data/cron.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/incident_views.xml",
        "views/schedule_views.xml",
        "views/pager_check_views.xml",
        "views/log_analyzer_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pager_duty/static/src/components/board/board.js",
            "pager_duty/static/src/components/board/board.xml",
            "pager_duty/static/src/components/log_viewer/log_viewer.js",
            "pager_duty/static/src/components/log_viewer/log_viewer.xml",
        ]
    },
}
