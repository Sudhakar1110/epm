import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, flt


def boot_session(bootinfo):
    """Add EPMS data to boot session via extend_bootinfo hook."""
    bootinfo.epms_roles = get_user_roles()
    bootinfo.epms_teams = get_user_teams()
    bootinfo.epms_is_founder = has_role("EPMS Founder")
    bootinfo.epms_is_team_leader = has_role("EPMS Team Leader")
    bootinfo.epms_is_team_member = has_role("EPMS Team Member")


def get_user_roles():
    """Get EPMS roles for current user."""
    roles = []
    if has_role("EPMS Founder"):
        roles.append("EPMS Founder")
    if has_role("EPMS Team Leader"):
        roles.append("EPMS Team Leader")
    if has_role("EPMS Team Member"):
        roles.append("EPMS Team Member")
    return roles


def get_user_teams():
    """Get teams for current user."""
    user = frappe.session.user
    teams = []

    if has_role("EPMS Founder"):
        teams = frappe.get_all("Team", fields=["name", "team_name"])
    elif has_role("EPMS Team Leader"):
        teams = frappe.get_all(
            "Team",
            filters={"team_leader": user},
            fields=["name", "team_name"],
        )
    elif has_role("EPMS Team Member"):
        team_names = frappe.get_all(
            "Team Member Mapping",
            filters={"user": user, "status": "Active"},
            pluck="team",
        )
        if team_names:
            teams = frappe.get_all(
                "Team",
                filters={"name": ["in", team_names]},
                fields=["name", "team_name"],
            )

    return teams


def has_role(role):
    """Check if current user has a role."""
    user_roles = frappe.get_roles(frappe.session.user)
    return role in user_roles


def get_employee_performance_summary(employee, month=None, year=None):
    """Get performance summary for an employee."""
    if not month:
        month = getdate(nowdate()).month
    if not year:
        year = getdate(nowdate()).year

    scorecard = frappe.db.get_value(
        "Performance Scorecard",
        {
            "employee": employee,
            "month": cint(month),
            "year": cint(year),
        },
        [
            "name",
            "overall_score",
            "final_grade",
            "performance_status",
            "tasks_completed",
            "pending_tasks",
            "average_rating",
            "average_quality",
        ],
        as_dict=True,
    )

    return scorecard


def get_team_summary(team):
    """Get team performance summary."""
    members = frappe.get_all(
        "Team Member Mapping",
        filters={"team": team, "status": "Active"},
        fields=["employee", "employee_name"],
    )

    summary = {
        "total_members": len(members),
        "members": [],
    }

    current_month = getdate(nowdate()).month
    current_year = getdate(nowdate()).year

    for member in members:
        perf = frappe.db.get_value(
            "Performance Scorecard",
            {
                "employee": member.employee,
                "month": current_month,
                "year": current_year,
            },
            ["overall_score", "final_grade", "tasks_completed"],
            as_dict=True,
        )

        summary["members"].append(
            {
                "employee": member.employee,
                "employee_name": member.employee_name,
                "score": perf.overall_score if perf else 0,
                "grade": perf.final_grade if perf else "N/A",
                "tasks": perf.tasks_completed if perf else 0,
            }
        )

    return summary


def calculate_productivity_score(tasks_completed, hours_worked, avg_completion_pct):
    """Calculate productivity score (0-100)."""
    task_score = min(tasks_completed * 5, 40)
    hours_score = min(hours_worked * 1.5, 30)
    completion_score = (avg_completion_pct / 100) * 30
    return min(task_score + hours_score + completion_score, 100)


def calculate_quality_score(avg_rating, avg_quality):
    """Calculate quality score (0-100)."""
    rating_score = (avg_rating / 10) * 60
    quality_score = (avg_quality / 10) * 40
    return min(rating_score + quality_score, 100)


def calculate_attendance_score(employee, month, year):
    """Calculate attendance score based on performance entries."""
    from frappe.utils import get_first_day, get_last_day, date_diff

    first_day = get_first_day(f"{year}-{month:02d}-01")
    last_day = get_last_day(f"{year}-{month:02d}-01")

    total_working_days = date_diff(last_day, first_day) + 1

    days_with_entries = frappe.db.count(
        "Daily Performance",
        filters={
            "employee": employee,
            "date": ["between", [first_day, last_day]],
            "docstatus": 1,
        },
    )

    if total_working_days <= 0:
        return 100

    score = (days_with_entries / total_working_days) * 100
    return min(score, 100)


def get_grade(score):
    """Get grade based on score."""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Average"
    else:
        return "Needs Improvement"


def get_performance_status(score):
    """Get performance status based on score."""
    if score >= 80:
        return "On Track"
    elif score >= 60:
        return "Needs Attention"
    else:
        return "At Risk"
