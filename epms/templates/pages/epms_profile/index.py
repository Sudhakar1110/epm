import frappe

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    user = frappe.get_doc("User", frappe.session.user)
    context.profile = {
        "name": user.name,
        "full_name": user.full_name or user.name,
        "email": user.email or "",
        "roles": ", ".join(frappe.get_roles(frappe.session.user)[:5]) or "—",
    }
    context.active_page = "profile"