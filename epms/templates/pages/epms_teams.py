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

    teams = frappe.get_all(
        "Team",
        fields=["name", "team_name", "team_leader", "status"],
        order_by="team_name asc",
    )

    context.teams = []
    for t in teams:
        t["member_count"] = frappe.db.count("Team Member Mapping", {"team": t.name})
        context.teams.append(t)

    context.active_page = "teams"
    context.no_cache = 1
