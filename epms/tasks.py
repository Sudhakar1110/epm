import frappe
from frappe import _
from frappe.utils import getdate, nowdate, cint, flt, add_days, get_first_day, get_last_day
from datetime import datetime


def daily_tasks():
    """Run daily tasks."""
    frappe.logger().info("EPMS: Running daily tasks")
    
    # Update pending tasks status
    update_pending_task_statuses()
    
    # Send daily reminders to team members
    send_daily_reminders()
    
    frappe.db.commit()


def update_pending_task_statuses():
    """Update statuses of pending tasks."""
    today = getdate(nowdate())
    
    # Get overdue tasks
    overdue_tasks = frappe.get_all(
        "Pending Task",
        filters={
            "expected_completion": ["<", today],
            "current_status": ["in", ["Pending", "In Progress"]],
            "docstatus": 1,
        },
        fields=["name", "employee", "employee_name", "task"],
    )
    
    for task in overdue_tasks:
        frappe.get_doc("Pending Task", task.name).db_set(
            "current_status", "Blocked", update_modified=True
        )
        frappe.logger().info(f"EPMS: Task {task.name} marked as overdue")


def send_pending_task_reminders():
    """Send reminders for pending tasks."""
    today = getdate(nowdate())
    tomorrow = add_days(today, 1)
    
    # Get tasks due tomorrow
    tasks_due_tomorrow = frappe.get_all(
        "Pending Task",
        filters={
            "expected_completion": tomorrow,
            "current_status": ["in", ["Pending", "In Progress"]],
            "docstatus": 1,
        },
        fields=["name", "employee", "employee_name", "task", "priority"],
    )
    
    for task in tasks_due_tomorrow:
        send_notification(
            user=task.employee,
            subject=f"Reminder: Task Due Tomorrow - {task.task}",
            message=f"Your task '{task.task}' is due tomorrow. Priority: {task.priority}",
            reference_doctype="Pending Task",
            reference_name=task.name,
        )


def send_late_update_reminders():
    """Send reminders to team leaders for late updates."""
    today = getdate(nowdate())
    
    # Get team leaders
    team_leaders = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name", "team_leader"],
    )
    
    for team in team_leaders:
        # Check if leader has updated today
        today_updates = frappe.db.count(
            "Daily Performance",
            filters={
                "team": team.name,
                "date": today,
                "docstatus": 1,
            },
        )
        
        if today_updates == 0 and team.team_leader:
            send_notification(
                user=team.team_leader,
                subject=f"Reminder: Update Daily Performance - {team.team_name}",
                message=f"Please update the daily performance for team '{team.team_name}'.",
            )


def send_weekly_summary():
    """Send weekly summary to founders and team leaders."""
    from frappe.utils import get_week_start, get_week_end
    
    week_start = get_week_start(nowdate())
    week_end = get_week_end(nowdate())
    
    # Get all active teams
    teams = frappe.get_all(
        "Team",
        filters={"status": "Active"},
        fields=["name", "team_name", "team_leader"],
    )
    
    for team in teams:
        # Calculate team weekly stats
        stats = frappe.db.get_value(
            "Daily Performance",
            {
                "team": team.name,
                "date": ["between", [week_start, week_end]],
                "docstatus": 1,
            },
            [
                "count(name) as total_entries",
                "avg(daily_rating) as avg_rating",
                "sum(hours_worked_actual) as total_hours",
            ],
            as_dict=True,
        )
        
        # Send to team leader
        if team.team_leader:
            message = f"Weekly Summary for {team.team_name}:\n"
            message += f"Total Entries: {stats.total_entries or 0}\n"
            message += f"Average Rating: {flt(stats.avg_rating or 0, 2)}\n"
            message += f"Total Hours: {flt(stats.total_hours or 0, 2)}"
            
            send_notification(
                user=team.team_leader,
                subject=f"Weekly Summary - {team.team_name}",
                message=message,
            )
        
        # Send to founders
        founders = frappe.get_all(
            "Has Role",
            filters={"role": "EPMS Founder", "parenttype": "User"},
            pluck="parent",
        )
        
        for founder in founders:
            send_notification(
                user=founder,
                subject=f"Weekly Summary - {team.team_name}",
                message=message,
            )


def send_low_performance_alerts():
    """Send alerts for low performance."""
    current_month = getdate(nowdate()).month
    current_year = getdate(nowdate()).year
    
    low_performers = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": current_month,
            "year": current_year,
            "overall_score": ["<", 60],
            "docstatus": 1,
        },
        fields=["employee", "employee_name", "overall_score", "final_grade"],
    )
    
    for performer in low_performers:
        # Notify founders
        founders = frappe.get_all(
            "Has Role",
            filters={"role": "EPMS Founder", "parenttype": "User"},
            pluck="parent",
        )
        
        for founder in founders:
            send_notification(
                user=founder,
                subject=f"Low Performance Alert - {performer.employee_name}",
                message=f"{performer.employee_name} has a low score of {performer.overall_score} ({performer.final_grade})",
                reference_doctype="Performance Scorecard",
            )
        
        # Notify team leader
        team = frappe.db.get_value(
            "Team Member Mapping",
            {"employee": performer.employee},
            "team",
        )
        
        if team:
            team_leader = frappe.db.get_value("Team", team, "team_leader")
            if team_leader:
                send_notification(
                    user=team_leader,
                    subject=f"Low Performance Alert - {performer.employee_name}",
                    message=f"{performer.employee_name} has a low score of {performer.overall_score} ({performer.final_grade})",
                    reference_doctype="Performance Scorecard",
                )


