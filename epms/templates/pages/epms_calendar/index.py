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

    try:
        data = portal_calendar_tasks(month, year)
        context.month = month
        context.year = year
        context.month_label = portal_month_label(month, year)
        context.by_day = data.get("by_day", {})
        context.last_day = data.get("last_day", 0)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EPMS Calendar Page Error")
        context.month = month
        context.year = year
        context.month_label = portal_month_label(month, year)
        context.by_day = {}
        context.last_day = 0

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

    context.today_day = getdate(nowdate()).day
    context.today_month = getdate(nowdate()).month
    context.today_year = getdate(nowdate()).year

    weekend_days = set()
    holiday_days = set()
    try:
        settings = frappe.get_single("EPMS Settings")
        sat_holiday = bool(settings.saturday_is_holiday)
    except Exception:
        sat_holiday = False

    for d in range(1, context.last_day + 1):
        dt = getdate(f"{year}-{month:02d}-{d:02d}")
        wd = dt.weekday()
        if wd == 6:  # Sunday always holiday
            holiday_days.add(d)
            weekend_days.add(d)
        elif wd == 5 and sat_holiday:  # Saturday holiday if setting enabled
            holiday_days.add(d)
            weekend_days.add(d)

    # Custom holidays from the Holiday doctype
    holiday_names = {}
    try:
        first = f"{year}-{month:02d}-01"
        last = frappe.utils.get_last_day(first)
        custom = frappe.get_all(
            "Holiday",
            filters={"holiday_date": ["between", [first, last]]},
            fields=["holiday_date", "holiday_name"],
        )
        for h in custom:
            try:
                d = int(str(h.get("holiday_date") or "")[-2:].lstrip("0") or "1")
            except (TypeError, ValueError):
                continue
            holiday_days.add(d)
            holiday_names[d] = h.get("holiday_name") or "Holiday"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "EPMS Calendar Holidays Error")
    context.holiday_names = holiday_names
    context.weekend_days = weekend_days
    context.holiday_days = holiday_days

    context.today_url = f"/epms/calendar?month={context.today_month}&year={context.today_year}"