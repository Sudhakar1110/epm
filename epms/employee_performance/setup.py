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
    """Run from bench to diagnose and force-create the workspace.

    bench --site epms.ogascale.com execute epms.employee_performance.setup.fix_workspace_now
    """
    print("\n=== EPMS Workspace Diagnostics ===")

    # Step 1: Check Module Def
    module_def = frappe.db.exists("Module Def", "Employee Performance")
    print(f"1. Module Def exists: {module_def}")
    if not module_def:
        create_module_def()
        frappe.db.commit()

    # Step 2: Check existing workspaces
    all_ws = frappe.db.sql(
        "SELECT name, module FROM `tabWorkspace`", as_dict=True
    )
    print(f"\n2. Total workspaces in DB: {len(all_ws)}")

    # Step 3: Show actual table columns
    columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_dict=True)
    col_names = [c.Field for c in columns]
    print(f"\n3. Actual tabWorkspace columns: {col_names}")

    # Step 4: Check our workspace
    ws_exists = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n4. Our workspace exists: {ws_exists}")

    if not ws_exists:
        # Build INSERT using only columns that actually exist
        insert_data = {
            "name": "Employee Performance Management",
            "module": "Employee Performance",
            "title": "Employee Performance Management",
        }

        # Add optional fields only if column exists
        optional = {
            "label": "Employee Performance Management",
            "icon": "octicon octicon-goal",
            "indicator_color": "green",
            "is_hidden": 0,
            "public": 1,
            "for_user": "",
            "custom": 0,
            "modified_by": "Administrator",
            "owner": "Administrator",
            "creation": "2024-01-01 00:00:00.000000",
            "modified": "2024-01-01 00:00:00.000000",
            "content": "[]",
            "links": "[]",
            "shortcuts": "[]",
            "charts": "[]",
            "number_cards": "[]",
            "custom_blocks": "[]",
            "roles": "[]",
            "sequence_id": 1,
            "parent_page": "",
            "hide_custom": 0,
            "quick_lists": "[]",
            "category": "Modules",
            "extends_another_page": 0,
            "restrict_to_domain": "",
            "pin_to_top": 0,
            "pin_to_bottom": 0,
        }

        for key, val in optional.items():
            if key in col_names:
                insert_data[key] = val

        cols = ", ".join([f"`{k}`" for k in insert_data.keys()])
        placeholders = ", ".join(["%s"] * len(insert_data))
        vals = list(insert_data.values())

        print(f"\n5. Inserting workspace with columns: {list(insert_data.keys())}")
        try:
            frappe.db.sql(
                f"INSERT INTO `tabWorkspace` ({cols}) VALUES ({placeholders})",
                vals,
            )
            frappe.db.commit()
            print("   SUCCESS via SQL!")
        except Exception as e:
            print(f"   SQL FAILED: {str(e)}")
            frappe.log_error(f"EPMS SQL failed: {str(e)}")

    # Final check
    final_check = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n6. FINAL: Workspace exists = {final_check}")
    if final_check:
        print("   Workspace URL: /app/employee-performance-management")
    print("=== Done ===")


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


def ensure_workspace_exists():
    """Create workspace if it doesn't exist yet."""
    workspace_name = "Employee Performance Management"

    if frappe.db.exists("Workspace", workspace_name):
        return

    # Get actual table columns
    columns = frappe.db.sql("SHOW COLUMNS FROM `tabWorkspace`", as_dict=True)
    col_names = [c.Field for c in columns]

    # Build data using only columns that exist
    insert_data = {
        "name": workspace_name,
        "module": "Employee Performance",
        "title": workspace_name,
    }

    optional = {
        "label": workspace_name,
        "icon": "octicon octicon-goal",
        "indicator_color": "green",
        "is_hidden": 0,
        "public": 1,
        "for_user": "",
        "custom": 0,
        "modified_by": "Administrator",
        "owner": "Administrator",
        "creation": "2024-01-01 00:00:00.000000",
        "modified": "2024-01-01 00:00:00.000000",
        "content": "[]",
        "links": "[]",
        "shortcuts": "[]",
        "charts": "[]",
        "number_cards": "[]",
        "custom_blocks": "[]",
        "roles": "[]",
        "sequence_id": 1,
        "parent_page": "",
        "hide_custom": 0,
        "quick_lists": "[]",
        "category": "Modules",
        "extends_another_page": 0,
        "restrict_to_domain": "",
        "pin_to_top": 0,
        "pin_to_bottom": 0,
    }

    for key, val in optional.items():
        if key in col_names:
            insert_data[key] = val

    cols = ", ".join([f"`{k}`" for k in insert_data.keys()])
    placeholders = ", ".join(["%s"] * len(insert_data))
    vals = list(insert_data.values())

    try:
        frappe.db.sql(
            f"INSERT INTO `tabWorkspace` ({cols}) VALUES ({placeholders})",
            vals,
        )
        frappe.db.commit()
        frappe.logger().info("EPMS: Created workspace: " + workspace_name)
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
            role = frappe.get_doc({"doctype": "Role", **role_data})
            role.insert(ignore_permissions=True)


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
            existing = frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role})
            if not existing:
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
