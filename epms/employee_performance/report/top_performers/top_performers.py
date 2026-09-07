import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Top Performers Report."""
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
            "fieldname": "rank",
            "fieldtype": "Int",
            "label": _("Rank"),
            "width": 60,
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
    ]


def get_data(filters):
    """Get report data."""
    month = cint(filters.get("month", getdate(nowdate()).month))
    year = cint(filters.get("year", getdate(nowdate()).year))
    limit = cint(filters.get("limit", 10))

    conditions = {
        "month": month,
        "year": year,
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
        ],
        order_by="overall_score desc",
        limit_page_length=limit,
    )

    # Add rank
    for i, row in enumerate(data):
        row["rank"] = i + 1

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in data[:10]],
            "datasets": [
                {
                    "name": "Overall Score",
                    "values": [d.get("overall_score", 0) for d in data[:10]],
                }
            ],
        },
        "type": "bar",
        "colors": ["#28a745"],
    }
