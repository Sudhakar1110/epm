import frappe
from frappe import _


def get_notification_config():
    """Return notification config for EPMS."""
    return {
        "for_module": ["Employee Performance", "HR"],
        "sort_by": "modified",
        "sort_order": "desc",
        "filters": [
            {
                "name": "Daily Performance",
                "icon": "octicon octicon-checklist",
                "color": "#5e64ff",
                "link": "/app/daily-performance",
            },
            {
                "name": "Pending Task",
                "icon": "octicon octicon-alert",
                "color": "#ff5858",
                "link": "/app/pending-task",
            },
            {
                "name": "Performance Scorecard",
                "icon": "octicon octicon-graph",
                "color": "#28a745",
                "link": "/app/performance-scorecard",
            },
        ],
    }
