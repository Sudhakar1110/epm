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
        print("   Creating Module Def...")
        create_module_def()
        frappe.db.commit()
        module_def = frappe.db.exists("Module Def", "Employee Performance")
        print(f"   Module Def after create: {module_def}")

    # Step 2: Check existing workspaces
    all_ws = frappe.db.sql(
        "SELECT name, module, is_hidden, public FROM `tabWorkspace`"
    )
    print(f"\n2. Total workspaces in DB: {len(all_ws)}")
    for w in all_ws:
        print(f"   - {w[0]} | module={w[1]} | hidden={w[2]} | public={w[3]}")

    # Step 3: Check our workspace
    ws_exists = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n3. Our workspace exists: {ws_exists}")

    if not ws_exists:
        print("\n4. Creating workspace with minimal fields...")
        try:
            ws = frappe.get_doc({
                "doctype": "Workspace",
                "module": "Employee Performance",
                "title": "Employee Performance Management",
                "label": "Employee Performance Management",
                "icon": "octicon octicon-goal",
                "indicator_color": "green",
                "category": "Modules",
                "is_hidden": 0,
                "public": 1,
                "links": [
                    {"type": "Link", "link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1},
                    {"type": "Link", "link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1},
                    {"type": "Link", "link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1},
                    {"type": "Link", "link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1},
                    {"type": "Link", "link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1},
                    {"type": "Separator", "link_type": "Separator"},
                    {"type": "Link", "link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Report", "is_query_report": 1, "onboard": 1},
                    {"type": "Link", "link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Report", "is_query_report": 1, "onboard": 1},
                ],
                "shortcuts": [
                    {"type": "DocType", "link_to": "Team", "label": "Teams"},
                    {"type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance"},
                    {"type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks"},
                    {"type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards"},
                ],
            })
            ws.insert(ignore_permissions=True)
            frappe.db.commit()
            print("   SUCCESS via frappe.get_doc!")
        except Exception as e:
            print(f"   get_doc FAILED: {str(e)}")
            frappe.log_error(f"EPMS get_doc failed: {str(e)}")

            # Fallback: SQL INSERT (without doctype column)
            print("\n5. Trying direct SQL INSERT...")
            try:
                frappe.db.sql(
                    """INSERT INTO `tabWorkspace`
                    (`name`, `module`, `label`, `title`, `icon`,
                     `indicator_color`, `category`, `is_hidden`, `public`,
                     `custom`, `modified_by`, `owner`, `for_user`,
                     `creation`, `modified`, `content`, `links`, `shortcuts`,
                     `charts`, `number_cards`, `custom_blocks`, `roles`,
                     `sequence_id`, `parent_page`, `hide_custom`, `quick_lists`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s)""",
                    (
                        "Employee Performance Management",
                        "Employee Performance",
                        "Employee Performance Management",
                        "Employee Performance Management",
                        "octicon octicon-goal",
                        "green",
                        "Modules",
                        0, 1, 0,
                        "Administrator", "Administrator", "",
                        "2024-01-01 00:00:00.000000",
                        "2024-01-01 00:00:00.000000",
                        "[]", "[]", "[]",
                        "[]", "[]", "[]", "[]",
                        1, "", 0, "[]",
                    ),
                )
                frappe.db.commit()
                print("   SUCCESS via SQL!")
            except Exception as e2:
                print(f"   SQL FAILED: {str(e2)}")
                frappe.log_error(f"EPMS SQL failed: {str(e2)}")

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
        frappe.logger().info("EPMS: Workspace already exists")
        return

    try:
        ws = frappe.get_doc({
            "doctype": "Workspace",
            "module": "Employee Performance",
            "title": "Employee Performance Management",
            "label": "Employee Performance Management",
            "icon": "octicon octicon-goal",
            "indicator_color": "green",
            "category": "Modules",
            "is_hidden": 0,
            "public": 1,
            "links": [
                {"type": "Link", "link_type": "DocType", "link_to": "Team", "label": "Teams", "onboard": 1},
                {"type": "Link", "link_type": "DocType", "link_to": "Team Member Mapping", "label": "Team Members", "onboard": 1},
                {"type": "Link", "link_type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance", "onboard": 1},
                {"type": "Link", "link_type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks", "onboard": 1},
                {"type": "Link", "link_type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards", "onboard": 1},
                {"type": "Separator", "link_type": "Separator"},
                {"type": "Link", "link_type": "Report", "link_to": "Daily Performance Report", "label": "Daily Report", "is_query_report": 1, "onboard": 1},
                {"type": "Link", "link_type": "Report", "link_to": "Monthly Performance Report", "label": "Monthly Report", "is_query_report": 1, "onboard": 1},
            ],
            "shortcuts": [
                {"type": "DocType", "link_to": "Team", "label": "Teams"},
                {"type": "DocType", "link_to": "Daily Performance", "label": "Daily Performance"},
                {"type": "DocType", "link_to": "Pending Task", "label": "Pending Tasks"},
                {"type": "DocType", "link_to": "Performance Scorecard", "label": "Scorecards"},
            ],
        })
        ws.insert(ignore_permissions=True)
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
