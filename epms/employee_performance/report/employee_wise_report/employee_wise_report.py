import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Employee Wise Report."""
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
            "fieldname": "total_entries",
            "fieldtype": "Int",
            "label": _("Total Entries"),
            "width": 100,
        },
        {
            "fieldname": "tasks_completed",
            "fieldtype": "Int",
            "label": _("Tasks Completed"),
            "width": 110,
        },
        {
            "fieldname": "avg_rating",
            "fieldtype": "Float",
            "label": _("Avg Rating"),
            "width": 90,
        },
        {
            "fieldname": "avg_quality",
            "fieldtype": "Float",
            "label": _("Avg Quality"),
            "width": 90,
        },
        {
            "fieldname": "total_hours",
            "fieldtype": "Float",
            "label": _("Total Hours"),
            "width": 90,
        },
        {
            "fieldname": "avg_completion",
            "fieldtype": "Percent",
            "label": _("Avg Completion %"),
            "width": 110,
        },
        {
            "fieldname": "latest_score",
            "fieldtype": "Float",
            "label": _("Latest Score"),
            "width": 100,
        },
        {
            "fieldname": "latest_grade",
            "fieldtype": "Data",
            "label": _("Latest Grade"),
            "width": 100,
        },
    ]


def get_data(filters):
    """Get report data."""
    conditions = {"dp.docstatus": 1}

    if filters.get("date_from"):
        conditions["dp.date"] = [">=", filters["date_from"]]
    if filters.get("date_to"):
        if "dp.date" in conditions:
            conditions["dp.date"] = [
                "between",
                [filters["date_from"], filters["date_to"]],
            ]
        else:
            conditions["dp.date"] = ["<=", filters["date_to"]]

    if filters.get("team"):
        conditions["dp.team"] = filters["team"]

    if filters.get("employee"):
        conditions["dp.employee"] = filters["employee"]

    # Get aggregated data
    data = frappe.db.sql(
        """
        SELECT 
            dp.employee_name,
            dp.team,
            COUNT(dp.name) as total_entries,
            SUM(CASE WHEN dp.task_status = 'Completed' THEN 1 ELSE 0 END) as tasks_completed,
            AVG(dp.daily_rating) as avg_rating,
            AVG(dp.quality_score) as avg_quality,
            SUM(dp.actual_hours) as total_hours,
            AVG(dp.completion_percentage) as avg_completion
        FROM `tabDaily Performance` dp
        WHERE dp.docstatus = 1
        {conditions}
        GROUP BY dp.employee, dp.team
        ORDER BY avg_rating DESC
    """.format(
            conditions=" AND ".join(
                [f"{k} = %s" if not isinstance(v, list) else f"{k} %s" for k, v in conditions.items()]
            )
        ),
        [v for v in conditions.values() if not isinstance(v, list)],
        as_dict=True,
    )

    # Get latest scorecard for each employee
    for row in data:
        scorecard = frappe.db.get_value(
            "Performance Scorecard",
            {"employee": row.get("employee"), "docstatus": 1},
            ["overall_score", "final_grade"],
            order_by="year desc, month desc",
            as_dict=True,
        )

        if scorecard:
            row["latest_score"] = scorecard.overall_score
            row["latest_grade"] = scorecard.final_grade
        else:
            row["latest_score"] = 0
            row["latest_grade"] = "N/A"

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Get top 10 performers
    top_performers = sorted(data, key=lambda x: x.get("avg_rating", 0), reverse=True)[:10]

    return {
        "data": {
            "labels": [d.get("employee_name", "Unknown") for d in top_performers],
            "datasets": [
                {
                    "name": "Average Rating",
                    "values": [d.get("avg_rating", 0) for d in top_performers],
                }
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff"],
    }
