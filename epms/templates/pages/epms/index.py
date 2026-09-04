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
    portal_login_redirect()
    portal_setup_common(context)

    # Stats
    context.total_teams = frappe.db.count("Team", {"status": "Active"})
    context.active_members = frappe.db.count("Team Member Mapping", {"status": "Active"})
    context.pending_tasks = frappe.db.count(
        "Pending Task",
        filters={"current_status": ["in", ["Pending", "In Progress"]], "docstatus": 1},
    )
    avg_score = frappe.db.get_value(
        "Performance Scorecard",
        {"month": getdate(nowdate()).month, "year": getdate(nowdate()).year, "docstatus": 1},
        "avg(overall_score)",
    )
    context.avg_score = round(flt(avg_score, 1) if avg_score else 0, 1)

    context.month_label = portal_month_label()
    context.current_year_label = str(getdate(nowdate()).year)

    # Open tasks across the portal
    context.open_tasks = portal_open_tasks(limit=6)

    # Top performers (current month)
    top = portal_current_scorecards(limit=5)
    for i, p in enumerate(top):
        p["rank"] = i + 1
        p["rank_class"] = "gold" if i == 0 else ("silver" if i == 1 else ("bronze" if i == 2 else "plain"))
    context.top_performers = top

    # Recently updated scorecards
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

    # Charts
    context.trend = portal_month_trend()
    context.distribution = portal_grade_distribution()

    context.active_page = "dashboard"
