import frappe

from epms.employee_performance.api import get_portal_team
from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
    portal_user_candidates,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    result = get_portal_team(frappe.form_dict.get("team") or "")
    if not result.get("ok"):
        frappe.local.flags.redirect_location = "/epms/teams"
        raise frappe.Redirect

    context.team = result["team"]
    context.members = result["members"]
    context.can_manage = result["can_manage"]
    context.user_candidates = portal_user_candidates()
    context.active_page = "teams"