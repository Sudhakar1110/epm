from epms.employee_performance.utils import (
    portal_audit_log,
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    context.audit_rows = portal_audit_log()
    context.active_page = "audit"