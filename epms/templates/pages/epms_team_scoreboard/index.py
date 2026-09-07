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

        # Filters
        try:
            filter_month = cint(frappe.form_dict.get("month") or getdate(nowdate()).month)
        except (TypeError, ValueError):
            filter_month = getdate(nowdate()).month
        try:
            filter_year = cint(frappe.form_dict.get("year") or getdate(nowdate()).year)
        except (TypeError, ValueError):
            filter_year = getdate(nowdate()).year

        if filter_month < 1 or filter_month > 12:
            filter_month = getdate(nowdate()).month
        if filter_year < 2000 or filter_year > 2100:
            filter_year = getdate(nowdate()).year

        context.filter_month = filter_month
        context.filter_year = filter_year
        context.current_month = getdate(nowdate()).month
        context.current_year = getdate(nowdate()).year
        context.month_label = portal_month_label(filter_month, filter_year)

        # Get all active teams
        teams = frappe.get_all(
            "Team",
            filters={"status": "Active"},
            fields=["name", "team_name", "team_leader"],
            order_by="team_name asc",
        )
        context.teams = teams or []

        # Get team members count for each team
        team_data = []
        for team in teams:
            try:
                members = frappe.get_all(
                    "Team Member Mapping",
                    filters={"team": team.name, "status": "Active"},
                    fields=["user", "employee_name"],
                )
                member_count = len(members)

                # Get average score for this team from scorecards
                avg_score = frappe.db.get_value(
                    "Performance Scorecard",
                    {"team": team.name, "month": filter_month, "year": filter_year, "docstatus": 1},
                    "avg(overall_score)",
                )
                avg_score = round(frappe.utils.flt(avg_score, 1), 1) if avg_score else 0

                # Get performance status based on score
                if avg_score >= 80:
                    status = "On Track"
                elif avg_score >= 60:
                    status = "Needs Attention"
                else:
                    status = "At Risk"

                # Get team leader name
                leader_name = team.team_leader
                if team.team_leader:
                    leader_name = frappe.db.get_value("User", team.team_leader, "full_name") or team.team_leader

                team_data.append({
                    "name": team.name,
                    "team_name": team.team_name,
                    "team_leader": leader_name,
                    "member_count": member_count,
                    "avg_score": avg_score,
                    "status": status,
                })
            except Exception:
                pass

        # Sort by score descending and assign rank
        team_data.sort(key=lambda x: x["avg_score"], reverse=True)
        for i, td in enumerate(team_data):
            td["rank"] = i + 1

        context.team_data = team_data
        context.total_teams = len(team_data)
        context.avg_all_score = round(sum(td["avg_score"] for td in team_data) / len(team_data), 1) if team_data else 0

        # Top performer in each team
        for td in team_data:
            try:
                top_performer = frappe.db.get_value(
                    "Performance Scorecard",
                    {"team": td["name"], "month": filter_month, "year": filter_year, "docstatus": 1},
                    "employee_name",
                    order_by="overall_score desc",
                )
                td["top_performer"] = top_performer or "—"
            except Exception:
                td["top_performer"] = "—"

        context.active_page = "team-scoreboard"

        # Permission: can this user generate scorecards?
        user_roles = frappe.get_roles(frappe.session.user)
        context.can_generate = "EPMS Founder" in user_roles or "EPMS Team Leader" in user_roles

        # For TLs, only show their own teams; Founders see all
        if context.can_generate:
            user_teams = []
            for td in team_data:
                if "EPMS Team Leader" in user_roles and "EPMS Founder" not in user_roles:
                    tl_user = frappe.db.get_value("Team", td["name"], "team_leader")
                    if tl_user != frappe.session.user:
                        continue
                user_teams.append(td["name"])
            context.user_teams = user_teams
        else:
            context.user_teams = []
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + f"\nError: {str(e)}", "EPMS Team Scoreboard Page")
        context.teams = []
        context.team_data = []
        context.total_teams = 0
        context.avg_all_score = 0
        context.filter_month = getdate(nowdate()).month
        context.filter_year = getdate(nowdate()).year
        context.month_label = portal_month_label()
        context.active_page = "team-scoreboard"
        context.can_generate = False
        context.user_teams = []
