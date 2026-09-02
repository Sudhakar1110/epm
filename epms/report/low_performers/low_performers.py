import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Low Performers Report."""
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
            "fieldname": "overall_score",
            "fieldtype": "Float",
            "label": _("Overall Score"),
            "width": 110,
        },
        {
            "fieldname": "final_grade",
            "fieldtype": "Data",
            "label": _("Grade"),
            "width": 100,
        },
        {
            "fieldname": "productivity_score",
            "fieldtype": "Float",
            "label": _("Productivity"),
            "width": 100,
        },
        {
            "fieldname": "quality_score",
            "fieldtype": "Float",
            "label": _("Quality"),
            "width": 80,
        },
        {
            "fieldname": "attendance_score",
            "fieldtype": "Float",
            "label": _("Attendance"),
            "width": 90,
        },
        {
            "fieldname": "tasks_completed",
            "fieldtype": "Int",
            "label": _("Tasks Completed"),
            "width": 110,
        },
        {
            "fieldname": "pending_tasks",
            "fieldtype": "Int",
            "label": _("Pending Tasks"),
            "width": 100,
        },
        {
            "fieldname": "performance_status",
            "fieldtype": "Data",
            "label": _("Status"),
            "width": 100,
        },
    ]


def get_data(filters):
    """Get report data."""
    month = cint(filters.get("month", getdate(nowdate()).month))
    year = cint(filters.get("year", getdate(nowdate()).year))
    threshold = cint(filters.get("threshold", 60))

    conditions = {
        "month": month,
        "year": year,
        "overall_score": ["<", threshold],
        "docstatus": 1,
    }

    if filters.get("team"):
        conditions["team"] = filters["team"]

    data = frappe.get_all(
        "Performance Scorecard",
        filters=conditions,
        fields=[
            "employee_name",
            "team",
            "overall_score",
            "final_grade",
            "productivity_score",
            "quality_score",
            "attendance_score",
            "tasks_completed",
            "pending_tasks",
            "performance_status",
        ],
        order_by="overall_score asc",
    )

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in data],
            "datasets": [
                {
                    "name": "Overall Score",
                    "values": [d.get("overall_score", 0) for d in data],
                }
            ],
        },
        "type": "bar",
        "colors": ["#dc3545"],
    }
