app_name = "epms"
app_title = "Employee Performance Management System"
app_publisher = "EPMS Team"
app_description = "Employee Performance Management System for ERPNext v15"
app_email = "epms@example.com"
app_license = "MIT"

# Dependencies
required_apps = ["erpnext"]

# User Data Privacy
user_data_fields = [
    {
        "doctype": "Daily Performance",
        "fieldname": ["employee", "employee_name", "remarks", "challenges", "next_day_plan"],
    },
    {
        "doctype": "Performance Scorecard",
        "fieldname": ["employee", "employee_name", "performance_status", "remarks"],
    },
    {
        "doctype": "Pending Task",
        "fieldname": ["employee", "task", "reason", "remarks"],
    },
]

# Document Events
doc_events = {
    "Daily Performance": {
        "on_submit": "epms.employee_performance.doctype.daily_performance.daily_performance.on_submit",
        "on_cancel": "epms.employee_performance.doctype.daily_performance.daily_performance.on_cancel",
        "validate": "epms.employee_performance.doctype.daily_performance.daily_performance.validate",
    },
    "Pending Task": {
        "on_submit": "epms.employee_performance.doctype.pending_task.pending_task.on_submit",
        "on_cancel": "epms.employee_performance.doctype.pending_task.pending_task.on_cancel",
    },
    "Performance Scorecard": {
        "on_submit": "epms.employee_performance.doctype.performance_scorecard.performance_scorecard.on_submit",
    },
    "Team Member Mapping": {
        "on_update": "epms.employee_performance.doctype.team_member_mapping.team_member_mapping.on_update",
    },
}

# Scheduler Events
scheduler_events = {
    "daily": [
        "epms.employee_performance.tasks.daily_tasks",
        "epms.employee_performance.tasks.send_pending_task_reminders",
        "epms.employee_performance.tasks.send_late_update_reminders",
    ],
    "daily_long": [
        "epms.employee_performance.tasks.recalculate_scorecards",
    ],
    "weekly": [
        "epms.employee_performance.tasks.send_weekly_summary",
        "epms.employee_performance.tasks.send_low_performance_alerts",
        "epms.employee_performance.tasks.send_email_reports",
    ],
    "monthly": [
        "epms.employee_performance.tasks.generate_monthly_scorecards",
        "epms.employee_performance.tasks.send_monthly_summary",
    ],
}

# Website Routes
website_redirects = []

# Jinja
jinja = {
    "methods": [
        "epms.employee_performance.utils.get_employee_performance_summary",
        "epms.employee_performance.utils.get_team_summary",
    ],
}

# Fixtures
fixtures = [
    {
        "dt": "Role",
        "filters": [
            ["name", "in", ["EPMS Founder", "EPMS Team Leader", "EPMS Team Member"]]
        ],
    },
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Notification",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Print Format",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Dashboard Chart",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Number Card",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Dashboard",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Workflow",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
    {
        "dt": "Kanban Board",
        "filters": [
            ["module", "=", "Employee Performance"],
        ],
    },
]

# Has Permission
has_permission = {
    "Daily Performance": "epms.employee_performance.doctype.daily_performance.daily_performance.has_permission",
    "Pending Task": "epms.employee_performance.doctype.pending_task.pending_task.has_permission",
    "Performance Scorecard": "epms.employee_performance.doctype.performance_scorecard.performance_scorecard.has_permission",
    "Team": "epms.employee_performance.doctype.team.team.has_permission",
    "Team Member Mapping": "epms.employee_performance.doctype.team_member_mapping.team_member_mapping.has_permission",
}

# Before Migrate
before_migrate = "epms.employee_performance.setup.before_migrate"

# After Install
after_install = "epms.employee_performance.setup.after_install"

# After Migrate
after_migrate = "epms.employee_performance.setup.after_migrate"

# Extend Bootinfo
extend_bootinfo = "epms.employee_performance.utils.boot_session"

# Notification Config
notification_config = "epms.employee_performance.notification.get_notification_config"

# Whitelisted Methods
whitelisted_methods = [
    "epms.employee_performance.api.get_employee_performance",
    "epms.employee_performance.api.get_monthly_scorecard",
    "epms.employee_performance.api.get_team_performance",
    "epms.employee_performance.api.get_leaderboard",
    "epms.employee_performance.api.get_daily_performance_chart",
    "epms.employee_performance.api.get_monthly_trend_chart",
    "epms.employee_performance.api.get_performance_distribution",
    "epms.employee_performance.api.get_portal_stats",
    "epms.employee_performance.api.get_portal_teams",
    "epms.employee_performance.api.get_portal_scorecards",
    "epms.employee_performance.api.get_portal_tasks",
    "epms.employee_performance.api.get_portal_top_performers",
    "epms.employee_performance.api.get_portal_notifications",
    "epms.employee_performance.api.set_portal_notifications_read",
    "epms.employee_performance.api.create_portal_team",
]

# Website
website_route_rules = [
    {"from_route": "/epms", "to_route": "epms", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/my-day", "to_route": "epms_my_day", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/teams", "to_route": "epms_teams", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/performance", "to_route": "epms_performance", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/tasks", "to_route": "epms_tasks", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/scorecards", "to_route": "epms_scorecards", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/reports", "to_route": "epms_reports", "defaults": {"allow_guest": 1}},
    {"from_route": "/epms/report", "to_route": "epms_report", "defaults": {"allow_guest": 1}},
]
