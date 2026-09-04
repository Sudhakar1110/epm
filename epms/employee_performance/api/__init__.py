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


# Portal API Endpoints

@frappe.whitelist()
def get_portal_stats():
    """Get portal dashboard stats."""
    teams = frappe.db.count("Team", {"status": "Active"})
    members = frappe.db.count("Team Member Mapping", {"status": "Active"})
    pending_tasks = frappe.db.count("Pending Task", {
        "current_status": ["in", ["Pending", "In Progress"]],
        "docstatus": 1,
    })
    avg_score = frappe.db.get_value(
        "Performance Scorecard",
        {"month": getdate(nowdate()).month, "year": getdate(nowdate()).year, "docstatus": 1},
        "avg(overall_score)",
    )
    return {
        "teams": teams or 0,
        "members": members or 0,
        "pending_tasks": pending_tasks or 0,
        "avg_score": round(flt(avg_score, 1) if avg_score else 0, 1),
    }


@frappe.whitelist()
def get_portal_teams():
    """Get all teams for portal."""
    return frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name", "team_leader", "total_members", "status"],
        order_by="team_name asc",
    )


@frappe.whitelist()
def get_portal_scorecards():
    """Get current month scorecards for portal."""
    return frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": getdate(nowdate()).month,
            "year": getdate(nowdate()).year,
            "docstatus": 1,
        },
        fields=["employee_name", "team", "overall_score", "final_grade", "performance_status"],
        order_by="overall_score desc",
    )


@frappe.whitelist()
def get_portal_tasks():
    """Get pending tasks for portal."""
    return frappe.get_all(
        "Pending Task",
        filters={
            "current_status": ["in", ["Pending", "In Progress"]],
            "docstatus": 1,
        },
        fields=["task", "employee_name", "expected_completion", "priority", "current_status"],
        order_by="expected_completion asc",
        limit_page_length=20,
    )


@frappe.whitelist()
def get_portal_top_performers():
    """Get top performers for portal dashboard."""
    return frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": getdate(nowdate()).month,
            "year": getdate(nowdate()).year,
            "docstatus": 1,
        },
        fields=["employee_name", "overall_score", "final_grade"],
        order_by="overall_score desc",
        limit_page_length=10,
    )


@frappe.whitelist()
def get_portal_notifications(limit=20):
    """Recent Notification Logs for the current user (portal bell dropdown)."""
    user = frappe.session.user

    try:
        limit = cint(limit) or 20
    except Exception:
        limit = 20

    notifications = frappe.get_all(
        "Notification Log",
        filters={"for_user": user},
        fields=[
            "name",
            "subject",
            "read",
            "creation",
            "document_type",
            "document_name",
        ],
        order_by="creation desc",
        limit_page_length=limit,
    )

    # Where each referenced doctype lives inside the portal (never the desk)
    portal_routes = {
        "Pending Task": "/epms/tasks",
        "Performance Scorecard": "/epms/scorecards",
        "Daily Performance": "/epms/my-day",
    }

    for n in notifications:
        n["subject"] = n.get("subject") or "Notification"
        n["document_type"] = n.get("document_type") or ""
        n["portal_route"] = portal_routes.get(n["document_type"], "")
        try:
            n["creation_label"] = frappe.utils.pretty_date(n.get("creation"))
        except Exception:
            n["creation_label"] = str(n.get("creation") or "")

    unread_count = frappe.db.count("Notification Log", {"for_user": user, "read": 0})

    return {
        "notifications": notifications,
        "unread_count": unread_count or 0,
    }


@frappe.whitelist()
def set_portal_notifications_read(name=None):
    """Mark one notification (or all) of the current user as read."""
    user = frappe.session.user

    if name:
        if frappe.db.exists("Notification Log", {"name": name, "for_user": user}):
            frappe.db.set_value("Notification Log", name, "read", 1)
    else:
        frappe.db.sql(
            "update `tabNotification Log` set `read` = 1 "
            "where `for_user` = %s and `read` = 0",
            (user,),
        )

    frappe.db.commit()
    return {"ok": True}