def generate_monthly_scorecards():
    """Generate monthly scorecards for all employees."""
    frappe.logger().info("EPMS: Generating monthly scorecards")
    
    # Get previous month
    today = getdate(nowdate())
    if today.month == 1:
        target_month = 12
        target_year = today.year - 1
    else:
        target_month = today.month - 1
        target_year = today.year
    
    # Get all active employees with performance data
    employees = frappe.get_all(
        "Daily Performance",
        filters={
            "date": ["between", [
                get_first_day(f"{target_year}-{target_month:02d}-01"),
                get_last_day(f"{target_year}-{target_month:02d}-01"),
            ]],
            "docstatus": 1,
        },
        pluck="employee",
        distinct=True,
    )
    
    for employee in employees:
        # Check if scorecard already exists
        existing = frappe.db.exists(
            "Performance Scorecard",
            {
                "employee": employee,
                "month": target_month,
                "year": target_year,
            },
        )
        
        if not existing:
            scorecard = frappe.get_doc(
                {
                    "doctype": "Performance Scorecard",
                    "employee": employee,
                    "month": target_month,
                    "year": target_year,
                }
            )
            scorecard.insert(ignore_permissions=True)
            scorecard.submit()
            
            frappe.logger().info(f"EPMS: Generated scorecard for {employee}")
    
    frappe.db.commit()


def recalculate_scorecards():
    """Recalculate all scorecards (runs daily at night)."""
    frappe.logger().info("EPMS: Recalculating scorecards")
    
    current_month = getdate(nowdate()).month
    current_year = getdate(nowdate()).year
    
    scorecards = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": current_month,
            "year": current_year,
            "docstatus": 1,
        },
        pluck="name",
    )
    
    for scorecard_name in scorecards:
        scorecard = frappe.get_doc("Performance Scorecard", scorecard_name)
        scorecard.calculate_scores()
        scorecard.save(ignore_permissions=True)
    
    frappe.db.commit()


def send_monthly_summary():
    """Send monthly summary to all users."""
    from epms.epms.utils import get_employee_performance_summary
    
    current_month = getdate(nowdate()).month
    current_year = getdate(nowdate()).year
    
    # Get all employees with scorecards
    scorecards = frappe.get_all(
        "Performance Scorecard",
        filters={
            "month": current_month,
            "year": current_year,
            "docstatus": 1,
        },
        fields=["employee", "employee_name", "overall_score", "final_grade"],
    )
    
    for scorecard in scorecards:
        send_notification(
            user=scorecard.employee,
            subject=f"Monthly Performance Summary - {current_month}/{current_year}",
            message=f"Your overall score: {scorecard.overall_score} ({scorecard.final_grade})",
            reference_doctype="Performance Scorecard",
        )


def send_daily_reminders():
    """Send daily reminders to team members."""
    team_members = frappe.get_all(
        "Team Member Mapping",
        filters={"status": "Active"},
        fields=["user", "employee_name", "team"],
    )
    
    for member in team_members:
        # Check if member has performance entry today
        today_entries = frappe.db.count(
            "Daily Performance",
            filters={
                "employee": member.user,
                "date": getdate(nowdate()),
                "docstatus": 1,
            },
        )
        
        if today_entries == 0 and member.user:
            send_notification(
                user=member.user,
                subject="Daily Performance Reminder",
                message="Please submit your daily performance entry for today.",
            )


def send_performance_published(employee, scorecard_name):
    """Notify employee when their scorecard is published."""
    scorecard = frappe.get_doc("Performance Scorecard", scorecard_name)
    
    send_notification(
        user=employee,
        subject="Performance Scorecard Published",
        message=f"Your performance scorecard for {scorecard.month}/{scorecard.year} has been published. Score: {scorecard.overall_score}",
        reference_doctype="Performance Scorecard",
        reference_name=scorecard_name,
    )


def send_monthly_score_generated(employee, scorecard_name):
    """Notify when monthly score is generated."""
    scorecard = frappe.get_doc("Performance Scorecard", scorecard_name)
    
    send_notification(
        user=employee,
        subject="Monthly Score Generated",
        message=f"Your monthly scorecard for {scorecard.month}/{scorecard.year} has been generated.",
        reference_doctype="Performance Scorecard",
        reference_name=scorecard_name,
    )


def send_notification(user, subject, message, reference_doctype=None, reference_name=None):
    """Send notification to a user."""
    if not user:
        return
    
    try:
        frappe.get_doc(
            {
                "doctype": "Notification Log",
                "for_user": user,
                "subject": subject,
                "type": "Information",
                "read": 0,
                "document_type": reference_doctype,
                "document_name": reference_name,
            }
        ).insert(ignore_permissions=True)
        
        frappe.logger().info(f"EPMS: Notification sent to {user}: {subject}")
    except Exception as e:
        frappe.log_error(f"EPMS Notification Error: {str(e)}")
