import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Team Wise Report."""
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
            "fieldname": "team_name",
            "fieldtype": "Data",
            "label": _("Team"),
            "width": 150,
        },
        {
            "fieldname": "team_leader",
            "fieldtype": "Data",
            "label": _("Team Leader"),
            "width": 150,
        },
        {
            "fieldname": "total_members",
            "fieldtype": "Int",
            "label": _("Members"),
            "width": 80,
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
            "fieldname": "team_score",
            "fieldtype": "Float",
            "label": _("Team Score"),
            "width": 100,
        },
    ]


def get_data(filters):
    """Get report data."""
    teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name", "team_leader", "total_members"],
    )

    data = []

    for team in teams:
        conditions = {"team": team.name, "docstatus": 1}

        if filters.get("date_from"):
            conditions["date"] = [">=", filters["date_from"]]
        if filters.get("date_to"):
            if "date" in conditions:
                conditions["date"] = [
                    "between",
                    [filters["date_from"], filters["date_to"]],
                ]
            else:
                conditions["date"] = ["<=", filters["date_to"]]

        stats = frappe.db.get_value(
            "Daily Performance",
            conditions,
            [
                "count(name) as total_entries",
                "sum(case when task_status = 'Completed' then 1 else 0 end) as tasks_completed",
                "avg(daily_rating) as avg_rating",
                "avg(quality_score) as avg_quality",
                "sum(actual_hours) as total_hours",
                "avg(completion_percentage) as avg_completion",
            ],
            as_dict=True,
        )

        # Get team score from scorecards
        current_month = getdate(nowdate()).month
        current_year = getdate(nowdate()).year

        team_score = frappe.db.get_value(
            "Performance Scorecard",
            {
                "team": team.name,
                "month": current_month,
                "year": current_year,
                "docstatus": 1,
            },
            "avg(overall_score)",
        )

        data.append(
            {
                "team_name": team.team_name,
                "team_leader": team.team_leader,
                "total_members": team.total_members,
                "total_entries": stats.total_entries or 0,
                "tasks_completed": stats.tasks_completed or 0,
                "avg_rating": round(stats.avg_rating or 0, 2),
                "avg_quality": round(stats.avg_quality or 0, 2),
                "total_hours": round(stats.total_hours or 0, 2),
                "avg_completion": round(stats.avg_completion or 0, 2),
                "team_score": round(team_score or 0, 2),
            }
        )

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    return {
        "data": {
            "labels": [d.get("team_name", "Unknown") for d in data],
            "datasets": [
                {
                    "name": "Team Score",
                    "values": [d.get("team_score", 0) for d in data],
                }
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff"],
    }