@frappe.whitelist()
def create_portal_team(team_name=None, team_leader=None, description=None):
    """Create a Team from the portal. Same doctype as the desk, so it appears there too.

    Never raises: failures are returned as {"ok": False, "error": "..."} so the
    portal dialog can always show a readable message.
    """
    team_name = (team_name or "").strip()
    team_leader = (team_leader or "").strip()

    if not team_name:
        return {"ok": False, "error": _("Please enter a team name.")}
    if not team_leader:
        return {"ok": False, "error": _("Please choose a team leader.")}

    try:
        if not frappe.db.exists("User", team_leader):
            return {"ok": False, "error": _("The selected team leader does not exist.")}

        existing = frappe.db.sql(
            "select name from `tabTeam` where lower(name) = lower(%s)",
            team_name,
        )
        if existing:
            return {"ok": False, "error": _("A team named \"{0}\" already exists.").format(existing[0][0])}

        # Keep portal and desk in sync: a user picked as leader but without the
        # role yet is promoted automatically (mirrors Team Member Mapping).
        user_roles = frappe.get_roles(team_leader)
        if "EPMS Team Leader" not in user_roles and "EPMS Founder" not in user_roles:
            frappe.get_doc("User", team_leader).add_roles("EPMS Team Leader")

        team = frappe.get_doc(
            {
                "doctype": "Team",
                "team_name": team_name,
                "team_leader": team_leader,
                "description": (description or "").strip() or None,
                "status": "Active",
            }
        )

        # No ignore_permissions: only roles with create rights on Team can create.
        team.insert()
        frappe.db.commit()
        return {"ok": True, "name": team.name}
    except frappe.DuplicateEntryError:
        frappe.db.rollback()
        return {"ok": False, "error": _("A team named \"{0}\" already exists.").format(team_name)}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        message = str(e).replace("[", "").replace("]", "").strip()
        return {"ok": False, "error": message or _("Could not create the team. Please check the details.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Create Portal Team")
        return {"ok": False, "error": _("Could not create the team. An unexpected error occurred (see Error Log \"EPMS Create Portal Team\").")}


@frappe.whitelist()
def create_portal_pending_task(employee=None, task=None, priority=None, expected_completion=None, assigned_date=None, remarks=None):
    """Create + submit a Pending Task from the portal (shows up on the desk too)."""
    employee = (employee or "").strip()
    task = (task or "").strip()
    expected_completion = (expected_completion or "").strip()

    if not employee:
        return {"ok": False, "error": _("Please choose an employee.")}
    if not task:
        return {"ok": False, "error": _("Please enter a task.")}
    if not expected_completion:
        return {"ok": False, "error": _("Please set the expected completion date.")}

    priority = (priority or "").strip() or "Medium"
    if priority not in ("Low", "Medium", "High", "Critical"):
        return {"ok": False, "error": _("Invalid priority.")}

    try:
        if not frappe.db.exists("User", employee):
            return {"ok": False, "error": _("The selected employee does not exist.")}

        doc = frappe.get_doc(
            {
                "doctype": "Pending Task",
                "employee": employee,
                "task": task,
                "priority": priority,
                "expected_completion": expected_completion,
                "assigned_date": (assigned_date or "").strip() or None,
                "current_status": "Pending",
                "remarks": (remarks or "").strip() or None,
            }
        )
        doc.insert()
        doc.submit()
        frappe.db.commit()
        return {"ok": True, "name": doc.name}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        message = str(e).replace("[", "").replace("]", "").strip()
        return {"ok": False, "error": message or _("Could not create the task. Please check the details.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Create Portal Task")
        return {"ok": False, "error": _("Could not create the task. An unexpected error occurred (see Error Log \"EPMS Create Portal Task\").")}


@frappe.whitelist()
def create_portal_scorecard(employee=None, month=None, year=None):
    """Create + submit a Performance Scorecard from the portal (shows up on the desk too)."""
    employee = (employee or "").strip()

    if not employee:
        return {"ok": False, "error": _("Please choose an employee.")}

    try:
        month = int(month or 0)
        year = int(year or 0)
    except (TypeError, ValueError):
        return {"ok": False, "error": _("Invalid month or year.")}

    if month < 1 or month > 12:
        return {"ok": False, "error": _("Month must be between 1 and 12.")}
    if year < 2000 or year > 2100:
        return {"ok": False, "error": _("Year must be between 2000 and 2100.")}

    try:
        if not frappe.db.exists("User", employee):
            return {"ok": False, "error": _("The selected employee does not exist.")}

        if frappe.db.exists(
            "Performance Scorecard",
            {"employee": employee, "month": month, "year": year},
        ):
            return {"ok": False, "error": _("A scorecard for this employee already exists for {0}/{1}.").format(month, year)}

        doc = frappe.get_doc(
            {
                "doctype": "Performance Scorecard",
                "employee": employee,
                "month": month,
                "year": year,
            }
        )
        doc.insert()
        doc.submit()
        frappe.db.commit()
        return {"ok": True, "name": doc.name}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        message = str(e).replace("[", "").replace("]", "").strip()
        return {"ok": False, "error": message or _("Could not create the scorecard. Please check the details.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Create Portal Scorecard")
        return {"ok": False, "error": _("Could not create the scorecard. An unexpected error occurred (see Error Log \"EPMS Create Portal Scorecard\").")}


# ------------------------------------------------------------
# Portal management APIs (team, task, daily entry, profile,
# exports, import, settings) — all GET-friendly and never raise.
# ------------------------------------------------------------

def _is_founder(user=None):
    return "EPMS Founder" in frappe.get_roles(user or frappe.session.user)


def _leader_of_team(team, user=None):
    return frappe.db.get_value("Team", team, "team_leader") == (user or frappe.session.user)


@frappe.whitelist()
def get_portal_team(team=None):
    """Team detail: info + active members."""
    team = (team or "").strip()
    if not team or not frappe.db.exists("Team", team):
        return {"ok": False, "error": _("Team not found.")}

    info = frappe.db.get_value(
        "Team", team, ["name", "team_name", "team_leader", "description", "total_members", "status"], as_dict=True
    )
    leader_name = info.get("team_leader")
    if leader_name:
        info["leader_name"] = frappe.db.get_value("User", leader_name, "full_name") or leader_name
    else:
        info["leader_name"] = ""

    members = frappe.get_all(
        "Team Member Mapping",
        filters={"team": team, "status": "Active"},
        fields=["name", "user", "employee_name", "designation", "joining_date"],
        order_by="employee_name asc",
    )

    user = frappe.session.user
    return {
        "ok": True,
        "team": info,
        "members": members,
        "can_manage": _is_founder(user) or _leader_of_team(team, user),
    }


@frappe.whitelist()
def add_portal_team_member(team=None, user=None):
    """Add an enabled user to a team (auto-assigns Team Member role)."""
    team = (team or "").strip()
    user = (user or "").strip()

    if not team or not user:
        return {"ok": False, "error": _("Team and user are required.")}

    me = frappe.session.user
    if not (_is_founder(me) or _leader_of_team(team, me)):
        return {"ok": False, "error": _("Not permitted to manage this team.")}

    try:
        if not frappe.db.exists("Team", team):
            return {"ok": False, "error": _("Team not found.")}
        if not frappe.db.exists("User", user):
            return {"ok": False, "error": _("User not found.")}
        if frappe.db.exists("Team Member Mapping", {"user": user, "team": team, "status": "Active"}):
            return {"ok": False, "error": _("User is already an active member of this team.")}

        full_name = frappe.db.get_value("User", user, "full_name") or user
        doc = frappe.get_doc(
            {
                "doctype": "Team Member Mapping",
                "employee": user,
                "user": user,
                "employee_name": full_name,
                "team": team,
                "status": "Active",
            }
        )
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"ok": True, "name": doc.name}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not add member.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Add Portal Team Member")
        return {"ok": False, "error": _("Could not add member. An unexpected error occurred.")}


@frappe.whitelist()
def remove_portal_team_member(name=None):
    """Deactivate a team member mapping (founder can delete it)."""
    name = (name or "").strip()
    if not name:
        return {"ok": False, "error": _("Member record is required.")}

    try:
        mapping = frappe.get_doc("Team Member Mapping", name)
        team = mapping.team
        me = frappe.session.user
        if not (_is_founder(me) or _leader_of_team(team, me)):
            return {"ok": False, "error": _("Not permitted to manage this team.")}
        if _is_founder(me):
            mapping.delete()
        else:
            mapping.db_set("status", "Inactive")
        frappe.db.commit()
        return {"ok": True}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not remove member.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Remove Portal Team Member")
        return {"ok": False, "error": _("Could not remove member. An unexpected error occurred.")}


@frappe.whitelist()
def set_portal_team_leader(team=None, team_leader=None):
    """Change a team's leader (auto-assigns Team Leader role when needed)."""
    team = (team or "").strip()
    team_leader = (team_leader or "").strip()

    if not team or not team_leader:
        return {"ok": False, "error": _("Team and team leader are required.")}

    me = frappe.session.user
    if not (_is_founder(me) or _leader_of_team(team, me)):
        return {"ok": False, "error": _("Not permitted to manage this team.")}

    try:
        if not frappe.db.exists("User", team_leader):
            return {"ok": False, "error": _("User not found.")}
        roles = frappe.get_roles(team_leader)
        if "EPMS Team Leader" not in roles and "EPMS Founder" not in roles:
            frappe.get_doc("User", team_leader).add_roles("EPMS Team Leader")
        frappe.db.set_value("Team", team, "team_leader", team_leader)
        frappe.db.commit()
        return {"ok": True}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not change team leader.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Set Portal Team Leader")
        return {"ok": False, "error": _("Could not change team leader. An unexpected error occurred.")}


@frappe.whitelist()
def update_portal_task(name=None, current_status=None, remarks=None, completion_date=None):
    """Update a task's status/remarks/completion date from the portal."""
    name = (name or "").strip()
    if not name or not frappe.db.exists("Pending Task", name):
        return {"ok": False, "error": _("Task not found.")}

    allowed = ("Pending", "In Progress", "Completed", "Blocked")
    if current_status and current_status not in allowed:
        return {"ok": False, "error": _("Invalid status.")}

    try:
        doc = frappe.get_doc("Pending Task", name)
        me = frappe.session.user
        team = frappe.db.get_value("Team Member Mapping", {"user": doc.employee, "status": "Active"}, "team")
        is_owner = doc.employee == me
        is_leader = bool(team and _leader_of_team(team, me))
        if not (_is_founder(me) or is_owner or is_leader):
            return {"ok": False, "error": _("Not permitted to update this task.")}

        if current_status:
            doc.db_set("current_status", current_status)
        if remarks is not None:
            doc.db_set("remarks", (remarks or "").strip() or None)
        if completion_date is not None:
            doc.db_set("completion_date", (completion_date or "").strip() or None)
        if current_status == "Completed":
            doc.db_set("completion_date", (completion_date or "").strip() or str(getdate(nowdate())))
        frappe.db.commit()
        return {"ok": True, "name": doc.name}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not update the task.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Update Portal Task")
        return {"ok": False, "error": _("Could not update the task. An unexpected error occurred.")}


@frappe.whitelist()
def submit_portal_daily_performance(date=None, task_title=None, task_status=None, priority=None, work_type=None, expected_hours=None, actual_hours=None, completion_percentage=None, daily_rating=None, quality_score=None, remarks=None, challenges=None, next_day_plan=None):
    """Submit today's (or a past date's) daily performance entry for the current user."""
    me = frappe.session.user
    task_title = (task_title or "").strip()

    if not task_title:
        return {"ok": False, "error": _("Please enter a task title.")}

    try:
        date = (date or "").strip() or str(getdate(nowdate()))
        if str(date) > str(getdate(nowdate())):
            return {"ok": False, "error": _("Cannot submit for future dates.")}

        mapping = frappe.db.get_value(
            "Team Member Mapping",
            {"user": me, "status": "Active"},
            ["team", "employee_name"],
            as_dict=True,
        )
        if not mapping:
            return {"ok": False, "error": _("You are not an active member of any team.")}

        if frappe.db.exists(
            "Daily Performance",
            {"employee": me, "date": date, "docstatus": ["!=", 2]},
        ):
            return {"ok": False, "error": _("A daily performance entry already exists for {0}.").format(date)}

        doc = frappe.get_doc(
            {
                "doctype": "Daily Performance",
                "date": date,
                "team": mapping.team,
                "employee": me,
                "employee_name": mapping.employee_name or frappe.db.get_value("User", me, "full_name") or me,
                "task_title": task_title,
                "task_status": (task_status or "In Progress") if (task_status or "In Progress") in ("Completed", "In Progress", "Pending", "Blocked") else "In Progress",
                "priority": (priority or "Medium") if (priority or "Medium") in ("Low", "Medium", "High", "Critical") else "Medium",
                "work_type": (work_type or "").strip() or None,
                "expected_hours": flt(expected_hours or 8),
                "actual_hours": flt(actual_hours or 0),
                "completion_percentage": flt(completion_percentage or 0),
                "daily_rating": flt(daily_rating or 5),
                "quality_score": flt(quality_score or 5),
                "remarks": (remarks or "").strip() or None,
                "challenges": (challenges or "").strip() or None,
                "next_day_plan": (next_day_plan or "").strip() or None,
            }
        )
        doc.insert()
        doc.submit()
        frappe.db.commit()
        return {"ok": True, "name": doc.name}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not submit the entry.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Submit Portal Daily Performance")
        return {"ok": False, "error": _("Could not submit the entry. An unexpected error occurred.")}


@frappe.whitelist()
def update_portal_profile(full_name=None, new_password=None):
    """Update the current user's full name and/or password."""
    me = frappe.session.user
    full_name = (full_name or "").strip()
    new_password = (new_password or "").strip()

    if not full_name and not new_password:
        return {"ok": False, "error": _("Nothing to update.")}

    try:
        if full_name:
            frappe.db.set_value("User", me, "full_name", full_name)
        if new_password:
            if len(new_password) < 6:
                return {"ok": False, "error": _("Password must be at least 6 characters.")}
            user = frappe.get_doc("User", me)
            user.new_password = new_password
            user.save(ignore_permissions=True)
        frappe.db.commit()
        return {"ok": True}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not update profile.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Update Portal Profile")
        return {"ok": False, "error": _("Could not update profile. An unexpected error occurred.")}


@frappe.whitelist()
def import_portal_csv(kind=None, data=None):
    """Bulk import teams, users or tasks from pasted CSV text (founder only)."""
    if not _is_founder():
        return {"ok": False, "error": _("Only EPMS Founder can import.")}

    kind = (kind or "").strip()
    data = (data or "").strip()
    if kind not in ("teams", "users", "tasks"):
        return {"ok": False, "error": _("Invalid import type.")}
    if not data:
        return {"ok": False, "error": _("Paste some CSV data first.")}

    created = 0
    errors = []
    lines = [ln for ln in data.splitlines() if ln.strip()]
    if not lines:
        return {"ok": False, "error": _("No rows to import.")}

    # Skip a header row when it looks like one
    if lines and lines[0].lower().startswith(("team", "email", "employee")) and "," in lines[0]:
        lines = lines[1:]

    for i, ln in enumerate(lines, start=1):
        parts = [p.strip() for p in ln.split(",")]
        try:
            if kind == "teams":
                if len(parts) < 2 or not parts[0] or not parts[1]:
                    errors.append(f"row {i}: team name and leader are required")
                    continue
                name, leader, desc = parts[0], parts[1], (parts[2] if len(parts) > 2 else "")
                if frappe.db.exists("Team", name):
                    errors.append(f"row {i}: team {name} already exists")
                    continue
                roles = frappe.get_roles(leader)
                if "EPMS Team Leader" not in roles and "EPMS Founder" not in roles:
                    frappe.get_doc("User", leader).add_roles("EPMS Team Leader")
                frappe.get_doc({"doctype": "Team", "team_name": name, "team_leader": leader, "description": desc or None, "status": "Active"}).insert()
                created += 1
            elif kind == "users":
                if len(parts) < 2 or not parts[0]:
                    errors.append(f"row {i}: email is required")
                    continue
                email = parts[0]
                first = parts[1] if len(parts) > 1 else email.split("@")[0]
                last = parts[2] if len(parts) > 2 else ""
                if frappe.db.exists("User", email):
                    errors.append(f"row {i}: user {email} already exists")
                    continue
                user = frappe.get_doc(
                    {
                        "doctype": "User",
                        "email": email,
                        "first_name": first,
                        "last_name": last,
                        "enabled": 1,
                        "send_welcome_email": 0,
                        "user_type": "System User",
                    }
                ).insert(ignore_permissions=True)
                user.add_roles("EPMS Team Member")
                created += 1
            elif kind == "tasks":
                if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
                    errors.append(f"row {i}: employee, task and due date are required")
                    continue
                emp, task, due = parts[0], parts[1], parts[2]
                priority = parts[3] if len(parts) > 3 and parts[3] else "Medium"
                if not frappe.db.exists("User", emp):
                    errors.append(f"row {i}: employee {emp} not found")
                    continue
                doc = frappe.get_doc(
                    {
                        "doctype": "Pending Task",
                        "employee": emp,
                        "employee_name": frappe.db.get_value("User", emp, "full_name") or emp,
                        "task": task,
                        "priority": priority,
                        "expected_completion": due,
                        "current_status": "Pending",
                    }
                )
                doc.insert()
                doc.submit()
                created += 1
        except frappe.ValidationError as e:
            frappe.db.rollback()
            errors.append(f"row {i}: {str(e).replace('[', '').replace(']', '').strip()}")
        except Exception as e:
            frappe.db.rollback()
            errors.append(f"row {i}: {str(e)}")

    frappe.db.commit()
    return {"ok": True, "created": created, "errors": errors[:20]}


@frappe.whitelist()
def portal_save_settings(auto_generate_scorecards=None, scorecard_day=None, send_daily_reminders=None, send_weekly_summary=None, send_monthly_summary=None, low_performance_threshold=None, excellent_threshold=None, very_good_threshold=None, good_threshold=None, average_threshold=None):
    """Save EPMS Settings from the portal (founder only)."""
    if not _is_founder():
        return {"ok": False, "error": _("Only EPMS Founder can update settings.")}

    try:
        if not frappe.db.exists("EPMS Settings", "EPMS Settings"):
            frappe.get_doc({"doctype": "EPMS Settings", "name": "EPMS Settings"}).insert(ignore_permissions=True)
        doc = frappe.get_doc("EPMS Settings", "EPMS Settings")

        checks = {
            "auto_generate_scorecards": auto_generate_scorecards,
            "send_daily_reminders": send_daily_reminders,
            "send_weekly_summary": send_weekly_summary,
            "send_monthly_summary": send_monthly_summary,
        }
        for k, v in checks.items():
            if v is not None:
                doc.set(k, 1 if str(v) in ("1", "true", "True", "on") else 0)

        ints = {
            "scorecard_day": scorecard_day,
            "low_performance_threshold": low_performance_threshold,
            "excellent_threshold": excellent_threshold,
            "very_good_threshold": very_good_threshold,
            "good_threshold": good_threshold,
            "average_threshold": average_threshold,
        }
        for k, v in ints.items():
            if v not in (None, ""):
                try:
                    doc.set(k, cint(v))
                except Exception:
                    pass
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"ok": True}
    except frappe.ValidationError as e:
        frappe.db.rollback()
        return {"ok": False, "error": str(e).replace("[", "").replace("]", "").strip() or _("Could not save settings.")}
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "EPMS Portal Save Settings")
        return {"ok": False, "error": _("Could not save settings. An unexpected error occurred.")}


