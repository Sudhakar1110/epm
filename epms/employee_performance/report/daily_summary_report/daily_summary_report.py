import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    """Execute Daily Summary Report - all employees in one view."""
    if not filters:
        filters = {}

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
    conditions = "dp.docstatus = 1"

    date = filters.get("date")
    if not date:
        date = getdate(nowdate())

    conditions += f" AND dp.date = '{date}'"

    if filters.get("team"):
        conditions += f" AND dp.team = '{filters['team']}'"

    if filters.get("employee"):
        conditions += f" AND dp.employee = '{filters['employee']}'"

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
        WHERE {conditions}
        GROUP BY dp.employee, dp.team
        ORDER BY avg_rating DESC
        """,
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
