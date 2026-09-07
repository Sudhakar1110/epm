import frappe

from epms.employee_performance.utils import (
    portal_annotate_scorecard,
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    name = frappe.form_dict.get("name") or ""
    scorecard = None
    if name and frappe.db.exists("Performance Scorecard", name):
        scorecard = frappe.get_doc("Performance Scorecard", name)
        if not frappe.has_permission("Performance Scorecard", "read", scorecard):
            scorecard = None

    if not scorecard:
        context.not_found = True
    else:
        context.scorecard = portal_annotate_scorecard(scorecard.as_dict())
        context.month_label = frappe.utils.formatdate(
            f"{scorecard.year}-{int(scorecard.month):02d}-01", "MMMM yyyy"
        )
    context.active_page = "performance"