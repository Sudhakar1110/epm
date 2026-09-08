import frappe

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    try:
        user = frappe.get_doc("User", frappe.session.user)
        role_list = frappe.get_roles(frappe.session.user)[:5]
        context.profile = {
            "name": user.name,
            "full_name": user.full_name or user.name,
            "email": user.email or "",
            "roles": ", ".join(role_list) or "\u2014",
            "role_list": role_list,
        }
    except Exception:
        context.profile = {"name": "", "full_name": "", "email": "", "roles": "", "role_list": []}
    context.active_page = "profile"
