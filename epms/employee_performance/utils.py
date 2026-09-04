import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, flt


def boot_session(bootinfo):
    """Add EPMS data to boot session via extend_bootinfo hook."""
    try:
        bootinfo.epms_roles = get_user_roles()
        bootinfo.epms_teams = get_user_teams()
        bootinfo.epms_is_founder = has_role("EPMS Founder")
        bootinfo.epms_is_team_leader = has_role("EPMS Team Leader")
        bootinfo.epms_is_team_member = has_role("EPMS Team Member")
    except Exception:
        # Never break the desk if EPMS data fails to load
        pass


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

    try:
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
    except Exception:
        pass

    return teams


def has_role(role):
    """Check if current user has a role."""
    try:
        user_roles = frappe.get_roles(frappe.session.user)
        return role in user_roles
    except Exception:
        return False


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


# ------------------------------------------------------------
# Portal page helpers (used by templates/pages/*/index.py)
# ------------------------------------------------------------

PRIORITY_CLASS_MAP = {
    "Low": "b-gray",
    "Medium": "b-blue",
    "High": "b-amber",
    "Critical": "b-red",
}

TASK_STATUS_CLASS_MAP = {
    "Pending": "b-amber",
    "In Progress": "b-blue",
    "Completed": "b-green",
    "Blocked": "b-red",
}

GRADE_CLASS_MAP = {
    "Excellent": "b-teal",
    "Very Good": "b-green",
    "Good": "b-blue",
    "Average": "b-amber",
    "Needs Improvement": "b-red",
}

PERF_STATUS_CLASS_MAP = {
    "On Track": "b-green",
    "Needs Attention": "b-amber",
    "At Risk": "b-red",
}


