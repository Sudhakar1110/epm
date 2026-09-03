import frappe
from frappe.utils import getdate, nowdate

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

    context.month_label = portal_month_label()
    context.current_month = getdate(nowdate()).month
    context.current_year = getdate(nowdate()).year

    scorecards = portal_current_scorecards(order_by="overall_score desc")

    # Grade distribution buckets for the current month
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
