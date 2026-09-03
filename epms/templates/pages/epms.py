import frappe
from frappe import _
import json


def get_context(context):
    """Dashboard page context."""
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access EPMS Portal"), frappe.DoesNotExistError)

    user = frappe.get_doc("User", frappe.session.user)
    context.user_name = user.full_name or frappe.session.user
    context.user_initial = (context.user_name[0] or "U").upper()
    context.user_role = "Team Member"
    roles = frappe.get_roles(frappe.session.user)
    if "Employee Performance Founder" in roles:
        context.user_role = "Founder"
    elif "Employee Performance Team Leader" in roles:
        context.user_role = "Team Leader"

    # Stats
    context.total_teams = frappe.db.count("Team", {"status": "Active"})
    context.active_members = frappe.db.count("Team Member Mapping", {"status": "Active"})
    context.pending_tasks = frappe.db.count("Pending Task", {"status": ["in", ["Pending", "In Progress"]]})

    avg = frappe.db.sql(
        """SELECT AVG(total_score) FROM `tabPerformance Scorecard`
        WHERE month = DATE_FORMAT(CURDATE(), '%%Y-%%m')"""
    )
    context.avg_score = round(avg[0][0] or 0, 1)

    # Today's tasks
    today_tasks = frappe.get_all(
        "Pending Task",
        filters={"status": ["in", ["Pending", "In Progress"]]},
        fields=["name", "subject", "team", "due_date", "priority", "status"],
        order_by="due_date asc",
        limit_page_length=5,
    )
    context.today_tasks = []
    for t in today_tasks:
        t["priority_class"] = "low"
        if t.get("priority") == "High":
            t["priority_class"] = "high"
        elif t.get("priority") == "Medium":
            t["priority_class"] = "medium"
        context.today_tasks.append(t)

    # Recent scores
    recent = frappe.get_all(
        "Performance Scorecard",
        fields=["name", "employee_name", "team", "month", "total_score", "grade", "status", "department"],
        order_by="modified desc",
        limit_page_length=5,
    )
    context.recent_scores = []
    for s in recent:
        s["grade_class"] = "gray"
        if s.get("grade") == "A":
            s["grade_class"] = "green"
        elif s.get("grade") == "B":
            s["grade_class"] = "blue"
        elif s.get("grade") == "C":
            s["grade_class"] = "orange"
        elif s.get("grade") == "D":
            s["grade_class"] = "red"
        context.recent_scores.append(s)

    # Top performers
    top = frappe.get_all(
        "Performance Scorecard",
        fields=["employee_name", "team", "total_score"],
        order_by="total_score desc",
        limit_page_length=5,
    )
    context.top_performers = []
    for i, p in enumerate(top):
        p["rank"] = i + 1
        p["name"] = p.get("employee_name") or "N/A"
        p["score"] = p.get("total_score") or 0
        p["rank_class"] = "silver"
        if i == 0:
            p["rank_class"] = "gold"
        elif i == 1:
            p["rank_class"] = "silver"
        elif i == 2:
            p["rank_class"] = "bronze"
        context.top_performers.append(p)

    context.active_page = "dashboard"
    context.no_cache = 1
