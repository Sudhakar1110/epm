app_name = "epms"
app_title = "Employee Performance Management System"
app_publisher = "EPMS Team"
app_description = "Employee Performance Management System for ERPNext v15"
app_email = "epms@example.com"
app_license = "MIT"

# Includes
app_include_css = "/assets/epms/css/epms.css"
app_include_js = "/assets/epms/js/epms.js"

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
        "on_submit": "epms.epms.doctype.daily_performance.daily_performance.on_submit",
        "on_cancel": "epms.epms.doctype.daily_performance.daily_performance.on_cancel",
        "validate": "epms.epms.doctype.daily_performance.daily_performance.validate",
    },
    "Pending Task": {
        "on_submit": "epms.epms.doctype.pending_task.pending_task.on_submit",
        "on_cancel": "epms.epms.doctype.pending_task.pending_task.on_cancel",
    },
    "Performance Scorecard": {
        "on_submit": "epms.epms.doctype.performance_scorecard.performance_scorecard.on_submit",
    },
    "Team Member Mapping": {
        "on_update": "epms.epms.doctype.team_member_mapping.team_member_mapping.on_update",
    },
}

# Scheduler Events
scheduler_events = {
    "daily": [
        "epms.epms.tasks.daily_tasks",
        "epms.epms.tasks.send_pending_task_reminders",
        "epms.epms.tasks.send_late_update_reminders",
    ],
    "daily_long": [
        "epms.epms.tasks.recalculate_scorecards",
    ],
    "weekly": [
        "epms.epms.tasks.send_weekly_summary",
        "epms.epms.tasks.send_low_performance_alerts",
    ],
    "monthly": [
        "epms.epms.tasks.generate_monthly_scorecards",
        "epms.epms.tasks.send_monthly_summary",
    ],
}

# Website Routes
website_redirects = []

# Jinja
jinja = {
    "methods": [
        "epms.epms.utils.get_employee_performance_summary",
        "epms.epms.utils.get_team_summary",
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
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Notification",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Print Format",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Dashboard Chart",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Workspace",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
]

# Has Permission
has_permission = {
    "Daily Performance": "epms.epms.doctype.daily_performance.daily_performance.has_permission",
    "Pending Task": "epms.epms.doctype.pending_task.pending_task.has_permission",
    "Performance Scorecard": "epms.epms.doctype.performance_scorecard.performance_scorecard.has_permission",
    "Team": "epms.epms.doctype.team.team.has_permission",
    "Team Member Mapping": "epms.epms.doctype.team_member_mapping.team_member_mapping.has_permission",
}

# Before Insert
before_insert = {
    "Daily Performance": "epms.epms.doctype.daily_performance.daily_performance.before_insert",
}

# After Insert
after_insert = {
    "Daily Performance": "epms.epms.doctype.daily_performance.daily_performance.after_insert",
}

# Extend Bootinfo
extend_bootinfo = "epms.epms.utils.boot_session"

# Notification Config
notification_config = "epms.epms.notification.get_notification_config"

# Setup
after_install = "epms.epms.setup.after_install"
after_migrate = "epms.epms.setup.after_migrate"

# Whitelisted Methods
whitelisted_methods = [
    "epms.epms.api.get_employee_performance",
    "epms.epms.api.get_monthly_scorecard",
    "epms.epms.api.get_team_performance",
    "epms.epms.api.get_leaderboard",
    "epms.epms.api.get_daily_performance_chart",
    "epms.epms.api.get_monthly_trend_chart",
    "epms.epms.api.get_performance_distribution",
]
