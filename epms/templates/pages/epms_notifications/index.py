import frappe

from epms.employee_performance.api import get_portal_notifications
from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    result = get_portal_notifications(limit=100)
    context.notifications = result.get("notifications", [])
    context.unread_count = result.get("unread_count", 0)
    context.active_page = "notifications"