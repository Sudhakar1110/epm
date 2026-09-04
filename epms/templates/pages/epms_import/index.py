import frappe

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    context.can_import = "EPMS Founder" in frappe.get_roles(frappe.session.user)
    context.active_page = "import"