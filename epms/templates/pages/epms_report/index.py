import frappe

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

    result = portal_run_report(slug)
    context.report_slug = slug
    context.report_name = report["name"]
    context.report_description = report["description"]
    context.month_label = portal_month_label()

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
