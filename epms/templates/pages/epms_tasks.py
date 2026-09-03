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

    tasks = frappe.get_all(
        "Pending Task",
        fields=["name", "subject", "team", "assigned_to", "due_date", "priority", "status"],
        order_by="due_date asc",
    )

    context.tasks = []
    for t in tasks:
        t["priority_class"] = "low"
        if t.get("priority") == "High":
            t["priority_class"] = "high"
        elif t.get("priority") == "Medium":
            t["priority_class"] = "medium"

        t["status_class"] = "gray"
        if t.status == "Completed":
            t["status_class"] = "green"
        elif t.status == "In Progress":
            t["status_class"] = "blue"
        elif t.status == "Pending":
            t["status_class"] = "orange"
        context.tasks.append(t)

    context.active_page = "tasks"
    context.no_cache = 1
