import frappe

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_search,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    context.query = frappe.form_dict.get("q") or ""
    result = portal_search(context.query)
    context.teams = result["teams"]
    context.tasks = result["tasks"]
    context.users = result["users"]
    context.active_page = "dashboard"