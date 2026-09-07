import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Monthly Performance Report."""
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
            "fieldname": "month",
            "fieldtype": "Data",
            "label": _("Month"),
            "width": 80,
        },
        {
            "fieldname": "year",
            "fieldtype": "Int",
            "label": _("Year"),
            "width": 80,
        },
        {
            "fieldname": "total_working_days",
            "fieldtype": "Int",
            "label": _("Working Days"),
            "width": 100,
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
            "fieldname": "completed_percentage",
            "fieldtype": "Percent",
            "label": _("Completion %"),
            "width": 100,
        },
        {
            "fieldname": "average_rating",
            "fieldtype": "Float",
            "label": _("Avg Rating"),
            "width": 90,
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
            "fieldname": "performance_status",
            "fieldtype": "Data",
            "label": _("Status"),
            "width": 100,
        },
    ]


def get_data(filters):
    """Get report data."""
    conditions = {"docstatus": 1}

    if filters.get("month"):
        conditions["month"] = cint(filters["month"])

    if filters.get("year"):
        conditions["year"] = cint(filters["year"])

    if filters.get("team"):
        conditions["team"] = filters["team"]

    if filters.get("employee"):
        conditions["employee"] = filters["employee"]

    if filters.get("grade"):
        conditions["final_grade"] = filters["grade"]

    data = frappe.get_all(
        "Performance Scorecard",
        filters=conditions,
        fields=[
            "employee_name",
            "team",
            "month",
            "year",
            "total_working_days",
            "tasks_completed",
            "pending_tasks",
            "completed_percentage",
            "average_rating",
            "productivity_score",
            "quality_score",
            "attendance_score",
            "overall_score",
            "final_grade",
            "performance_status",
        ],
        order_by="overall_score desc",
    )

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Group by grade
    grade_counts = {}
    for row in data:
        grade = row.get("final_grade", "Unknown")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    return {
        "data": {
            "labels": list(grade_counts.keys()),
            "datasets": [
                {"name": "Employees", "values": list(grade_counts.values())}
            ],
        },
        "type": "pie",
        "colors": ["#28a745", "#17a2b8", "#ffc107", "#fd7e14", "#dc3545"],
    }
