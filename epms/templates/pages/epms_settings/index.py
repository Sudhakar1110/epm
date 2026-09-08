import frappe

from epms.employee_performance.utils import (
    portal_get_settings,
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    try:
        context.can_manage = "EPMS Founder" in frappe.get_roles(frappe.session.user)
        context.settings = portal_get_settings()
    except Exception:
        context.can_manage = False
        context.settings = {}
    context.active_page = "settings"
