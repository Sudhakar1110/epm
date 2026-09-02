import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, cint, flt


class PendingTask(Document):
    def validate(self):
        self.validate_dates()
        self.validate_employee()
        self.set_employee_name()

    def validate_dates(self):
        """Validate dates."""
        if self.expected_completion and self.expected_completion < getdate(nowdate()):
            if self.current_status not in ["Completed"]:
                frappe.msgprint(
                    _("Warning: Task is past due date"),
                    alert=True,
                )

        if self.completion_date and self.completion_date > getdate(nowdate()):
            frappe.throw(_("Completion date cannot be in the future"))

    def validate_employee(self):
        """Validate employee exists."""
        if self.employee:
            user = frappe.db.get_value("User", self.employee, "name")
            if not user:
                frappe.throw(_("Invalid employee"))

    def set_employee_name(self):
        """Set employee name."""
        if self.employee and not self.employee_name:
            full_name = frappe.db.get_value("User", self.employee, "full_name")
            self.employee_name = full_name or self.employee

    def on_submit(self):
        """On document submit."""
        self.create_timeline_entry("Task Created")
        self.send_notification()

    def on_cancel(self):
        """On document cancel."""
        self.create_timeline_entry("Task Cancelled")

    def create_timeline_entry(self, action):
        """Create timeline entry."""
        frappe.get_doc(
            {
                "doctype": "Comment",
                "comment_type": "Info",
                "reference_doctype": "Pending Task",
                "reference_name": self.name,
                "content": action,
            }
        ).insert(ignore_permissions=True)

    def send_notification(self):
        """Send notification."""
        from epms.epms.tasks import send_notification

        # Notify employee
        if self.employee:
            send_notification(
                user=self.employee,
                subject=f"New Task Assigned: {self.task}",
                message=f"You have been assigned a new task: {self.task}. Priority: {self.priority}",
                reference_doctype="Pending Task",
                reference_name=self.name,
            )


def on_submit(doc, method):
    """On Pending Task submit."""
    pass


def on_cancel(doc, method):
    """On Pending Task cancel."""
    pass


def has_permission(doc, user):
    """Custom permission check for Pending Task."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    # Founder has full access
    if "EPMS Founder" in user_roles:
        return True

    # Team leader can see their team's tasks
    if "EPMS Team Leader" in user_roles:
        # Get team members
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        if team:
            members = frappe.get_all(
                "Team Member Mapping",
                filters={"team": team, "status": "Active"},
                pluck="user",
            )
            return doc.employee in members

    # Team member can only see their own tasks
    if "EPMS Team Member" in user_roles:
        return doc.employee == user

    return False
