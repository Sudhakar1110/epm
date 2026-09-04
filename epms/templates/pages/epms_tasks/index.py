import frappe
from frappe.utils import nowdate

from epms.employee_performance.utils import (
    portal_login_redirect,
    portal_open_tasks,
    portal_setup_common,
    portal_user_candidates,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    tasks = portal_open_tasks()
    open_tasks = [t for t in tasks if t.get("current_status") in ("Pending", "In Progress")]
    overdue_tasks = [t for t in open_tasks if t.get("is_overdue")]
    high_priority = [t for t in open_tasks if t.get("priority") in ("High", "Critical")]

    context.tasks = tasks
    context.open_tasks = len(open_tasks)
    context.overdue_tasks = len(overdue_tasks)
    context.high_priority = len(high_priority)
    context.completed_tasks = frappe.db.count(
        "Pending Task", filters={"current_status": "Completed", "docstatus": 1}
    )
    context.today = str(nowdate())
    context.can_create_task = frappe.has_permission("Pending Task", "create")
    context.user_candidates = portal_user_candidates()
    context.active_page = "tasks"