def _csv_text(headers, rows):
    """Simple CSV serialization."""
    def cell(v):
        v = "" if v is None else str(v)
        return '"' + v.replace('"', '""') + '"' if ("," in v or '"' in v or "\n" in v) else v
    lines = [",".join(cell(h) for h in headers)]
    for row in rows:
        lines.append(",".join(cell(v) for v in row))
    return "\n".join(lines)


@frappe.whitelist()
def export_portal_scorecards_csv(month=None, year=None, team=None):
    """CSV export of the filtered scorecard list."""
    try:
        from epms.employee_performance.utils import portal_current_scorecards
        rows = portal_current_scorecards(
            month=cint(month) if month else None,
            year=cint(year) if year else None,
            team=team or None,
        )
        headers = ["Employee", "Team", "Month", "Year", "Attendance", "Productivity", "Quality", "Overall", "Grade", "Status"]
        data = [
            [r.get("employee_name") or "", r.get("team") or "", r.get("month") or "", r.get("year") or "",
             flt(r.get("attendance_score"), 1), flt(r.get("productivity_score"), 1), flt(r.get("quality_score"), 1),
             flt(r.get("overall_score"), 1), r.get("final_grade") or "", r.get("performance_status") or ""]
            for r in rows
        ]
        return _csv_text(headers, data)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "EPMS Export Scorecards CSV")
        return ""


@frappe.whitelist()
def export_portal_report_csv(slug=None, month=None, year=None, team=None):
    """CSV export of a portal script report (with optional filters)."""
    try:
        from epms.employee_performance.utils import portal_run_report
        filters = {}
        if month:
            filters["month"] = cint(month)
        if year:
            filters["year"] = cint(year)
        if team:
            filters["team"] = team
        result = portal_run_report(slug or "", filters)
        if not result:
            return ""
        headers = [c.get("label") or c.get("fieldname") or "" for c in result["columns"]]
        rows = [[r.get(c.get("fieldname")) for c in result["columns"]] for r in result["data"]]
        return _csv_text(headers, rows)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "EPMS Export Report CSV")
        return ""
