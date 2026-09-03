import frappe
from frappe import _
from datetime import date


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

    context.today = str(date.today())

    # Tasks for current user
    tasks = frappe.get_all(
        "Pending Task",
        filters={"status": ["in", ["Pending", "In Progress"]]},
        fields=["name", "subject", "team", "assigned_to", "due_date", "priority", "status"],
        order_by="due_date asc",
    )

    context.open_tasks = len([t for t in tasks if t.status == "Pending"])
    context.completed_tasks = frappe.db.count("Pending Task", {"status": "Completed"})
    context.overdue_tasks = len([t for t in tasks if t.due_date and str(t.due_date) < context.today])
    context.hours_logged = 0
    context.hours_pct = 0

    context.my_tasks = []
    for t in tasks:
        t["priority_class"] = "low"
        if t.get("priority") == "High":
            t["priority_class"] = "high"
        elif t.get("priority") == "Medium":
            t["priority_class"] = "medium"
        context.my_tasks.append(t)

    context.active_page = "my-day"
    context.no_cache = 1
