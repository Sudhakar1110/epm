import frappe
from frappe.utils import flt, getdate, nowdate

from epms.employee_performance.utils import (
    portal_annotate_scorecard,
    portal_current_scorecards,
    portal_grade_distribution,
    portal_login_redirect,
    portal_month_label,
    portal_month_trend,
    portal_open_tasks,
    portal_setup_common,
)


def get_context(context):
    try:
        portal_login_redirect()
        portal_setup_common(context)

        today = getdate(nowdate())

        # Stats
        try:
            context.total_teams = frappe.db.count("Team", {"status": "Active"})
        except Exception:
            context.total_teams = 0
        try:
            context.active_members = frappe.db.count("Team Member Mapping", {"status": "Active"})
        except Exception:
            context.active_members = 0
        try:
            context.pending_tasks = frappe.db.count(
                "Daily Performance",
                filters={"docstatus": 1, "date": today},
            )
        except Exception:
            context.pending_tasks = 0
        try:
            avg_score = frappe.db.get_value(
                "Performance Scorecard",
                {"month": today.month, "year": today.year, "docstatus": 1},
                "avg(overall_score)",
            )
            context.avg_score = round(flt(avg_score, 1) if avg_score else 0, 1)
        except Exception:
            context.avg_score = 0

        context.month_label = portal_month_label()
        context.current_year_label = str(today.year)

        # Daily performance entries across the portal
        try:
            context.open_tasks = frappe.get_all(
                "Daily Performance",
                filters={"docstatus": 1},
                fields=["name", "task_title", "employee_name", "team", "task_status"],
                order_by="modified desc",
                limit_page_length=6,
            ) or []
        except Exception:
            context.open_tasks = []

        # Top performers (current month)
        try:
            top = portal_current_scorecards(limit=5)
            for i, p in enumerate(top):
                p["rank"] = i + 1
                p["rank_class"] = "gold" if i == 0 else ("silver" if i == 1 else ("bronze" if i == 2 else "plain"))
            context.top_performers = top
        except Exception:
            context.top_performers = []

        # Recently updated scorecards
        try:
            recent = frappe.get_all(
                "Performance Scorecard",
                filters={"docstatus": 1},
                fields=[
                    "name",
                    "employee_name",
                    "team",
                    "month",
                    "year",
                    "overall_score",
                    "final_grade",
                    "performance_status",
                ],
                order_by="modified desc",
                limit_page_length=5,
            )
            context.recent_scorecards = [portal_annotate_scorecard(r) for r in recent]
        except Exception:
            context.recent_scorecards = []

        # Charts
        try:
            context.trend = portal_month_trend()
        except Exception:
            context.trend = []
        try:
            context.distribution = portal_grade_distribution()
        except Exception:
            context.distribution = {"grades": {}, "total": 0, "month_label": ""}

        context.active_page = "dashboard"
    except Exception as e:
        frappe.log_error(frappe.get_traceback() + f"\nError: {str(e)}", "EPMS Dashboard Page")
        context.total_teams = 0
        context.active_members = 0
        context.pending_tasks = 0
        context.avg_score = 0
        context.month_label = ""
        context.current_year_label = str(getdate(nowdate()).year)
        context.open_tasks = []
        context.top_performers = []
        context.recent_scorecards = []
        context.trend = []
        context.distribution = {"grades": {}, "total": 0, "month_label": ""}
        context.active_page = "dashboard"
