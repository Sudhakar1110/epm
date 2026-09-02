import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Leaderboard Report."""
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
            "label": _("Score"),
            "width": 100,
        },
        {
            "fieldname": "final_grade",
            "fieldtype": "Data",
            "label": _("Grade"),
            "width": 100,
        },
        {
            "fieldname": "tasks_completed",
            "fieldtype": "Int",
            "label": _("Tasks"),
            "width": 80,
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
            "fieldname": "badge",
            "fieldtype": "Data",
            "label": _("Badge"),
            "width": 80,
        },
    ]


def get_data(filters):
    """Get report data."""
    month = cint(filters.get("month", getdate(nowdate()).month))
    year = cint(filters.get("year", getdate(nowdate()).year))

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
            "tasks_completed",
            "productivity_score",
            "quality_score",
            "attendance_score",
        ],
        order_by="overall_score desc",
    )

    # Add rank and badge
    for i, row in enumerate(data):
        row["rank"] = i + 1

        # Assign badge
        if row.overall_score >= 90:
            row["badge"] = "🏆"
        elif row.overall_score >= 80:
            row["badge"] = "🥇"
        elif row.overall_score >= 70:
            row["badge"] = "🥈"
        elif row.overall_score >= 60:
            row["badge"] = "🥉"
        else:
            row["badge"] = "📋"

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Top 10 performers
    top_10 = data[:10]

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in top_10],
            "datasets": [
                {
                    "name": "Overall Score",
                    "values": [d.get("overall_score", 0) for d in top_10],
                }
            ],
        },
        "type": "bar",
        "colors": ["#28a745"],
    }
