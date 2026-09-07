import frappe
from frappe.utils import cint, getdate, nowdate

from epms.employee_performance.utils import (
    portal_current_scorecards,
    portal_login_redirect,
    portal_month_label,
    portal_setup_common,
)


def get_context(context):
    try:
        portal_login_redirect()
        portal_setup_common(context)

        # Filters (month / year / team) — GET params so links are shareable.
        try:
            filter_month = cint(frappe.form_dict.get("month") or getdate(nowdate()).month)
        except (TypeError, ValueError):
            filter_month = getdate(nowdate()).month
        try:
            filter_year = cint(frappe.form_dict.get("year") or getdate(nowdate()).year)
        except (TypeError, ValueError):
            filter_year = getdate(nowdate()).year
        filter_team = (frappe.form_dict.get("team") or "").strip() or None

        context.filter_month = filter_month
        context.filter_year = filter_year
        context.filter_team = filter_team
        context.current_month = getdate(nowdate()).month
        context.current_year = getdate(nowdate()).year
        context.month_label = portal_month_label(filter_month, filter_year)
        
        try:
            context.teams = frappe.get_all(
                "Team",
                filters={"status": "Active"},
                fields=["name", "team_name"],
                order_by="team_name asc",
            ) or []
        except Exception:
            context.teams = []

        try:
            scorecards = portal_current_scorecards(
                order_by="overall_score desc",
                month=filter_month,
                year=filter_year,
                team=filter_team,
            )
        except Exception:
            scorecards = []

        scores = [s.get("overall_score") or 0 for s in scorecards]
        context.total_scorecards = len(scorecards)
        context.avg_score = round(sum(scores) / len(scores), 1) if scores else 0
        context.top_score = max(scores) if scores else 0
        context.attention_count = len(
            [s for s in scorecards if s.get("performance_status") == "Needs Attention"]
        )
        context.at_risk_count = len([s for s in scorecards if s.get("performance_status") == "At Risk"])

        context.scorecards = scorecards
        context.active_page = "performance"
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + f"\nError: {str(e)}", "EPMS Performance Page")
        context.teams = []
        context.scorecards = []
        context.total_scorecards = 0
        context.avg_score = 0
        context.top_score = 0
        context.attention_count = 0
        context.at_risk_count = 0
        context.active_page = "performance"
