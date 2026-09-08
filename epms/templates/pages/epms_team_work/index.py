import frappe
from frappe.utils import cint, getdate, nowdate

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_month_label,
    portal_setup_common,
)


def get_context(context):
    try:
        portal_login_redirect()
        portal_setup_common(context)

        user = frappe.session.user
        user_roles = frappe.get_roles(user)

        if "EPMS Founder" in user_roles:
            frappe.local.flags.redirect_location = "/epms"
            raise frappe.Redirect

        context.today = str(nowdate())
        context.today_label = frappe.utils.formatdate(nowdate(), "EEEE, d MMMM yyyy")
        context.current_month = getdate(nowdate()).month
        context.current_year = getdate(nowdate()).year
        context.month_label = portal_month_label()

        # Get user's teams
        user = frappe.session.user
        user_roles = frappe.get_roles(user)

        if "EPMS Team Leader" in user_roles:
            teams = frappe.get_all(
                "Team",
                filters={"team_leader": user, "status": "Active"},
                fields=["name", "team_name"],
                order_by="team_name asc",
            )
        elif "EPMS Team Member" in user_roles:
            team_names = frappe.get_all(
                "Team Member Mapping",
                filters={"user": user, "status": "Active"},
                pluck="team",
            )
            if team_names:
                teams = frappe.get_all(
                    "Team",
                    filters={"name": ["in", team_names], "status": "Active"},
                    fields=["name", "team_name"],
                    order_by="team_name asc",
                )
            else:
                teams = []
        else:
            teams = []
        context.teams = teams or []

        # Get team members for the selected team (if any)
        selected_team = frappe.form_dict.get("team") or (teams[0].name if teams else None)
        context.selected_team = selected_team

        if selected_team:
            try:
                members = frappe.get_all(
                    "Team Member Mapping",
                    filters={"team": selected_team, "status": "Active"},
                    fields=["name", "user", "employee_name", "designation"],
                    order_by="employee_name asc",
                )
                context.members = members or []
            except Exception:
                context.members = []
            context.member_count = len(context.members)
        else:
            context.members = []
            context.member_count = 0

        # Check if already submitted for today
        member_users = [m.get("user") for m in context.members if m.get("user")]
        context.submitted_employees = set()
        if member_users:
            try:
                existing_entries = frappe.get_all(
                    "Daily Performance",
                    filters={
                        "employee": ["in", member_users],
                        "date": nowdate(),
                        "docstatus": ["!=", 2],
                    },
                    fields=["name", "employee", "docstatus"],
                )
                for entry in existing_entries:
                    if entry.get("docstatus") == 1:
                        context.submitted_employees.add(entry.get("employee"))
            except Exception:
                pass

        context.can_submit = "EPMS Team Leader" in user_roles
        context.active_page = "team-work"
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + f"\nError: {str(e)}", "EPMS Team Work Page")
        context.today = str(nowdate())
        context.today_label = frappe.utils.formatdate(nowdate(), "EEEE, d MMMM yyyy")
        context.current_month = getdate(nowdate()).month
        context.current_year = getdate(nowdate()).year
        context.month_label = portal_month_label()
        context.teams = []
        context.members = []
        context.selected_team = None
        context.member_count = 0
        context.submitted_employees = set()
        context.can_submit = False
        context.active_page = "team-work"