def portal_login_redirect():
    """Redirect guests to the login page."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect


def portal_user_role():
    """Human readable role for the current user."""
    if has_role("EPMS Founder"):
        return "Founder"
    if has_role("EPMS Team Leader"):
        return "Team Leader"
    return "Team Member"


def portal_setup_common(context):
    """Populate context keys shared by every portal page."""
    user = frappe.get_doc("User", frappe.session.user)
    user_name = user.full_name or frappe.session.user
    context.user_name = user_name
    context.user_initial = (user_name[:1] or "U").upper()
    context.user_role = portal_user_role()
    context.date_label = frappe.utils.formatdate(nowdate(), "EEEE, d MMMM yyyy")
    context.pending_count = frappe.db.count(
        "Pending Task",
        filters={"current_status": ["in", ["Pending", "In Progress"]], "docstatus": 1},
    )
    context.no_cache = 1


def portal_annotate_task(row):
    """Add display/class helpers to a Pending Task dict."""
    row = row or {}
    row["priority_class"] = PRIORITY_CLASS_MAP.get(row.get("priority"), "b-gray")
    row["status_class"] = TASK_STATUS_CLASS_MAP.get(row.get("current_status"), "b-gray")
    due = row.get("expected_completion")
    row["is_overdue"] = bool(due and str(due) < str(nowdate()))
    return row


def portal_annotate_scorecard(row):
    """Add display/class helpers to a Performance Scorecard dict."""
    row = row or {}
    row["overall_score"] = flt(row.get("overall_score"), 1)
    row["grade_class"] = GRADE_CLASS_MAP.get(row.get("final_grade"), "b-gray")
    row["status_class"] = PERF_STATUS_CLASS_MAP.get(row.get("performance_status"), "b-gray")
    row["attendance_score"] = flt(row.get("attendance_score"), 0)
    row["productivity_score"] = flt(row.get("productivity_score"), 0)
    row["quality_score"] = flt(row.get("quality_score"), 0)
    return row


def portal_open_tasks(filters=None, limit=None):
    """Open (Pending/In Progress) tasks for portal pages."""
    base = {"current_status": ["in", ["Pending", "In Progress"]], "docstatus": 1}
    if filters:
        base.update(filters)
    tasks = frappe.get_all(
        "Pending Task",
        filters=base,
        fields=[
            "name",
            "task",
            "employee_name",
            "team",
            "assigned_date",
            "expected_completion",
            "priority",
            "current_status",
        ],
        order_by="expected_completion asc",
    )
    if limit:
        tasks = tasks[:limit]
    return [portal_annotate_task(t) for t in tasks]


def portal_current_scorecards(order_by="overall_score desc", limit=None):
    """Scorecards for the current month/year."""
    scorecards = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": getdate(nowdate()).month,
            "year": getdate(nowdate()).year,
            "docstatus": 1,
        },
        fields=[
            "name",
            "employee_name",
            "team",
            "month",
            "year",
            "overall_score",
            "final_grade",
            "performance_status",
            "attendance_score",
            "productivity_score",
            "quality_score",
            "tasks_completed",
            "pending_tasks",
        ],
        order_by=order_by,
    )
    if limit:
        scorecards = scorecards[:limit]
    return [portal_annotate_scorecard(s) for s in scorecards]


def portal_month_label(month=None, year=None):
    """Human readable label like 'September 2026'."""
    month = month or getdate(nowdate()).month
    year = year or getdate(nowdate()).year
    return frappe.utils.formatdate(f"{cint(year)}-{cint(month):02d}-01", "MMMM yyyy")


# Portal-viewable script reports. Folders mirror the module layout under
# epms/employee_performance/report/<folder>/<folder>.py
PORTAL_REPORTS = [
    {"name": "Daily Performance Report", "slug": "daily-performance", "folder": "daily_performance_report", "description": "Daily performance summary for every employee"},
    {"name": "Monthly Performance Report", "slug": "monthly-performance", "folder": "monthly_performance_report", "description": "Monthly performance overview and trends"},
    {"name": "Employee Wise Report", "slug": "employee-wise", "folder": "employee_wise_report", "description": "Performance data filtered by employee"},
    {"name": "Team Wise Report", "slug": "team-wise", "folder": "team_wise_report", "description": "Team-level performance comparison"},
    {"name": "Pending Task Report", "slug": "pending-task", "folder": "pending_task_report", "description": "Overview of pending tasks and deadlines"},
    {"name": "Top Performers", "slug": "top-performers", "folder": "top_performers", "description": "Ranked list of the highest performers"},
    {"name": "Low Performers", "slug": "low-performers", "folder": "low_performers", "description": "Employees who may need improvement support"},
    {"name": "Monthly KPI Report", "slug": "monthly-kpi", "folder": "monthly_kpi_report", "description": "Key performance indicators by month"},
    {"name": "Leaderboard Report", "slug": "leaderboard", "folder": "leaderboard_report", "description": "Employee ranking leaderboard"},
    {"name": "Daily Summary Report", "slug": "daily-summary", "folder": "daily_summary_report", "description": "Complete daily summary across all teams"},
]


def portal_user_candidates():
    """Enabled system users for portal pickers (same pool the desk shows)."""
    candidates = []
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "full_name", "email"],
        order_by="full_name asc",
    )
    for u in users:
        label = (u.get("full_name") or "").strip() or u.get("email") or u.get("name")
        candidates.append({"name": u.get("name"), "label": f"{label} ({u.get('name')})"})
    return candidates


def portal_reports():
    """Registry of portal-viewable reports (never opens the ERP desk)."""
    return [dict(r) for r in PORTAL_REPORTS]


def portal_run_report(slug, filters=None):
    """Execute a portal script report and return its columns/data for rendering."""
    report = next((r for r in PORTAL_REPORTS if r["slug"] == slug), None)
    if not report:
        return None

    module = "epms.employee_performance.report.{folder}.{folder}".format(folder=report["folder"])
    try:
        columns, data, _message, _chart = frappe.get_attr(module + ".execute")(filters or {})
    except Exception:
        frappe.log_error(f"EPMS Portal Report Error: {slug}", "epms")
        return None

    return {
        "name": report["name"],
        "description": report["description"],
        "slug": slug,
        "columns": columns or [],
        "data": data or [],
    }


def portal_format_report_value(value, fieldtype=None):
    """Light formatting for report cells shown in the portal table."""
    if value is None:
        return ""
    if fieldtype in ("Float", "Percent", "Currency", "Duration", "Rating"):
        try:
            num = float(value)
        except (TypeError, ValueError):
            return str(value)
        return str(int(num)) if num == int(num) else f"{num:.2f}".rstrip("0").rstrip(".")
    return str(value)
