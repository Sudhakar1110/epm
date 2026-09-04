from epms.employee_performance.utils import portal_login_redirect, portal_reports, portal_setup_common


def get_context(context):
    portal_login_redirect()
    portal_setup_common(context)

    icon_set = ["icon-teal", "icon-blue", "icon-purple", "icon-amber", "icon-red", "icon-green"]

    context.reports = []
    for i, r in enumerate(portal_reports()):
        r["url"] = "/epms/report?report=" + r["slug"]
        r["icon_class"] = icon_set[i % len(icon_set)]
        context.reports.append(r)

    context.active_page = "reports"
