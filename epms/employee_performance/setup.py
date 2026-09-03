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

    # Step 2: Check for ANY workspace with similar names
    all_ws = frappe.db.sql(
        "SELECT name, module, is_hidden, public FROM `tabWorkspace`"
    )
    print(f"\n2. Total workspaces in DB: {len(all_ws)}")
    for w in all_ws:
        print(f"   - {w[0]} | module={w[1]} | hidden={w[2]} | public={w[3]}")

    # Step 3: Check if our workspace exists
    ws_exists = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n3. Our workspace exists: {ws_exists}")

    if not ws_exists:
        # Step 4: Check if JSON file exists
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "workspace",
            "employee_performance_management.json",
        )
        print(f"4. JSON path: {json_path}")
        print(f"   JSON file exists: {os.path.exists(json_path)}")

        if os.path.exists(json_path):
            # Step 5: Try get_doc
            print("\n5. Trying frappe.get_doc insert...")
            try:
                with open(json_path, "r") as f:
                    ws_data = json.load(f)
                ws_data["doctype"] = "Workspace"
                ws_data["module"] = "Employee Performance"
                ws_data["name"] = "Employee Performance Management"
                ws = frappe.get_doc(ws_data)
                ws.insert(ignore_permissions=True)
                frappe.db.commit()
                print("   SUCCESS via get_doc!")
            except Exception as e:
                print(f"   FAILED: {str(e)}")
                frappe.log_error(f"EPMS get_doc failed: {str(e)}")

                # Step 6: Try direct SQL
                print("\n6. Trying direct SQL INSERT...")
                try:
                    content = json.dumps(ws_data.get("content", "[]"))
                    links_json = json.dumps(ws_data.get("links", []))
                    shortcuts_json = json.dumps(ws_data.get("shortcuts", []))
                    frappe.db.sql(
                        """INSERT INTO `tabWorkspace`
                        (`name`, `module`, `label`, `title`, `doctype`,
                         `is_hidden`, `public`, `custom`, `modified_by`, `owner`,
                         `creation`, `modified`, `content`, `links`, `shortcuts`)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (
                            "Employee Performance Management",
                            "Employee Performance",
                            "Employee Performance Management",
                            "Employee Performance Management",
                            "Workspace",
                            0, 1, 0,
                            "Administrator", "Administrator",
                            "2024-01-01 00:00:00.000000",
                            "2024-01-01 00:00:00.000000",
                            content, links_json, shortcuts_json,
                        ),
                    )
                    frappe.db.commit()
                    print("   SUCCESS via SQL!")
                except Exception as e2:
                    print(f"   FAILED: {str(e2)}")
                    frappe.log_error(f"EPMS SQL failed: {str(e2)}")

    # Final check
    final_check = frappe.db.exists("Workspace", "Employee Performance Management")
    print(f"\n7. FINAL: Workspace exists = {final_check}")
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
    """Create workspace from JSON if it doesn't exist yet."""
    workspace_name = "Employee Performance Management"

    if frappe.db.exists("Workspace", workspace_name):
        frappe.logger().info("EPMS: Workspace already exists")
        return

    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
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
        ws_data["module"] = "Employee Performance"
        ws_data["name"] = workspace_name

        ws = frappe.get_doc(ws_data)
        ws.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("EPMS: Created workspace: " + workspace_name)
    except Exception as e:
        frappe.log_error(f"EPMS: Failed to create workspace via get_doc: {str(e)}")
        # Fallback: create via direct SQL
        _create_workspace_sql(workspace_name)


def _create_workspace_sql(workspace_name):
    """Fallback: create workspace via direct SQL INSERT."""
    json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "workspace",
        "employee_performance_management.json",
    )
    try:
        with open(json_path, "r") as f:
            ws_data = json.load(f)

        content = json.dumps(ws_data.get("content", "[]"))
        links_json = json.dumps(ws_data.get("links", []))
        shortcuts_json = json.dumps(ws_data.get("shortcuts", []))
        charts_json = json.dumps(ws_data.get("charts", []))
        number_cards_json = json.dumps(ws_data.get("number_cards", []))
        custom_blocks_json = json.dumps(ws_data.get("custom_blocks", []))
        roles_json = json.dumps(ws_data.get("roles", []))

        frappe.db.sql(
            """INSERT INTO `tabWorkspace`
            (`name`, `module`, `label`, `title`, `doctype`, `icon`,
             `indicator_color`, `category`, `is_hidden`, `public`,
             `for_user`, `custom`, `modified_by`, `owner`,
             `creation`, `modified`, `content`, `links`, `shortcuts`,
             `charts`, `number_cards`, `custom_blocks`, `roles`,
             `sequence_id`, `parent_page`, `hide_custom`, `quick_lists`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s)""",
            (
                workspace_name,
                "Employee Performance",
                ws_data.get("label", workspace_name),
                ws_data.get("title", workspace_name),
                "Workspace",
                ws_data.get("icon", "octicon octicon-file-directory"),
                ws_data.get("indicator_color", "green"),
                ws_data.get("category", "Modules"),
                0,
                1,
                "",
                0,
                "Administrator",
                "Administrator",
                "2024-01-01 00:00:00.000000",
                "2024-01-01 00:00:00.000000",
                content,
                links_json,
                shortcuts_json,
                charts_json,
                number_cards_json,
                custom_blocks_json,
                roles_json,
                1,
                "",
                0,
                "[]",
            ),
        )
        frappe.db.commit()
        frappe.logger().info(
            "EPMS: Created workspace via SQL: " + workspace_name
        )
    except Exception as e:
        frappe.log_error(f"EPMS: SQL workspace creation failed: {str(e)}")


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
