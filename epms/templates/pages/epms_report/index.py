import frappe
from frappe.utils import cint, getdate, nowdate

from epms.employee_performance.utils import (
    portal_format_report_value,
    portal_login_redirect,
    portal_month_label,
    portal_reports,
    portal_run_report,
    portal_setup_common,
)


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    slug = frappe.form_dict.get("report") or ""
    report = next((r for r in portal_reports() if r["slug"] == slug), None)
    if not report:
        frappe.local.flags.redirect_location = "/epms/reports"
        raise frappe.Redirect

    # Filters (month / year / team) — passed straight into the report script.
    filter_month = cint(frappe.form_dict.get("month") or getdate(nowdate()).month)
    filter_year = cint(frappe.form_dict.get("year") or getdate(nowdate()).year)
    filter_team = (frappe.form_dict.get("team") or "").strip() or None

    context.report_slug = slug
    context.report_name = report["name"]
    context.report_description = report["description"]
    context.month_label = portal_month_label(filter_month, filter_year)
    context.filter_month = filter_month
    context.filter_year = filter_year
    context.filter_team = filter_team
    context.current_month = getdate(nowdate()).month
    context.current_year = getdate(nowdate()).year
    context.teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name"],
        order_by="team_name asc",
    )

    filters = {}
    if filter_month:
        filters["month"] = filter_month
    if filter_year:
        filters["year"] = filter_year
    if filter_team:
        filters["team"] = filter_team

    result = portal_run_report(slug, filters)
    if not result:
        context.report_error = True
    else:
        context.columns = result["columns"]
        rows = []
        for row in result["data"]:
            display = {}
            for col in result["columns"]:
                fieldname = col.get("fieldname")
                display[fieldname] = portal_format_report_value(
                    row.get(fieldname), col.get("fieldtype")
                )
            rows.append(display)
        context.rows = rows

    context.active_page = "reports"