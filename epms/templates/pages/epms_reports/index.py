from epms.employee_performance.utils import portal_login_redirect, portal_setup_common


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    icon_set = ["icon-teal", "icon-blue", "icon-purple", "icon-amber", "icon-red", "icon-green"]
    reports = [
        {"name": "Daily Performance Report", "description": "Daily performance summary for every employee"},
        {"name": "Monthly Performance Report", "description": "Monthly performance overview and trends"},
        {"name": "Employee Wise Report", "description": "Performance data filtered by employee"},
        {"name": "Team Wise Report", "description": "Team-level performance comparison"},
        {"name": "Pending Task Report", "description": "Overview of pending tasks and deadlines"},
        {"name": "Top Performers", "description": "Ranked list of the highest performers"},
        {"name": "Low Performers", "description": "Employees who may need improvement support"},
        {"name": "Monthly KPI Report", "description": "Key performance indicators by month"},
        {"name": "Leaderboard Report", "description": "Employee ranking leaderboard"},
        {"name": "Daily Summary Report", "description": "Complete daily summary across all teams"},
    ]

    context.reports = []
    for i, r in enumerate(reports):
        r["url"] = "/app/query-report/" + r["name"].replace(" ", "%20")
        r["icon_class"] = icon_set[i % len(icon_set)]
        context.reports.append(r)

    context.active_page = "reports"
