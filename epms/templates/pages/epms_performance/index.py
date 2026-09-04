import frappe
from frappe.utils import getdate, nowdate

from epms.employee_performance.utils import (
    portal_current_scorecards,
    portal_login_redirect,
    portal_month_label,
    portal_setup_common,
    portal_user_candidates,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    context.month_label = portal_month_label()
    context.current_month = getdate(nowdate()).month
    context.current_year = getdate(nowdate()).year

    scorecards = portal_current_scorecards(order_by="overall_score desc")

    scores = [s.get("overall_score") or 0 for s in scorecards]
    context.total_scorecards = len(scorecards)
    context.avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    context.top_score = max(scores) if scores else 0
    context.attention_count = len(
        [s for s in scorecards if s.get("performance_status") == "Needs Attention"]
    )
    context.at_risk_count = len([s for s in scorecards if s.get("performance_status") == "At Risk"])

    context.scorecards = scorecards
    context.can_create_scorecard = frappe.has_permission("Performance Scorecard", "create")
    context.user_candidates = portal_user_candidates()
    context.active_page = "performance"
