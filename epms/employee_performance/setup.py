import frappe
from frappe import _


def after_install():
    """Run after app installation."""
    create_module_def()
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def after_migrate():
    """Run after migration."""
    create_module_def()
    sync_workspace()
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def create_module_def():
    """Ensure the Employee Performance Module Def exists."""
    if not frappe.db.exists("Module Def", "Employee Performance"):
        try:
            frappe.get_doc(
                {
                    "doctype": "Module Def",
                    "module_name": "Employee Performance",
                    "app_name": "epms",
                    "label": "Employee Performance",
                    "color": "#28a745",
                    "icon": "octicon octicon-goal",
                    "description": "Employee Performance Management System",
                    "type": "Module",
                    "custom": 0,
                }
            ).insert(ignore_permissions=True)
            frappe.logger().info("EPMS: Created Module Def for Employee Performance")
        except Exception as e:
            frappe.log_error(f"EPMS: Failed to create Module Def: {str(e)}")


def sync_workspace():
    """Ensure the workspace is created from JSON if it doesn't exist."""
    import json
    import os

    workspace_name = "Employee Performance Management"
    if frappe.db.exists("Workspace", workspace_name):
        return

    json_path = os.path.join(
        os.path.dirname(__file__),
        "workspace",
        "employee_performance_management.json",
    )
    if not os.path.exists(json_path):
        frappe.log_error("EPMS: Workspace JSON not found at " + json_path)
        return

    try:
        with open(json_path, "r") as f:
            ws_data = json.load(f)

        ws_data["doctype"] = "Workspace"
        if "name" in ws_data:
            del ws_data["name"]

        ws = frappe.get_doc(ws_data)
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("EPMS: Created workspace: " + workspace_name)
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to create workspace: {str(e)}")


def create_roles():
    """Create EPMS roles."""
    roles = [
        {
            "role_name": "EPMS Founder",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "EPMS Team Leader",
            "desk_access": 1,
            "is_custom": 1,
        },
        {
            "role_name": "EPMS Team Member",
            "desk_access": 1,
            "is_custom": 1,
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
