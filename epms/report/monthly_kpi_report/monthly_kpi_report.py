import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


def execute(filters=None):
    """Execute Monthly KPI Report."""
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
            "fieldname": "kpi_name",
            "fieldtype": "Data",
            "label": _("KPI"),
            "width": 200,
        },
        {
            "fieldname": "target",
            "fieldtype": "Float",
            "label": _("Target"),
            "width": 100,
        },
        {
            "fieldname": "actual",
            "fieldtype": "Float",
            "label": _("Actual"),
            "width": 100,
        },
        {
            "fieldname": "achievement",
            "fieldtype": "Percent",
            "label": _("Achievement %"),
            "width": 110,
        },
        {
            "fieldname": "status",
            "fieldtype": "Data",
            "label": _("Status"),
            "width": 100,
        },
    ]


def get_data(filters):
    """Get report data."""
    month = cint(filters.get("month", getdate(nowdate()).month))
    year = cint(filters.get("year", getdate(nowdate()).year))

    # Get team performance data
    teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name"],
    )

    data = []

    for team in teams:
        # Get team stats
        stats = frappe.db.get_value(
            "Daily Performance",
            {
                "team": team.name,
                "date": ["between", [f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"]],
                "docstatus": 1,
            },
            [
                "count(name) as total_entries",
                "sum(case when task_status = 'Completed' then 1 else 0 end) as tasks_completed",
                "avg(daily_rating) as avg_rating",
                "sum(actual_hours) as total_hours",
            ],
            as_dict=True,
        )

        # Get team scorecard
        scorecard = frappe.db.get_value(
            "Performance Scorecard",
            {
                "team": team.name,
                "month": month,
                "year": year,
                "docstatus": 1,
            },
            [
                "avg(overall_score) as team_score",
                "avg(productivity_score) as productivity",
                "avg(quality_score) as quality",
                "avg(attendance_score) as attendance",
            ],
            as_dict=True,
        )

        # Define KPIs
        kpis = [
            {
                "kpi_name": f"{team.team_name} - Task Completion Rate",
                "target": 80,
                "actual": round(
                    (stats.tasks_completed / stats.total_entries * 100)
                    if stats.total_entries
                    else 0,
                    2,
                ),
            },
            {
                "kpi_name": f"{team.team_name} - Average Rating",
                "target": 7,
                "actual": round(stats.avg_rating or 0, 2),
            },
            {
                "kpi_name": f"{team.team_name} - Team Score",
                "target": 70,
                "actual": round(scorecard.team_score or 0, 2),
            },
            {
                "kpi_name": f"{team.team_name} - Productivity Score",
                "target": 70,
                "actual": round(scorecard.productivity or 0, 2),
            },
            {
                "kpi_name": f"{team.team_name} - Quality Score",
                "target": 70,
                "actual": round(scorecard.quality or 0, 2),
            },
            {
                "kpi_name": f"{team.team_name} - Attendance Score",
                "target": 90,
                "actual": round(scorecard.attendance or 0, 2),
            },
        ]

        for kpi in kpis:
            achievement = (kpi["actual"] / kpi["target"] * 100) if kpi["target"] else 0
            status = (
                "On Track" if achievement >= 100 else "Needs Attention" if achievement >= 80 else "At Risk"
            )

            data.append(
                {
                    "kpi_name": kpi["kpi_name"],
                    "target": kpi["target"],
                    "actual": kpi["actual"],
                    "achievement": round(achievement, 2),
                    "status": status,
                }
            )

    return data


def get_chart_data(data):
    """Get chart data for the report."""
    if not data:
        return None

    # Group by team
    team_scores = {}
    for row in data:
        if "Team Score" in row.get("kpi_name", ""):
            team_name = row["kpi_name"].replace(" - Team Score", "")
            team_scores[team_name] = row.get("actual", 0)

    return {
        "data": {
            "labels": list(team_scores.keys()),
            "datasets": [
                {"name": "Team Score", "values": list(team_scores.values())}
            ],
        },
        "type": "bar",
        "colors": ["#5e64ff"],
    }
