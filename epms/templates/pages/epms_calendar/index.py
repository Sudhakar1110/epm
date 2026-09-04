import frappe
from frappe.utils import getdate, nowdate

from epms.employee_performance.utils import (
    portal_calendar_tasks,
    portal_login_redirect,
    portal_month_label,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    try:
        month = int(frappe.form_dict.get("month") or getdate(nowdate()).month)
    except (TypeError, ValueError):
        month = getdate(nowdate()).month
    try:
        year = int(frappe.form_dict.get("year") or getdate(nowdate()).year)
    except (TypeError, ValueError):
        year = getdate(nowdate()).year

    if month < 1 or month > 12:
        month = getdate(nowdate()).month
    if year < 2000 or year > 2100:
        year = getdate(nowdate()).year

    data = portal_calendar_tasks(month, year)
    context.month = month
    context.year = year
    context.month_label = portal_month_label(month, year)
    context.by_day = data["by_day"]
    context.last_day = data["last_day"]

    # first weekday of the month (1=Mon ... 7=Sun), CSS grid is Mon-first
    first = getdate(f"{year}-{month:02d}-01")
    context.first_weekday = first.weekday() + 1  # 1..7

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    context.prev_url = f"/epms/calendar?month={prev_month}&year={prev_year}"
    context.next_url = f"/epms/calendar?month={next_month}&year={next_year}"

    context.active_page = "calendar"