import frappe
from frappe.utils import cint, getdate, nowdate

from epms.employee_performance.utils import (
    GRADE_CLASS_MAP,
    portal_current_scorecards,
    portal_login_redirect,
    portal_month_label,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    # Filters (month / year / team) — GET params so links are shareable.
    filter_month = cint(frappe.form_dict.get("month") or getdate(nowdate()).month)
    filter_year = cint(frappe.form_dict.get("year") or getdate(nowdate()).year)
    filter_team = (frappe.form_dict.get("team") or "").strip() or None

    context.filter_month = filter_month
    context.filter_year = filter_year
    context.filter_team = filter_team
    context.current_month = getdate(nowdate()).month
    context.current_year = getdate(nowdate()).year
    context.month_label = portal_month_label(filter_month, filter_year)
    context.teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name"],
        order_by="team_name asc",
    )

    scorecards = portal_current_scorecards(
        order_by="overall_score desc",
        month=filter_month,
        year=filter_year,
        team=filter_team,
    )

    # Grade distribution buckets for the filtered month
    buckets = {}
    for s in scorecards:
        grade = s.get("final_grade") or "Needs Improvement"
        buckets.setdefault(grade, 0)
        buckets[grade] += 1
    context.grade_buckets = [
        {"grade": g, "count": c, "grade_class": GRADE_CLASS_MAP.get(g, "b-gray")}
        for g, c in sorted(buckets.items(), key=lambda x: -x[1])
    ]

    context.scorecards = scorecards
    context.active_page = "scorecards"