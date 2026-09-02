import frappe
from frappe import _


class EPMASettings(Document):
    def validate(self):
        self.validate_thresholds()

    def validate_thresholds(self):
        """Validate threshold values."""
        if self.excellent_threshold <= self.very_good_threshold:
            frappe.throw(_("Excellent threshold must be greater than Very Good threshold"))
        
        if self.very_good_threshold <= self.good_threshold:
            frappe.throw(_("Very Good threshold must be greater than Good threshold"))
        
        if self.good_threshold <= self.average_threshold:
            frappe.throw(_("Good threshold must be greater than Average threshold"))
        
        if self.average_threshold <= self.low_performance_threshold:
            frappe.throw(_("Average threshold must be greater than Low Performance threshold"))


def get_settings():
    """Get EPMS settings."""
    settings = frappe.get_single("EPMS Settings")
    return settings
