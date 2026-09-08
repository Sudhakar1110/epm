import frappe
from frappe.utils import getdate, nowdate

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    try:
        user_roles = frappe.get_roles(frappe.session.user)

        me = frappe.session.user
        today = getdate(nowdate())

        context.today = str(today)
        context.today_label = frappe.utils.formatdate(today, "EEEE, d MMMM yyyy")

        if "EPMS Founder" in user_roles or "EPMS Team Leader" in user_roles:
            if "EPMS Founder" in user_roles:
                teams = frappe.get_all(
                    "Team",
                    filters={"status": "Active"},
                    fields=["name", "team_name"],
                    order_by="team_name asc",
                )
            else:
                teams = frappe.get_all(
                    "Team",
                    filters={"team_leader": me, "status": "Active"},
                    fields=["name", "team_name"],
                    order_by="team_name asc",
                )

            team_names = [t.name for t in teams]
            members = []
            if team_names:
                members = frappe.get_all(
                    "Team Member Mapping",
                    filters={"team": ["in", team_names], "status": "Active"},
                    fields=["user", "employee_name", "team"],
                    order_by="employee_name asc",
                )

            submitted_today = {}
            if members:
                member_users = [m.user for m in members]
                entries = frappe.get_all(
                    "Daily Performance",
                    filters={
                        "employee": ["in", member_users],
                        "date": today,
                        "docstatus": ["!=", 2],
                    },
                    fields=["employee", "task_title", "docstatus"],
                )
                for e in entries:
                    submitted_today[e.employee] = {
                        "task_title": e.task_title,
                        "submitted": e.docstatus == 1,
                    }

            member_list = []
            for m in members:
                status_info = submitted_today.get(m.user)
                member_list.append({
                    "user": m.user,
                    "employee_name": m.employee_name or m.user,
                    "team": m.team,
                    "logged": status_info is not None and status_info.get("submitted", False),
                    "task_title": status_info.get("task_title", "") if status_info else "",
                })

            context.members = member_list
            context.total_members = len(member_list)
            context.logged_count = sum(1 for m in member_list if m["logged"])
            context.pending_count = context.total_members - context.logged_count
        else:
            # Team Member: show own submission status only
            today_entry = frappe.db.get_value(
                "Daily Performance",
                {"employee": me, "date": today, "docstatus": ["!=", 2]},
                ["name", "task_title", "docstatus"],
                as_dict=True,
            )
            submitted = today_entry and today_entry.docstatus == 1
            context.members = [{
                "user": me,
                "employee_name": frappe.db.get_value("User", me, "full_name") or me,
                "team": "",
                "logged": submitted,
                "task_title": today_entry.task_title if today_entry else "",
            }]
            context.total_members = 1
            context.logged_count = 1 if submitted else 0
            context.pending_count = 0 if submitted else 1
    except frappe.Redirect:
        raise
    except Exception:
        context.members = []
        context.total_members = 0
        context.logged_count = 0
        context.pending_count = 0
    context.active_page = "my-day"
