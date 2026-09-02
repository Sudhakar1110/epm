import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, flt, get_first_day, get_last_day


@frappe.whitelist()
def get_employee_performance(employee, month=None, year=None):
    """Get employee performance data."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    month = cint(month)
    year = cint(year)

    scorecard = frappe.db.get_value(
        "Performance Scorecard",
        {
            "employee": employee,
            "month": month,
            "year": year,
        },
        "*",
        as_dict=True,
    )

    first_day = get_first_day(f"{year}-{month:02d}-01")
    last_day = get_last_day(f"{year}-{month:02d}-01")

    daily_performances = frappe.get_all(
        "Daily Performance",
        filters={
            "employee": employee,
            "date": ["between", [first_day, last_day]],
            "docstatus": 1,
        },
        fields=[
            "name",
            "performance_id",
            "date",
            "task_title",
            "task_status",
            "daily_rating",
            "quality_score",
            "actual_hours",
            "completion_percentage",
            "remarks",
        ],
        order_by="date desc",
    )

    pending_tasks = frappe.get_all(
        "Pending Task",
        filters={
            "employee": employee,
            "docstatus": 1,
            "current_status": ["in", ["Pending", "In Progress"]],
        },
        fields=[
            "name",
            "task",
            "assigned_date",
            "expected_completion",
            "priority",
            "current_status",
        ],
        order_by="expected_completion asc",
    )

    return {
        "scorecard": scorecard,
        "daily_performances": daily_performances,
        "pending_tasks": pending_tasks,
    }


@frappe.whitelist()
def get_monthly_scorecard(employee, month=None, year=None):
    """Get monthly scorecard for an employee."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    scorecard = frappe.db.get_value(
        "Performance Scorecard",
        {
            "employee": cint(employee) if employee else frappe.session.user,
            "month": cint(month),
            "year": cint(year),
        },
        "*",
        as_dict=True,
    )

    return scorecard


@frappe.whitelist()
def get_team_performance(team, month=None, year=None):
    """Get team performance data."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    members = frappe.get_all(
        "Team Member Mapping",
        filters={"team": team, "status": "Active"},
        fields=["employee", "employee_name"],
    )

    result = []
    for member in members:
        scorecard = frappe.db.get_value(
            "Performance Scorecard",
            {
                "employee": member.employee,
                "month": cint(month),
                "year": cint(year),
            },
            ["overall_score", "final_grade", "tasks_completed", "pending_tasks"],
            as_dict=True,
        )

        result.append(
            {
                "employee": member.employee,
                "employee_name": member.employee_name,
                "score": scorecard.overall_score if scorecard else 0,
                "grade": scorecard.final_grade if scorecard else "N/A",
                "tasks_completed": scorecard.tasks_completed if scorecard else 0,
                "pending_tasks": scorecard.pending_tasks if scorecard else 0,
            }
        )

    return result


@frappe.whitelist()
def get_leaderboard(month=None, year=None):
    """Get leaderboard data."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    scorecards = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": cint(month),
            "year": cint(year),
            "docstatus": 1,
        },
        fields=[
            "employee",
            "employee_name",
            "overall_score",
            "final_grade",
            "tasks_completed",
            "productivity_score",
            "quality_score",
            "attendance_score",
        ],
        order_by="overall_score desc",
    )

    return scorecards


@frappe.whitelist()
def get_daily_performance_chart(team=None, days=30):
    """Get daily performance chart data."""
    from frappe.utils import add_days

    conditions = {"docstatus": 1}
    if team:
        conditions["team"] = team

    start_date = add_days(nowdate(), -cint(days))

    performances = frappe.get_all(
        "Daily Performance",
        filters={**conditions, "date": [">=", start_date]},
        fields=["date", "completion_percentage", "daily_rating", "actual_hours"],
        order_by="date asc",
    )

    chart_data = {}
    for perf in performances:
        date_str = str(perf.date)
        if date_str not in chart_data:
            chart_data[date_str] = {
                "completion": [],
                "rating": [],
                "hours": [],
            }
        chart_data[date_str]["completion"].append(perf.completion_percentage or 0)
        chart_data[date_str]["rating"].append(perf.daily_rating or 0)
        chart_data[date_str]["hours"].append(perf.actual_hours or 0)

    labels = sorted(chart_data.keys())
    avg_completion = [
        sum(chart_data[d]["completion"]) / len(chart_data[d]["completion"])
        if chart_data[d]["completion"]
        else 0
        for d in labels
    ]
    avg_rating = [
        sum(chart_data[d]["rating"]) / len(chart_data[d]["rating"])
        if chart_data[d]["rating"]
        else 0
        for d in labels
    ]

    return {
        "labels": labels,
        "datasets": [
            {"name": "Avg Completion %", "values": avg_completion},
            {"name": "Avg Rating", "values": avg_rating},
        ],
    }


@frappe.whitelist()
def get_monthly_trend_chart(year=None):
    """Get monthly trend chart data."""
    if not year:
        year = getdate(nowdate()).year

    months = []
    scores = []

    for month in range(1, 13):
        avg_score = frappe.db.get_value(
            "Performance Scorecard",
            filters={
                "month": month,
                "year": cint(year),
                "docstatus": 1,
            },
            fieldname="avg(overall_score)",
        )

        months.append(frappe.utils.formatdate(f"{year}-{month:02d}-01", "MMM"))
        scores.append(flt(avg_score, 2) if avg_score else 0)

    return {
        "labels": months,
        "datasets": [{"name": "Average Score", "values": scores}],
    }


@frappe.whitelist()
def get_performance_distribution(month=None, year=None):
    """Get performance distribution chart data."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    grades = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": cint(month),
            "year": cint(year),
            "docstatus": 1,
        },
        fields=["final_grade"],
    )

    distribution = {
        "Excellent": 0,
        "Very Good": 0,
        "Good": 0,
        "Average": 0,
        "Needs Improvement": 0,
    }

    for grade in grades:
        if grade.final_grade in distribution:
            distribution[grade.final_grade] += 1

    return {
        "labels": list(distribution.keys()),
        "values": list(distribution.values()),
    }
