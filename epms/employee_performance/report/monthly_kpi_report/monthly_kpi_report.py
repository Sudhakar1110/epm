import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, get_first_day, get_last_day


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)

    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "team_name", "fieldtype": "Data", "label": _("Team"), "width": 150},
        {"fieldname": "kpi_name", "fieldtype": "Data", "label": _("KPI"), "width": 200},
        {"fieldname": "target", "fieldtype": "Float", "label": _("Target"), "width": 100},
        {"fieldname": "actual", "fieldtype": "Float", "label": _("Actual"), "width": 100},
        {"fieldname": "achievement", "fieldtype": "Percent", "label": _("Achievement %"), "width": 110},
        {"fieldname": "status", "fieldtype": "Data", "label": _("Status"), "width": 100},
    ]


def get_data(filters):
    month = cint(filters.get("month")) or getdate(nowdate()).month
    year = cint(filters.get("year")) or getdate(nowdate()).year

    first_day = get_first_day(f"{year}-{month:02d}-01")
    last_day = get_last_day(f"{year}-{month:02d}-01")

    teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name"],
    )

    data = []

    for team in teams:
        try:
            stats = frappe.db.sql(
                """
                SELECT
                    count(name) as total_entries,
                    sum(case when task_status = 'Completed' then 1 else 0 end) as tasks_completed,
                    avg(daily_rating) as avg_rating,
                    sum(actual_hours) as total_hours
                from `tabDaily Performance`
                where team = %s
                and date between %s and %s
                and docstatus = 1
                """,
                (team.name, first_day, last_day),
                as_dict=True,
            )
            stats = stats[0] if stats else None
        except Exception:
            stats = None

        try:
            scorecard = frappe.db.sql(
                """
                SELECT
                    avg(overall_score) as team_score,
                    avg(productivity_score) as productivity,
                    avg(quality_score) as quality,
                    avg(attendance_score) as attendance
                from `tabPerformance Scorecard`
                where team = %s
                and month = %s
                and year = %s
                and docstatus = 1
                """,
                (team.name, month, year),
                as_dict=True,
            )
            scorecard = scorecard[0] if scorecard else None
        except Exception:
            scorecard = None

        if not stats:
            stats = frappe._dict(total_entries=0, tasks_completed=0, avg_rating=0, total_hours=0)
        if not scorecard:
            scorecard = frappe._dict(team_score=0, productivity=0, quality=0, attendance=0)

        total_entries = cint(stats.total_entries) or 0
        tasks_completed = cint(stats.tasks_completed) or 0
        avg_rating = flt(stats.avg_rating) or 0

        completion_rate = round((tasks_completed / total_entries * 100) if total_entries else 0, 2)

        kpis = [
            {"kpi_name": "Task Completion Rate", "target": 80, "actual": completion_rate},
            {"kpi_name": "Average Rating", "target": 7, "actual": round(avg_rating, 2)},
            {"kpi_name": "Team Score", "target": 70, "actual": round(flt(scorecard.team_score), 2)},
            {"kpi_name": "Productivity Score", "target": 70, "actual": round(flt(scorecard.productivity), 2)},
            {"kpi_name": "Quality Score", "target": 70, "actual": round(flt(scorecard.quality), 2)},
            {"kpi_name": "Attendance Score", "target": 90, "actual": round(flt(scorecard.attendance), 2)},
        ]

        for kpi in kpis:
            achievement = (kpi["actual"] / kpi["target"] * 100) if kpi["target"] else 0
            status = (
                "On Track" if achievement >= 100 else "Needs Attention" if achievement >= 80 else "At Risk"
            )

            data.append({
                "team_name": team.team_name,
                "kpi_name": kpi["kpi_name"],
                "target": kpi["target"],
                "actual": kpi["actual"],
                "achievement": round(achievement, 2),
                "status": status,
            })

    return data


def get_chart_data(data):
    if not data:
        return None

    team_scores = {}
    for row in data:
        if "Team Score" in row.get("kpi_name", ""):
            team_name = row.get("team_name", "")
            team_scores[team_name] = row.get("actual", 0)

    if not team_scores:
        return None

    return {
        "data": {
            "labels": list(team_scores.keys()),
            "datasets": [{"name": "Team Score", "values": list(team_scores.values())}],
        },
        "type": "bar",
        "colors": ["#5e64ff"],
    }


def flt(val):
    try:
        return float(val) if val else 0.0
    except (TypeError, ValueError):
        return 0.0
