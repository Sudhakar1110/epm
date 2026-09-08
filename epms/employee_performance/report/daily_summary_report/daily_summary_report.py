import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Daily Summary Report - all employees in one view."""
    if not filters:
        filters = {}

    if filters.get("month") and filters.get("year"):
        import calendar
        month = cint(filters["month"])
        year = cint(filters["year"])
        last_day = calendar.monthrange(year, month)[1]
        filters["date_from"] = f"{year}-{month:02d}-01"
        filters["date_to"] = f"{year}-{month:02d}-{last_day:02d}"

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_columns():
    """Get report columns."""
    return [
        {"fieldname": "employee_name", "fieldtype": "Data", "label": _("Employee"), "width": 150},
        {"fieldname": "team", "fieldtype": "Link", "label": _("Team"), "options": "Team", "width": 120},
        {"fieldname": "total_entries", "fieldtype": "Int", "label": _("Entries"), "width": 80},
        {"fieldname": "tasks_completed", "fieldtype": "Int", "label": _("Completed"), "width": 90},
        {"fieldname": "tasks_pending", "fieldtype": "Int", "label": _("Pending"), "width": 80},
        {"fieldname": "tasks_blocked", "fieldtype": "Int", "label": _("Blocked"), "width": 80},
        {"fieldname": "avg_rating", "fieldtype": "Float", "label": _("Avg Rating"), "width": 90},
        {"fieldname": "avg_quality", "fieldtype": "Float", "label": _("Avg Quality"), "width": 90},
        {"fieldname": "total_hours", "fieldtype": "Float", "label": _("Total Hours"), "width": 90},
        {"fieldname": "avg_completion", "fieldtype": "Percent", "label": _("Avg Completion"), "width": 100},
    ]


def get_data(filters):
    """Get report data."""
    conditions = ["dp.docstatus = 1"]
    params = []

    if filters.get("date_from") and filters.get("date_to"):
        conditions.append("dp.date BETWEEN %s AND %s")
        params.extend([filters["date_from"], filters["date_to"]])
    elif filters.get("date_from"):
        conditions.append("dp.date >= %s")
        params.append(filters["date_from"])
    elif filters.get("date_to"):
        conditions.append("dp.date <= %s")
        params.append(filters["date_to"])
    else:
        conditions.append("dp.date = %s")
        params.append(getdate(nowdate()))

    if filters.get("team"):
        conditions.append("dp.team = %s")
        params.append(filters["team"])

    if filters.get("employee"):
        conditions.append("dp.employee = %s")
        params.append(filters["employee"])

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            dp.employee_name,
            dp.team,
            COUNT(dp.name) as total_entries,
            SUM(CASE WHEN dp.task_status = 'Completed' THEN 1 ELSE 0 END) as tasks_completed,
            SUM(CASE WHEN dp.task_status = 'Pending' THEN 1 ELSE 0 END) as tasks_pending,
            SUM(CASE WHEN dp.task_status = 'Blocked' THEN 1 ELSE 0 END) as tasks_blocked,
            ROUND(AVG(dp.daily_rating), 2) as avg_rating,
            ROUND(AVG(dp.quality_score), 2) as avg_quality,
            ROUND(SUM(dp.actual_hours), 2) as total_hours,
            ROUND(AVG(dp.completion_percentage), 2) as avg_completion
        FROM `tabDaily Performance` dp
        WHERE {where_clause}
        GROUP BY dp.employee, dp.team
        ORDER BY avg_rating DESC
        """,
        tuple(params),
        as_dict=True,
    )

    return data


def get_chart_data(data):
    """Get chart data."""
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in data[:10]],
            "datasets": [
                {"name": "Avg Rating", "values": [d.get("avg_rating", 0) for d in data[:10]]},
                {"name": "Avg Quality", "values": [d.get("avg_quality", 0) for d in data[:10]]},
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff", "#28a745"],
    }
