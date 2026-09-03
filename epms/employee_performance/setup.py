import frappe
from frappe import _
import os
import json


def before_migrate():
    """Run before migration to ensure Module Def exists."""
    create_module_def()
    frappe.db.commit()


def after_install():
    """Run after app installation."""
    create_module_def()
    ensure_workspace_exists()
    create_roles()
    setup_role_permissions()
    frappe.db.commit()


def after_migrate():
    """Run after migration."""
    create_module_def()
    ensure_workspace_exists()
    frappe.db.commit()


def fix_workspace_now():
    """Run from bench to force-create the workspace with full content.

    bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now
    """
    print("\n=== EPMS Workspace Fix ===")

    # Delete existing empty workspace and recreate
    if frappe.db.exists("Workspace", "Employee Performance Management"):
        print("Deleting existing empty workspace...")
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", "Employee Performance Management")
        frappe.db.commit()

    ensure_workspace_exists()

    final = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"Workspace exists: {final}")
    if final:
        ws = frappe.get_doc("Workspace", "Employee Performance Management")
        content_preview = ws.content[:200] if ws.content else "EMPTY"
        print(f"Content preview: {content_preview}...")
        print(f"URL: /app/employee-performance-management")
    print("=== Done ===")


def _get_workspace_content():
    """Build the workspace content JSON with all links and shortcuts."""
    return json.dumps([
        {"type": "header", "data": {"text": "Employee Performance Management", "orientation": "left"}},
        {"type": "shortcut", "data": {"shortcut_name": "Team", "type": "DocType"}},
        {"type": "shortcut", "data": {"shortcut_name": "Team Member Mapping", "type": "DocType"}},
        {"type": "shortcut", "data": {"shortcut_name": "Daily Performance", "type": "DocType"}},
        {"type": "shortcut", "data": {"shortcut_name": "Pending Task", "type": "DocType"}},
        {"type": "shortcut", "data": {"shortcut_name": "Performance Scorecard", "type": "DocType"}},
        {"type": "header", "data": {"text": "Quick Links", "orientation": "left"}},
        {"type": "link", "data": {"link_type": "DocType", "link_to": "Team", "label": "Teams"}},
        {"type": "link", "data": {"link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members"}},
        {"type": "link", "data": {"link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance"}},
        {"type": "link", "data": {"link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks"}},
        {"type": "link", "data": {"link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards"}},
        {"type": "header", "data": {"text": "Reports", "orientation": "left"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Performance Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Performance Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Employee Wise Report", "label": "Employee Wise Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Team Wise Report", "label": "Team Wise Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Pending Task Report", "label": "Pending Task Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Top Performers", "label": "Top Performers"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Low Performers", "label": "Low Performers"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Monthly KPI Report", "label": "Monthly KPI Report"}},
        {"type": "link", "data": {"link_type": "Report", "link_to": "Leaderboard Report", "label": "Leaderboard Report"}},
    ])


def _get_shortcuts():
    """Build shortcuts JSON."""
    return json.dumps([
        {"type": "DocType", "link_to": "Team", "label": "Teams"},
        {"type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members"},
        {"type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance"},
        {"type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks"},
        {"type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards"},
    ])


def _build_workspace_row():
    """Build workspace data dict using only columns that exist in Frappe v15."""
    columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_dict=True)
    col_names = [c.Field for c in columns]

    data = {
        "name": "Employee Performance Management",
        "label": "Employee Performance Management",
        "title": "Employee Performance Management",
        "module": "Employee Performance",
        "icon": "octicon octicon-goal",
        "indicator_color": "green",
        "is_hidden": 0,
        "public": 1,
        "for_user": "",
        "modified_by": "Administrator",
        "owner": "Administrator",
        "creation": "2024-01-01 00:00:00.000000",
        "modified": "2024-01-01 00:00:00.000000",
        "content": _get_workspace_content(),
        "sequence_id": 1,
        "parent_page": "",
        "hide_custom": 0,
        "restrict_to_domain": "",
        "docstatus": 0,
        "idx": 0,
    }

    # Only include columns that exist in the table
    return {k: v for k, v in data.items() if k in col_names}


def create_module_def():
    """Ensure the Employee Performance Module Def exists."""
    if not frappe.db.exists("Module Def", "Employee Performance"):
        try:
            frappe.get_doc({
                "doctype": "Module Def",
                "module_name": "Employee Performance",
                "app_name": "epms",
                "label": "Employee Performance",
                "color": "#28a745",
                "icon": "octicon octicon-goal",
                "description": "Employee Performance Management System",
                "type": "Module",
                "custom": 0,
            }).insert(ignore_permissions=True)
            frappe.logger().info("EPMS: Created Module Def for Employee Performance")
        except Exception as e:
            frappe.log_error(f"EPMS: Failed to create Module Def: {str(e)}")


def ensure_workspace_exists():
    """Create workspace with full content if it doesn't exist yet."""
    if frappe.db.exists("Workspace", "Employee Performance Management"):
        return

    data = _build_workspace_row()
    cols = ", ".join([f"`{k}`" for k in data.keys()])
    placeholders = ", ".join(["%s"] * len(data))
    vals = list(data.values())

    try:
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace` ({cols}) VALUES ({placeholders})",
            vals,
        )
        frappe.db.commit()
        frappe.logger().info("EPMS: Created workspace with full content")
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to create workspace: {str(e)}")


def create_roles():
    """Create EPMS roles."""
    roles = [
        {"role_name": "EPMS Founder", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Leader", "desk_access": 1, "is_custom": 1},
        {"role_name": "EPMS Team Member", "desk_access": 1, "is_custom": 1},
    ]
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            frappe.get_doc({"doctype": "Role", **role_data}).insert(ignore_permissions=True)


def setup_role_permissions():
    """Setup role permissions for EPMS doctypes."""
    permissions = {
        "Team": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1},
            "EPMS Team Leader": {"read": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Team Member Mapping": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Daily Performance": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "cancel": 1, "submit": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Pending Task": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1, "write": 1, "create": 1, "submit": 1},
            "EPMS Team Member": {"read": 1},
        },
        "Performance Scorecard": {
            "EPMS Founder": {"read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
            "EPMS Team Leader": {"read": 1},
            "EPMS Team Member": {"read": 1},
        },
    }
    for doctype, roles in permissions.items():
        for role, perms in roles.items():
            if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
                try:
                    frappe.get_doc({
                        "doctype": "Custom DocPerm",
                        "parent": doctype,
                        "parenttype": "DocType",
                        "parentfield": "permissions",
                        "role": role,
                        **perms,
                    }).insert(ignore_permissions=True)
                except Exception:
                    pass
