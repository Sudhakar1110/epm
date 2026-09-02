import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, cint, flt, get_first_day, get_last_day, date_diff


class PerformanceScorecard(Document):
    def validate(self):
        self.validate_month_year()
        self.validate_no_manual_creation()
        self.calculate_scores()

    def validate_month_year(self):
        """Validate month and year."""
        if self.month and (self.month < 1 or self.month > 12):
            frappe.throw(_("Invalid month"))

        if self.year and (self.year < 2000 or self.year > 2100):
            frappe.throw(_("Invalid year"))

    def validate_no_manual_creation(self):
        """Prevent manual creation of scorecards."""
        # Allow creation only from system or API
        if not frappe.flags.in_install and not frappe.flags.in_test:
            if not frappe.db.exists(
                "Performance Scorecard",
                {"employee": self.employee, "month": self.month, "year": self.year},
            ):
                # Check if this is being created by system
                if not frappe.flags.get("allow_scorecard_creation"):
                    frappe.throw(
                        _(
                            "Scorecards are auto-generated. Cannot create manually."
                        )
                    )

    def calculate_scores(self):
        """Calculate all scores for the scorecard."""
        if not self.employee or not self.month or not self.year:
            return

        # Get date range
        first_day = get_first_day(f"{self.year}-{int(self.month):02d}-01")
        last_day = get_last_day(f"{self.year}-{int(self.month):02d}-01")

        # Get team
        if not self.team:
            self.team = frappe.db.get_value(
                "Team Member Mapping",
                {"user": self.employee, "status": "Active"},
                "team",
            )

        # Get employee name
        if not self.employee_name:
            self.employee_name = frappe.db.get_value(
                "User", self.employee, "full_name"
            ) or self.employee

        # Calculate total working days
        self.total_working_days = date_diff(last_day, first_day) + 1

        # Get daily performances
        performances = frappe.get_all(
            "Daily Performance",
            filters={
                "employee": self.employee,
                "date": ["between", [first_day, last_day]],
                "docstatus": 1,
            },
            fields=[
                "daily_rating",
                "quality_score",
                "hours_worked_actual",
                "completion_percentage",
                "task_status",
            ],
        )

        if not performances:
            self.set_zero_scores()
            return

        # Calculate tasks completed and pending
        self.tasks_completed = sum(
            1 for p in performances if p.task_status == "Completed"
        )
        self.pending_tasks = sum(
            1 for p in performances if p.task_status != "Completed"
        )

        # Calculate completion percentage
        total_tasks = self.tasks_completed + self.pending_tasks
        self.completed_percentage = (
            (self.tasks_completed / total_tasks * 100) if total_tasks > 0 else 0
        )

        # Calculate average rating
        ratings = [p.daily_rating for p in performances if p.daily_rating]
        self.average_rating = (sum(ratings) / len(ratings)) if ratings else 0

        # Calculate average quality
        qualities = [p.quality_score for p in performances if p.quality_score]
        self.average_quality = (sum(qualities) / len(qualities)) if qualities else 0

        # Calculate hours worked
        total_hours = sum(p.hours_worked_actual or 0 for p in performances)
        avg_completion = (
            sum(p.completion_percentage or 0 for p in performances) / len(performances)
        )

        # Calculate productivity score
        self.productivity_score = self._calculate_productivity_score(
            self.tasks_completed, total_hours, avg_completion
        )

        # Calculate quality score
        self.quality_score = self._calculate_quality_score(
            self.average_rating, self.average_quality
        )

        # Calculate attendance score
        self.attendance_score = self._calculate_attendance_score(
            first_day, last_day
        )

        # Calculate overall score
        # 30% Productivity + 30% Quality + 20% Attendance + 20% Task Completion
        self.overall_score = (
            (self.productivity_score * 0.30)
            + (self.quality_score * 0.30)
            + (self.attendance_score * 0.20)
            + (self.completed_percentage * 0.20)
        )

        # Set grade
        self.final_grade = self._get_grade(self.overall_score)

        # Set performance status
        self.performance_status = self._get_performance_status(self.overall_score)

    def _calculate_productivity_score(self, tasks_completed, hours_worked, avg_completion_pct):
        """Calculate productivity score (0-100)."""
        task_score = min(tasks_completed * 5, 40)  # Max 40 points
        hours_score = min(hours_worked * 1.5, 30)  # Max 30 points
        completion_score = (avg_completion_pct / 100) * 30  # Max 30 points

        return min(task_score + hours_score + completion_score, 100)

    def _calculate_quality_score(self, avg_rating, avg_quality):
        """Calculate quality score (0-100)."""
        rating_score = (avg_rating / 10) * 60  # Max 60 points
        quality_score = (avg_quality / 10) * 40  # Max 40 points

        return min(rating_score + quality_score, 100)

    def _calculate_attendance_score(self, first_day, last_day):
        """Calculate attendance score."""
        days_with_entries = frappe.db.count(
            "Daily Performance",
            filters={
                "employee": self.employee,
                "date": ["between", [first_day, last_day]],
                "docstatus": 1,
            },
        )

        total_working_days = date_diff(last_day, first_day) + 1

        if total_working_days <= 0:
            return 100

        score = (days_with_entries / total_working_days) * 100
        return min(score, 100)

    def _get_grade(self, score):
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

    def _get_performance_status(self, score):
        """Get performance status."""
        if score >= 80:
            return "On Track"
        elif score >= 60:
            return "Needs Attention"
        else:
            return "At Risk"

    def set_zero_scores(self):
        """Set all scores to zero when no data."""
        self.tasks_completed = 0
        self.pending_tasks = 0
        self.completed_percentage = 0
        self.average_rating = 0
        self.average_quality = 0
        self.attendance_score = 0
        self.productivity_score = 0
        self.quality_score = 0
        self.overall_score = 0
        self.final_grade = "Needs Improvement"
        self.performance_status = "At Risk"

    def on_submit(self):
        """On scorecard submit."""
        self.create_timeline_entry("Scorecard Generated")
        self.send_notification()

    def create_timeline_entry(self, action):
        """Create timeline entry."""
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Performance Scorecard",
                "reference_name": self.name,
                "content": action,
            }
        ).insert(ignore_permissions=True)

    def send_notification(self):
        """Send notification to employee."""
        from epms.epms.tasks import send_notification

        if self.employee:
            send_notification(
                user=self.employee,
                subject=f"Performance Scorecard Generated - {self.month}/{self.year}",
                message=f"Your performance scorecard has been generated. Overall Score: {self.overall_score:.2f} ({self.final_grade})",
                reference_doctype="Performance Scorecard",
                reference_name=self.name,
            )


def on_submit(doc, method):
    """On Performance Scorecard submit."""
    pass


def has_permission(doc, user):
    """Custom permission check for Performance Scorecard."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Founder has full access
    if "EPMS Founder" in user_roles:
        return True

    # Team leader can see their team's scorecards
    if "EPMS Team Leader" in user_roles:
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        if team:
            members = frappe.get_all(
                "Team Member Mapping",
                filters={"team": team, "status": "Active"},
                pluck="user",
            )
            return doc.employee in members

    # Team member can only see their own scorecard
    if "EPMS Team Member" in user_roles:
        return doc.employee == user

    return False
