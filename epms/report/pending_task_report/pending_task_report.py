import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, date_diff


def execute(filters=None):
    """Execute Pending Task Report."""
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
            "fieldname": "task",
            "fieldtype": "Data",
            "label": _("Task"),
            "width": 200,
        },
        {
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "label": _("Employee"),
            "width": 150,
        },
        {
            "fieldname": "assigned_date",
            "fieldtype": "Date",
            "label": _("Assigned Date"),
            "width": 100,
        },
        {
            "fieldname": "expected_completion",
            "fieldtype": "Date",
            "label": _("Expected"),
            "width": 100,
        },
        {
            "fieldname": "days_overdue",
            "fieldtype": "Int",
            "label": _("Days Overdue"),
            "width": 100,
        },
        {
            "fieldname": "priority",
            "fieldtype": "Data",
            "label": _("Priority"),
            "width": 80,
        },
        {
            "fieldname": "current_status",
            "fieldtype": "Data",
            "label": _("Status"),
            "width": 100,
        },
        {
            "fieldname": "reason",
            "fieldtype": "Data",
            "label": _("Reason"),
            "width": 150,
        },
    ]


def get_data(filters):
    """Get report data."""
    conditions = {"docstatus": 1}

    if filters.get("employee"):
        conditions["employee"] = filters["employee"]

    if filters.get("priority"):
        conditions["priority"] = filters["priority"]

    if filters.get("status"):
        conditions["current_status"] = filters["status"]

    if filters.get("show_completed") != 1:
        conditions["current_status"] = ["not in", ["Completed"]]

    data = frappe.get_all(
        "Pending Task",
        filters=conditions,
        fields=[
            "task",
            "employee_name",
            "assigned_date",
            "expected_completion",
            "priority",
            "current_status",
            "reason",
        ],
        order_by="expected_completion asc",
    )

    # Calculate days overdue
    today = getdate(nowdate())
    for row in data:
        if row.expected_completion and row.expected_completion < today:
            row["days_overdue"] = date_diff(today, row.expected_completion)
        else:
            row["days_overdue"] = 0

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Group by status
    status_counts = {}
    for row in data:
        status = row.get("current_status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [
                {"name": "Tasks", "values": list(status_counts.values())}
            ],
        },
        "type": "pie",
        "colors": ["#ffc107", "#007bff", "#28a745", "#dc3545"],
    }
