import frappe
from frappe import _


def get_notification_config():
    """Return notification config for EPMS."""
    return {
        "for_doctype": {
            "Daily Performance": {
                "docstatus": 1,
            },
            "Pending Task": {
                "current_status": ["in", ["Pending", "In Progress"]],
                "docstatus": 1,
            },
            "Performance Scorecard": {
                "docstatus": 1,
            },
        },
    }
