from frappe import _

base_hooks_fixtures = [
    {
        "dt": "Role",
        "filters": [
            ["name", "in", ["EPMS Founder", "EPMS Team Leader", "EPMS Team Member"]]
        ],
    },
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Notification",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Print Format",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Report",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Dashboard Chart",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
    {
        "dt": "Workspace",
        "filters": [
            ["module", "=", "EPMS"],
        ],
    },
]
