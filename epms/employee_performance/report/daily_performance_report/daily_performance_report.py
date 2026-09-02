import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Daily Performance Report."""
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_columns():
    """Get report columns."""
    return [
        {
            "fieldname": "performance_id",
            "fieldtype": "Data",
            "label": _("Performance ID"),
            "width": 150,
        },
        {
            "fieldname": "date",
            "fieldtype": "Date",
            "label": _("Date"),
            "width": 100,
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": _("Employee"),
            "width": 150,
        },
        {
            "fieldname": "team",
            "fieldtype": "Link",
            "label": _("Team"),
            "options": "Team",
            "width": 120,
        },
        {
            "fieldname": "task_title",
            "fieldtype": "Data",
            "label": _("Task Title"),
            "width": 200,
        },
        {
            "fieldname": "priority",
            "fieldtype": "Data",
            "label": _("Priority"),
            "width": 80,
        },
        {
            "fieldname": "task_status",
            "fieldtype": "Data",
            "label": _("Status"),
            "width": 100,
        },
        {
            "fieldname": "work_type",
            "fieldtype": "Data",
            "label": _("Work Type"),
            "width": 100,
        },
        {
            "fieldname": "actual_hours",
            "fieldtype": "Float",
            "label": _("Hours"),
            "width": 80,
        },
        {
            "fieldname": "completion_percentage",
            "fieldtype": "Percent",
            "label": _("Completion %"),
            "width": 100,
        },
        {
            "fieldname": "daily_rating",
            "fieldtype": "Float",
            "label": _("Rating"),
            "width": 80,
        },
        {
            "fieldname": "quality_score",
            "fieldtype": "Float",
            "label": _("Quality"),
            "width": 80,
        },
    ]


def get_data(filters):
    """Get report data."""
    conditions = {"docstatus": 1}

    if filters.get("date_from"):
        conditions["date"] = [">=", filters["date_from"]]
    if filters.get("date_to"):
        if "date" in conditions:
            conditions["date"] = ["between", [filters["date_from"], filters["date_to"]]]
        else:
            conditions["date"] = ["<=", filters["date_to"]]

    if filters.get("team"):
        conditions["team"] = filters["team"]

    if filters.get("employee"):
        conditions["employee"] = filters["employee"]

    if filters.get("priority"):
        conditions["priority"] = filters["priority"]

    if filters.get("task_status"):
        conditions["task_status"] = filters["task_status"]

    data = frappe.get_all(
        "Daily Performance",
        filters=conditions,
        fields=[
            "performance_id",
            "date",
            "employee_name",
            "team",
            "task_title",
            "priority",
            "task_status",
            "work_type",
            "actual_hours",
            "completion_percentage",
            "daily_rating",
            "quality_score",
        ],
        order_by="date desc, employee_name asc",
    )

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Group by status
    status_counts = {}
    for row in data:
        status = row.get("task_status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"name": "Tasks", "values": list(status_counts.values())}],
        },
        "type": "pie",
        "colors": ["#28a745", "#007bff", "#ffc107", "#dc3545"],
    }
