import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint


@frappe.whitelist()
def get_leaderboard_data(month=None, year=None, team=None):
    """Get leaderboard data."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    month = cint(month)
    year = cint(year)

    conditions = {
        "month": month,
        "year": year,
        "docstatus": 1,
    }

    if team:
        conditions["team"] = team

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

    # Add rank and medal
    for i, row in enumerate(data):
        row["rank"] = i + 1

        if i == 0:
            row["medal"] = "🥇"
        elif i == 1:
            row["medal"] = "🥈"
        elif i == 2:
            row["medal"] = "🥉"
        else:
            row["medal"] = str(i + 1)

    return data


@frappe.whitelist()
def get_teams():
    """Get all active teams."""
    return frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name"],
        order_by="team_name asc",
    )
