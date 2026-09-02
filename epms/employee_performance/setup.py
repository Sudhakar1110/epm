import frappe
from frappe import _


def after_install():
    """Run after app installation."""
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def after_migrate():
    """Run after migration."""
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def create_roles():
    """Create EPMS roles."""
    roles = [
        {
            "role_name": "EPMS Founder",
            "desk_access": 1,
            "is_custom": 1,
            "module_name": "Employee Performance",
            "description": "Full access to Employee Performance Management System",
        },
        {
            "role_name": "EPMS Team Leader",
            "desk_access": 1,
            "is_custom": 1,
            "module_name": "Employee Performance",
            "description": "Manage team members and daily performance",
        },
        {
            "role_name": "EPMS Team Member",
            "desk_access": 1,
            "is_custom": 1,
            "module_name": "Employee Performance",
            "description": "View own performance and scorecard",
        },
    ]

    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.get_doc({"doctype": "Role", **role_data})
            role.insert(ignore_permissions=True)


def setup_role_permissions():
    """Setup role permissions for EPMS doctypes."""
    permissions = {
        "Team": {
            "EPMS Founder": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
            },
            "EPMS Team Leader": {
                "read": 1,
            },
            "EPMS Team Member": {
                "read": 1,
            },
        },
        "Team Member Mapping": {
            "EPMS Founder": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
            },
            "EPMS Team Leader": {
                "read": 1, "write": 1, "create": 1,
            },
            "EPMS Team Member": {
                "read": 1,
            },
        },
        "Daily Performance": {
            "EPMS Founder": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 1, "cancel": 1, "amend": 1,
            },
            "EPMS Team Leader": {
                "read": 1, "write": 1, "create": 1, "cancel": 1,
                "submit": 1,
            },
            "EPMS Team Member": {
                "read": 1,
            },
        },
        "Pending Task": {
            "EPMS Founder": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 1, "cancel": 1, "amend": 1,
            },
            "EPMS Team Leader": {
                "read": 1, "write": 1, "create": 1, "submit": 1,
            },
            "EPMS Team Member": {
                "read": 1,
            },
        },
        "Performance Scorecard": {
            "EPMS Founder": {
                "read": 1, "write": 1, "create": 1, "delete": 1,
                "submit": 1, "cancel": 1, "amend": 1,
            },
            "EPMS Team Leader": {
                "read": 1,
            },
            "EPMS Team Member": {
                "read": 1,
            },
        },
    }

    for doctype, roles in permissions.items():
        for role, perms in roles.items():
            existing = frappe.db.exists(
                "Custom DocPerm",
                {"parent": doctype, "role": role},
            )
            if not existing:
                try:
                    frappe.get_doc(
                        {
                            "doctype": "Custom DocPerm",
                            "parent": doctype,
                            "parenttype": "DocType",
                            "parentfield": "permissions",
                            "role": role,
                            **perms,
                        }
                    ).insert(ignore_permissions=True)
                except Exception:
                    pass
