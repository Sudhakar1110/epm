import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EmployeeKPI(Document):
    def validate(self):
        self.validate_values()
        self.calculate_achievement()
        self.set_employee_name()

    def validate_values(self):
        """Validate KPI values."""
        if self.target_value and self.target_value < 0:
            frappe.throw(_("Target value cannot be negative"))

        if self.actual_value and self.actual_value < 0:
            frappe.throw(_("Actual value cannot be negative"))

        if self.weight and (self.weight < 0 or self.weight > 100):
            frappe.throw(_("Weight must be between 0 and 100"))

    def calculate_achievement(self):
        """Calculate achieved percentage."""
        if self.target_value and self.target_value > 0:
            self.achieved_percentage = (self.actual_value / self.target_value) * 100
        else:
            self.achieved_percentage = 0

        # Update status based on achievement
        if self.achieved_percentage >= 100:
            self.status = "Exceeded"
        elif self.achieved_percentage >= 80:
            self.status = "Completed"
        elif self.achieved_percentage > 0:
            self.status = "In Progress"
        else:
            self.status = "Pending"

    def set_employee_name(self):
        """Set employee name."""
        if self.employee and not self.employee_name:
            full_name = frappe.db.get_value("User", self.employee, "full_name")
            self.employee_name = full_name or self.employee


def has_permission(doc, user):
    """Custom permission check."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "EPMS Founder" in user_roles:
        return True

    if "EPMS Team Leader" in user_roles:
        team = frappe.db.get_value("Team", {"team_leader": user}, "name")
        return doc.team == team

    if "EPMS Team Member" in user_roles:
        return doc.employee == user

    return False
