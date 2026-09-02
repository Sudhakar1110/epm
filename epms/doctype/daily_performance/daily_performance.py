import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, cint, flt, add_days


class DailyPerformance(Document):
    def validate(self):
        self.validate_date()
        self.validate_hours()
        self.validate_completion_percentage()
        self.validate_rating()
        self.validate_employee()
        self.set_team_leader()
        self.set_employee_name()
        self.calculate_computed_fields()

    def validate_date(self):
        """Validate date is not in the future."""
        if self.date and self.date > getdate(nowdate()):
            frappe.throw(_("Cannot submit performance for future dates"))

    def validate_hours(self):
        """Validate hours worked."""
        if self.actual_hours and self.actual_hours > 24:
            frappe.throw(_("Hours worked cannot exceed 24"))

        if self.expected_hours and self.expected_hours > 24:
            frappe.throw(_("Expected hours cannot exceed 24"))

        if self.actual_hours and self.actual_hours < 0:
            frappe.throw(_("Actual hours cannot be negative"))

    def validate_completion_percentage(self):
        """Validate completion percentage."""
        if self.completion_percentage is not None:
            if self.completion_percentage < 0 or self.completion_percentage > 100:
                frappe.throw(_("Completion percentage must be between 0 and 100"))

    def validate_rating(self):
        """Validate rating values."""
        if self.daily_rating is not None:
            if self.daily_rating < 1 or self.daily_rating > 10:
                frappe.throw(_("Daily rating must be between 1 and 10"))

        if self.quality_score is not None:
            if self.quality_score < 1 or self.quality_score > 10:
                frappe.throw(_("Quality score must be between 1 and 10"))

    def validate_employee(self):
        """Validate employee belongs to the team."""
        if self.employee and self.team:
            member = frappe.db.exists(
                "Team Member Mapping",
                {
                    "user": self.employee,
                    "team": self.team,
                    "status": "Active",
                },
            )
            if not member:
                frappe.throw(
                    _("Employee {0} is not a member of team {1}").format(
                        self.employee, self.team
                    )
                )

    def set_team_leader(self):
        """Set team leader from team."""
        if self.team and not self.team_leader:
            self.team_leader = frappe.db.get_value("Team", self.team, "team_leader")

    def set_employee_name(self):
        """Set employee name from user."""
        if self.employee and not self.employee_name:
            full_name = frappe.db.get_value("User", self.employee, "full_name")
            self.employee_name = full_name or self.employee

    def calculate_computed_fields(self):
        """Calculate computed fields."""
        # Auto-set completion based on status
        if self.task_status == "Completed":
            self.completion_percentage = 100
        elif self.task_status == "Pending":
            self.completion_percentage = 0

    def on_submit(self):
        """On document submit."""
        self.create_timeline_entry("Performance Submitted")
        self.send_notification()

    def on_cancel(self):
        """On document cancel."""
        self.create_timeline_entry("Performance Cancelled")

    def create_timeline_entry(self, action):
        """Create timeline entry."""
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Daily Performance",
                "reference_name": self.name,
                "content": action,
            }
        ).insert(ignore_permissions=True)

    def send_notification(self):
        """Send notification on submit."""
        from epms.epms.tasks import send_notification

        # Notify team leader
        if self.team_leader and self.team_leader != frappe.session.user:
            send_notification(
                user=self.team_leader,
                subject=f"Performance Entry Submitted: {self.performance_id}",
                message=f"Performance entry {self.performance_id} submitted by {self.employee_name}",
                reference_doctype="Daily Performance",
                reference_name=self.name,
            )

        # Notify founders
        founders = frappe.get_all(
            "Has Role",
            filters={"role": "EPMS Founder", "parenttype": "User"},
            pluck="parent",
        )

        for founder in founders:
            if founder != frappe.session.user:
                send_notification(
                    user=founder,
                    subject=f"Performance Entry: {self.performance_id}",
                    message=f"New performance entry submitted by {self.employee_name}",
                    reference_doctype="Daily Performance",
                    reference_name=self.name,
                )


def before_insert(doc, method):
    """Before Daily Performance insert."""
    doc.created_by = frappe.session.user


def validate(doc, method):
    """Validate Daily Performance."""
    pass


def on_submit(doc, method):
    """On Daily Performance submit."""
    pass


def on_cancel(doc, method):
    """On Daily Performance cancel."""
    pass


def after_insert(doc, method):
    """After Daily Performance insert."""
    doc.create_timeline_entry("Performance Created")


def has_permission(doc, user):
    """Custom permission check for Daily Performance."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Founder has full access
    if "EPMS Founder" in user_roles:
        return True

    # Team leader can see their team's performances
    if "EPMS Team Leader" in user_roles:
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        return doc.team == team

    # Team member can only see their own
    if "EPMS Team Member" in user_roles:
        return doc.employee == user

    return False
