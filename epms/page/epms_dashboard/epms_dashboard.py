import frappe
from frappe import _


@frappe.whitelist()
def get_dashboard_data():
    """Get dashboard data based on user role."""
    user_roles = frappe.get_roles(frappe.session.user)

    if "EPMS Founder" in user_roles:
        return get_founder_dashboard()
    elif "EPMS Team Leader" in user_roles:
        return get_team_leader_dashboard()
    elif "EPMS Team Member" in user_roles:
        return get_employee_dashboard()
    else:
        return {}


def get_founder_dashboard():
    """Get founder dashboard data."""
    from frappe.utils import getdate, nowdate

    today = getdate(nowdate())

    # Stats
    total_employees = frappe.db.count("User", {"user_type": "System User", "enabled": 1})
    total_teams = frappe.db.count("Team", {"status": "Active"})
    tasks_today = frappe.db.count(
        "Daily Performance", {"date": today, "docstatus": 1}
    )
    pending_tasks = frappe.db.count(
        "Pending Task",
        {"current_status": ["in", ["Pending", "In Progress"]], "docstatus": 1},
    )
    blocked_tasks = frappe.db.count(
        "Pending Task", {"current_status": "Blocked", "docstatus": 1}
    )

    # Average performance
    avg_performance = frappe.db.get_value(
        "Performance Scorecard",
        {"docstatus": 1},
        "avg(overall_score)",
    )

    # Top performer
    top_performer = frappe.get_all(
        "Performance Scorecard",
        {"docstatus": 1},
        ["employee_name", "overall_score"],
        order_by="overall_score desc",
        limit_page_length=1,
    )

    # Lowest performer
    lowest_performer = frappe.get_all(
        "Performance Scorecard",
        {"docstatus": 1},
        ["employee_name", "overall_score"],
        order_by="overall_score asc",
        limit_page_length=1,
    )

    return {
        "total_employees": total_employees,
        "total_teams": total_teams,
        "tasks_today": tasks_today,
        "pending_tasks": pending_tasks,
        "blocked_tasks": blocked_tasks,
        "avg_performance": round(avg_performance or 0, 2),
        "top_performer": top_performer[0] if top_performer else None,
        "lowest_performer": lowest_performer[0] if lowest_performer else None,
    }


def get_team_leader_dashboard():
    """Get team leader dashboard data."""
    from frappe.utils import getdate, nowdate

    today = getdate(nowdate())
    user = frappe.session.user

    # Get team
    team = frappe.db.get_value("Team", {"team_leader": user}, "name")

    if not team:
        return {}

    # Stats
    today_tasks = frappe.db.count(
        "Daily Performance", {"team": team, "date": today, "docstatus": 1}
    )
    pending_tasks = frappe.db.count(
        "Pending Task",
        {
            "employee": [
                "in",
                frappe.get_all(
                    "Team Member Mapping",
                    {"team": team, "status": "Active"},
                    pluck="user",
                ),
            ],
            "current_status": ["in", ["Pending", "In Progress"]],
            "docstatus": 1,
        },
    )
    completed_tasks = frappe.db.count(
        "Daily Performance",
        {"team": team, "task_status": "Completed", "docstatus": 1},
    )

    # Team average score
    current_month = today.month
    current_year = today.year
    team_score = frappe.db.get_value(
        "Performance Scorecard",
        {"team": team, "month": current_month, "year": current_year, "docstatus": 1},
        "avg(overall_score)",
    )

    # Top performer
    top_performer = frappe.get_all(
        "Performance Scorecard",
        {"team": team, "month": current_month, "year": current_year, "docstatus": 1},
        ["employee_name", "overall_score"],
        order_by="overall_score desc",
        limit_page_length=1,
    )

    # Lowest performer
    lowest_performer = frappe.get_all(
        "Performance Scorecard",
        {"team": team, "month": current_month, "year": current_year, "docstatus": 1},
        ["employee_name", "overall_score"],
        order_by="overall_score asc",
        limit_page_length=1,
    )

    return {
        "today_tasks": today_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "team_score": round(team_score or 0, 2),
        "top_performer": top_performer[0] if top_performer else None,
        "lowest_performer": lowest_performer[0] if lowest_performer else None,
    }


def get_employee_dashboard():
    """Get employee dashboard data."""
    from frappe.utils import getdate, nowdate

    today = getdate(nowdate())
    user = frappe.session.user

    # Today's performance
    today_perf = frappe.get_all(
        "Daily Performance",
        {"employee": user, "date": today, "docstatus": 1},
        ["daily_rating", "task_status", "completion_percentage"],
    )

    # Monthly score
    current_month = today.month
    current_year = today.year
    scorecard = frappe.db.get_value(
        "Performance Scorecard",
        {"employee": user, "month": current_month, "year": current_year, "docstatus": 1},
        ["overall_score", "final_grade", "tasks_completed", "pending_tasks"],
        as_dict=True,
    )

    return {
        "today_performance": today_perf,
        "monthly_score": scorecard,
    }
