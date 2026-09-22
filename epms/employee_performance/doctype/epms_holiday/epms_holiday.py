import frappe
from frappe import _
from frappe.model.document import Document


class EPMSHoliday(Document):
    def validate(self):
        self.validate_duplicate_date()

    def validate_duplicate_date(self):
        existing = frappe.db.exists(
            "EPMS Holiday",
            {
                "holiday_date": self.holiday_date,
                "name": ["!=", self.name],
            },
        )
        if existing:
            frappe.throw(
                _("A holiday already exists for {0}").format(self.holiday_date)
            )


def has_permission(doc, user=None):
    """Custom permission check for EPMS Holiday.

    Founder manages holidays; everyone else with a role can read
    (so the calendar can show them)."""
    if not user:
        user = frappe.session.user

    user_roles = frappe.get_roles(user)

    if "EPMS Founder" in user_roles:
        return True

    if any(r in user_roles for r in ["EPMS Team Leader", "EPMS Team Member"]):
        if isinstance(doc, str):
            return True
        if isinstance(doc, dict):
            return True
        return hasattr(doc, "holiday_date")

    return False