import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


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
        {"fieldname": "team_leader", "fieldtype": "Data", "label": _("Team Leader"), "width": 150},
        {"fieldname": "total_members", "fieldtype": "Int", "label": _("Members"), "width": 80},
        {"fieldname": "total_entries", "fieldtype": "Int", "label": _("Total Entries"), "width": 100},
        {"fieldname": "tasks_completed", "fieldtype": "Int", "label": _("Tasks Completed"), "width": 110},
        {"fieldname": "avg_rating", "fieldtype": "Float", "label": _("Avg Rating"), "width": 90},
        {"fieldname": "avg_quality", "fieldtype": "Float", "label": _("Avg Quality"), "width": 90},
        {"fieldname": "total_hours", "fieldtype": "Float", "label": _("Total Hours"), "width": 90},
        {"fieldname": "avg_completion", "fieldtype": "Percent", "label": _("Avg Completion %"), "width": 110},
        {"fieldname": "team_score", "fieldtype": "Float", "label": _("Team Score"), "width": 100},
    ]


def get_data(filters):
    try:
        teams = frappe.get_all(
            "Team",
            filters={"status": "Active"},
            fields=["name", "team_name", "team_leader", "total_members"],
        )
    except Exception:
        return []

    data = []

    for team in teams:
        try:
            dp_conditions = {"team": team.name, "docstatus": 1}

            if filters.get("date_from") and filters.get("date_to"):
                dp_conditions["date"] = ["between", [filters["date_from"], filters["date_to"]]]
            elif filters.get("date_from"):
                dp_conditions["date"] = [">=", filters["date_from"]]
            elif filters.get("date_to"):
                dp_conditions["date"] = ["<=", filters["date_to"]]

            stats = frappe.db.sql(
                """
                SELECT
                    count(name) as total_entries,
                    sum(case when task_status = 'Completed' then 1 else 0 end) as tasks_completed,
                    avg(daily_rating) as avg_rating,
                    avg(quality_score) as avg_quality,
                    sum(actual_hours) as total_hours,
                    avg(completion_percentage) as avg_completion
                from `tabDaily Performance`
                where team = %s and docstatus = 1
                """ + (" and date between %s and %s" if filters.get("date_from") and filters.get("date_to") else
                       " and date >= %s" if filters.get("date_from") else
                       " and date <= %s" if filters.get("date_to") else ""),
                (team.name,) + (
                    (filters["date_from"], filters["date_to"]) if filters.get("date_from") and filters.get("date_to") else
                    (filters["date_from"],) if filters.get("date_from") else
                    (filters["date_to"],) if filters.get("date_to") else ()
                ),
                as_dict=True,
            )
            stats = stats[0] if stats else None
        except Exception:
            stats = None

        try:
            current_month = cint(getdate(nowdate()).month)
            current_year = cint(getdate(nowdate()).year)
            team_score = frappe.db.sql(
                """
                SELECT avg(overall_score) as team_score
                from `tabPerformance Scorecard`
                where team = %s and month = %s and year = %s and docstatus = 1
                """,
                (team.name, current_month, current_year),
                as_dict=True,
            )
            team_score = team_score[0].team_score if team_score else 0
        except Exception:
            team_score = 0

        total_entries = int(stats.total_entries or 0) if stats else 0
        tasks_completed = int(stats.tasks_completed or 0) if stats else 0
        avg_rating = round(float(stats.avg_rating or 0), 2) if stats else 0
        avg_quality = round(float(stats.avg_quality or 0), 2) if stats else 0
        total_hours = round(float(stats.total_hours or 0), 2) if stats else 0
        avg_completion = round(float(stats.avg_completion or 0), 2) if stats else 0

        data.append({
            "team_name": team.team_name,
            "team_leader": team.team_leader,
            "total_members": team.total_members or 0,
            "total_entries": total_entries,
            "tasks_completed": tasks_completed,
            "avg_rating": avg_rating,
            "avg_quality": avg_quality,
            "total_hours": total_hours,
            "avg_completion": avg_completion,
            "team_score": round(float(team_score or 0), 2),
        })

    return data


def get_chart_data(data):
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
