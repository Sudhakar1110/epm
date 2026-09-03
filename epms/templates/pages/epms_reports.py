import frappe
from frappe import _


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login"))

    user = frappe.get_doc("User", frappe.session.user)
    context.user_name = user.full_name or frappe.session.user
    context.user_initial = (context.user_name[0] or "U").upper()
    context.user_role = "Team Member"
    roles = frappe.get_roles(frappe.session.user)
    if "Employee Performance Founder" in roles:
        context.user_role = "Founder"
    elif "Employee Performance Team Leader" in roles:
        context.user_role = "Team Leader"

    context.reports = [
        {"name": "Daily Performance Report", "description": "Daily performance summary for all employees", "icon_class": "stat-icon green"},
        {"name": "Monthly Performance Report", "description": "Monthly performance overview and trends", "icon_class": "stat-icon blue"},
        {"name": "Employee Wise Report", "description": "Performance data filtered by employee", "icon_class": "stat-icon purple"},
        {"name": "Team Wise Report", "description": "Team-level performance comparison", "icon_class": "stat-icon orange"},
        {"name": "Pending Task Report", "description": "Overview of all pending tasks and deadlines", "icon_class": "stat-icon red"},
        {"name": "Top Performers", "description": "List of top performing employees", "icon_class": "stat-icon green"},
        {"name": "Low Performers", "description": "Employees needing improvement support", "icon_class": "stat-icon red"},
        {"name": "Monthly KPI Report", "description": "Key performance indicators by month", "icon_class": "stat-icon blue"},
        {"name": "Leaderboard Report", "description": "Employee ranking leaderboard", "icon_class": "stat-icon purple"},
        {"name": "Daily Summary Report", "description": "Complete daily summary across teams", "icon_class": "stat-icon orange"},
    ]

    context.active_page = "reports"
    context.no_cache = 1
