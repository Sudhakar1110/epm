import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EPMSSettings(Document):
    def validate(self):
        self.validate_thresholds()

    def validate_thresholds(self):
        """Validate threshold values."""
        excellent = flt(self.excellent_threshold or 90)
        very_good = flt(self.very_good_threshold or 80)
        good = flt(self.good_threshold or 70)
        average = flt(self.average_threshold or 60)
        low = flt(self.low_performance_threshold or 60)

        if excellent <= very_good:
            frappe.throw(_("Excellent threshold must be greater than Very Good threshold"))
        
        if very_good <= good:
            frappe.throw(_("Very Good threshold must be greater than Good threshold"))
        
        if good <= average:
            frappe.throw(_("Good threshold must be greater than Average threshold"))
        
        if average <= low:
            frappe.throw(_("Average threshold must be greater than Low Performance threshold"))


def get_settings():
    """Get EPMS settings."""
    settings = frappe.get_single("EPMS Settings")
    return settings


def has_permission(doc, user):
    """Only EPMS Founder can access EPMS Settings."""
    if not user:
        user = frappe.session.user
    user_roles = frappe.get_roles(user)
    return "EPMS Founder" in user_roles
