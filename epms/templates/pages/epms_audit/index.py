import frappe

from epms.employee_performance.utils import (
    portal_audit_log,
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    try:
        user_roles = frappe.get_roles(frappe.session.user)
        if "EPMS Founder" not in user_roles and "EPMS Team Leader" not in user_roles:
            frappe.local.flags.redirect_location = "/epms"
            raise frappe.Redirect

        context.audit_rows = portal_audit_log()
    except frappe.Redirect:
        raise
    except Exception:
        context.audit_rows = []
    context.active_page = "audit"
